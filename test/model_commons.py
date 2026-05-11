from langchain_google_genai import ChatGoogleGenerativeAI
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, TypedDict, Sequence

import chromadb
import numpy as np
import pandas as pd
import torch
from langchain.agents.middleware import ToolCallLimitMiddleware, AgentMiddleware
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.types import Command
from PIL import Image
from pydantic import SecretStr
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor

# --------------------------------
# KB
# --------------------------------

CSV_PATH = Path(__file__).with_name("augmented_clean_youtube_watch_log.csv")
REPO_DIR = Path(__file__).resolve().parent.parent
THUMBNAIL_PATH = REPO_DIR / "knowledge" / "thumbnails"

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

client = chromadb.PersistentClient(path=str(REPO_DIR / "chroma_db"))
collection_text = client.get_or_create_collection(name="youtube_videos_test_text")
collection_hybrid = client.get_or_create_collection(name="youtube_videos_test_hybrid")

df = pd.read_csv(CSV_PATH)


def embed_text(text: str) -> np.ndarray:
    """Embed a text using CLIP"""
    inputs = proc(
        text=[text], return_tensors="pt", truncation=True, padding=True
    )  # WARNING! Truncation may lead to loss of information for long texts
    with torch.no_grad():
        emb = model.get_text_features(**inputs)
    emb = emb / emb.norm(dim=-1, keepdim=True)  # Normalize
    return emb.to("cpu").numpy().squeeze()


def embed_image(image: Image.Image) -> np.ndarray:
    """Embed an image using CLIP"""
    inputs = proc(images=image, return_tensors="pt")
    with torch.no_grad():
        emb = model.get_image_features(**inputs)
    emb = emb / emb.norm(dim=-1, keepdim=True)  # Normalize
    return emb.to("cpu").numpy().squeeze()


# Check and add any new videos need to the KB
for collection in [collection_text, collection_hybrid]:
    ids_to_add = set(df["video_id"]) - set(collection.get(ids=None)["ids"])
    print(f"Found {len(ids_to_add)} new videos to add to collection {collection.name}.")

    for video_id in tqdm(ids_to_add, desc="Building KB"):
        row = df[df["video_id"] == video_id].iloc[0]
        user_id = row["user_id"]
        title = row["video_title"]
        thumbnail_path = f"{THUMBNAIL_PATH}/{video_id}.jpg"

        if collection.name == "youtube_videos_test_text":
            collection.add(
                ids=[video_id],
                embeddings=embed_text(title).tolist(),
                metadatas=[
                    {"user_id": int(user_id)}
                ],  # Metadata (user_id for filtering during retrieval)
            )
        elif collection.name == "youtube_videos_test_hybrid":
            fused_emb = 0.7 * embed_text(title) + 0.3 * embed_image(
                Image.open(thumbnail_path)
            )  # Simple weighted fusion
            fused_emb = fused_emb / np.linalg.norm(
                fused_emb
            )  # Normalize the fused embedding
            collection.add(
                ids=[video_id],
                embeddings=fused_emb.tolist(),
                metadatas=[
                    {"user_id": int(user_id)}
                ],  # Metadata (user_id for filtering during retrieval)
            )


# --------------------------------
# LLM
# --------------------------------

with open(REPO_DIR / "llm-api-key.txt") as f:
    # llm = ChatGroq(
    #     model="llama-3.3-70b-versatile",
    #     api_key=SecretStr(f.readline().strip()),
    #     temperature=0,
    # )
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        api_key=SecretStr(f.readline().strip()),
        convert_system_message_to_human=True,
    )

# --------------------------------
# Task-specific types
# --------------------------------


@dataclass
class BiasProfile:
    emotional_tone: Literal["low", "medium", "high"]
    sensationalism: Literal["low", "medium", "high"]
    topical_narrowing: Literal["low", "medium", "high"]
    echo_chamber_effect: Literal["low", "medium", "high"]
    dominant_topics: list[str]
    evidence_titles: list[str]
    overall_profile: str = field(
        metadata={
            "description": "Some comments from the model explaining why the scores were assigned."
        }
    )
    confidence: float = field(
        default=0.0,
        metadata={
            "description": "A confidence score (0-1) indicating how confident the model is in its bias assessment."
        },
    )

    def __repr__(self):
        return str(asdict(self))


# --------------------------------
# Agent state and context
# --------------------------------


@dataclass
class AgentContext:  # context (static configuration)
    user_id: int


MIDDLEWARE: Sequence[AgentMiddleware[Any, Any, Any]] = [
    ToolCallLimitMiddleware(run_limit=1)  # Only one tool call per turn
]  

CHECKPOINTER = InMemorySaver(  # chat history
    serde=JsonPlusSerializer(
        allowed_msgpack_modules=[
            ("__main__", "WatchItem"),
            ("__main__", "BiasProfile"),
        ]
    )
)
