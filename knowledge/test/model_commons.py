import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, Sequence, TypedDict
import chromadb
import numpy as np
import pandas as pd
import torch
from langchain.agents import AgentState as BaseAgentState
from langchain.agents import create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.types import Command
from PIL import Image
from pydantic import SecretStr, BaseModel
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from transformers import CLIPModel, CLIPProcessor

# --------------------------------
# KB
# --------------------------------

REPO_DIR = Path(__file__).resolve().parent.parent.parent
THUMBNAIL_PATH = REPO_DIR / "knowledge" / "thumbnails"
CSV_PATH = REPO_DIR / "knowledge" / "augmented_youtube_watch_log.csv"

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
# Domain-specific types
# --------------------------------

class WatchItem(BaseModel):
    video_id: str
    video_title: str
    timestamp: str  # ISO format

    @property
    def thumbnail_url(self) -> str:
        return f"./knowledge/thumbnails/{self.video_id}.jpg"

    @classmethod
    def from_row(cls, row) -> "WatchItem":
        return cls(
            video_id=row["video_id"],
            video_title=row["video_title"],
            timestamp=row["watch_date"],
        )

    def __repr__(self): # json
        d = self.model_dump()
        d["thumbnail_url"] = self.thumbnail_url
        return json.dumps(d, ensure_ascii=False)

class AgentState(BaseAgentState):   # tool-managed state (short-term memory)
    watch_history: list[WatchItem]  # @dataclass


# --------------------------------
# LLM
# --------------------------------

with open(REPO_DIR / "llm-api-key.txt") as f:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=SecretStr(f.readline().strip()),
        temperature=0,
    )

# --------------------------------
# Task-specific types
# --------------------------------


class BiasProfile(BaseModel):
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
        return json.dumps(self.model_dump(), ensure_ascii=False)


# --------------------------------
# Agent state and context
# --------------------------------


@dataclass
class AgentContext:  # context (static configuration)
    user_id: int

CHECKPOINTER = InMemorySaver(  # chat history
    serde=JsonPlusSerializer(
        allowed_msgpack_modules=[
            ("model_commons", "WatchItem"),
            ("model_commons", "BiasProfile"),
        ]
    )
)


# --------------------------------
# Agent tools
# --------------------------------

@tool
def find_similar_videos_text(
    title: str, limit: int, runtime: ToolRuntime[AgentContext, AgentState]
) -> list[WatchItem]:
    """Invokes the VectorDB to find similar videos by title.
    Args:
        title (str): A title to find similar videos for.
        limit (int): The number of similar videos to return. Defaults to 5.
    Returns:
        list[WatchItem]: A list of similar videos
    """

    # Query the vector database for similar videos
    similar_ids = collection_text.query(                    # <-- uses text-only collection
        query_embeddings=embed_text(title),
        n_results=limit or 5,
        where={"user_id": runtime.context.user_id}
    ).get("ids", [[]])[0]  

    return (
        df[df["video_id"].isin(similar_ids)]
        .apply(WatchItem.from_row, axis=1)
        .tolist()
    )

@tool
def find_similar_videos_hybrid(
    title_or_thumbnail_url: str, limit: int, runtime: ToolRuntime[AgentContext, AgentState]
) -> list[WatchItem]:
    """Invokes the VectorDB to find similar videos by title and/or thumbnail.
    Likely the first result is going to be the query video itself, so the second result is the truly "most similar" video.
    Args:
        title_or_thumbnail_url (str): A title or thumbnail (local file path) to find similar videos for.
        limit (int): The number of similar videos to return. Defaults to 5.
    Returns:
        list[WatchItem]: A list of similar videos
    """

    # Embed the input title and thumbnail
    if title_or_thumbnail_url.lower().endswith((".jpg", ".jpeg", ".png")):
        # treat as thumbnail path
        query_vec = embed_image(Image.open(title_or_thumbnail_url))
    else:
        # treat as text
        query_vec = embed_text(title_or_thumbnail_url)

    # Query the vector database for similar videos
    similar_ids = collection_hybrid.query(                    # <-- uses hybrid collection
        query_embeddings=query_vec,
        n_results=limit or 5,
        where={"user_id": runtime.context.user_id}
    ).get("ids", [[]])[0]  

    return (
        df[df["video_id"].isin(similar_ids)]
        .apply(WatchItem.from_row, axis=1)
        .tolist()
    )

@tool
def retrieve_session(
    sort_asc: bool, limit: int, runtime: ToolRuntime[AgentContext, AgentState]
) -> Command:
    """Loads a user's watch session in the agent state.
    Args:
        sort_asc (bool): sort oldest first if True
        limit (int): maximum number of videos to retrieve
    Returns:
        Command: Updates the agent state with the retrieved watch history.
    """
    df = pd.read_csv(CSV_PATH)
    df = df[df["user_id"] == runtime.context.user_id]  # Filter by user ID from state
    df = df.sort_values("watch_date", ascending=sort_asc)
    df = df.head(limit) if limit else df
    result = df.apply(
        WatchItem.from_row, axis=1
    ).tolist()  # Convert to WatchItem list

    return Command(
        update={
            "watch_history": result,  # Update agent state with the retrieved watch history
            "messages": [
                ToolMessage(content=str(result), tool_call_id=runtime.tool_call_id)
            ],
        },
    )
