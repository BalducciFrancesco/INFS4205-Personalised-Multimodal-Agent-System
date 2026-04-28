# The "Rabbit Hole" Multimodal Agent (Adapted)

**Course:** UQ INFS4205/7205 - A3 Personalised Multimodal Agent System  
**Core Concept:** An intelligent LangGraph agent that acts as a **"Cognitive Shield"**. It analyzes a user's YouTube watch session, derived from a public user-level usage dataset, to detect filter bubbles, algorithmic polarization, and missing counter-information.

## 🤖 Copilot AI Instructions

If you are an AI assistant reading this file to help the developer:

- **Do not write the entire solution at once.** Guide the developer step-by-step.
- **Frameworks:** Use LangGraph for agent orchestration, an LLM API for reasoning, and a Vector DB for multimodal retrieval.
- **Assignment Goal:** This is a systems research project. The focus is on comparing system design choices such as routing, memory, and multimodal retrieval, not just building a chatbot that works.

## 📂 Phase 1: Data Preparation (The Knowledge Base)

*Goal: Curate a genuinely personalized, multimodal dataset from public YouTube usage logs.*

- **Source:**
  - Primary: *A YouTube Dataset with User-Level Usage Data* (Kaggle).
- **Task:**
  - Extract one or more **single-user chronological watch sessions** (for example, 10–15 videos in a row) to represent a "descent into a rabbit hole."
  - Each session should correspond to a coherent theme or emerging interest, if possible based on metadata.
- **Modality 1 (Text):**
  - Video titles, channel names if available, and any provided textual metadata such as category, tags, or description-like fields.
  - If the dataset contains only video IDs and minimal metadata, conceptually treat titles and descriptions as retrievable enrichment, but keep the stored local knowledge base limited to what is actually available for the assignment.
- **Modality 2 (Image):**
  - Dynamically fetch video thumbnails using the standard YouTube thumbnail URL format: `https://img.youtube.com/vi/[VIDEO_ID]/hqdefault.jpg`
  - Store or reference these thumbnails as the image modality for each watched video.
- **Note:**
  - The goal is not to reconstruct an entire user history. Instead, select representative **segments** for qualitative analysis, plus a broader subset for quantitative evaluation.

## 🔍 Phase 2: Indexing & Retrieval

*Goal: Build the multimodal retrieval pipeline over YouTube usage-based sessions.*

- **Task:** Embed both text metadata and visual thumbnail information into a Vector Database.
  - Text embeddings: titles, channel names, and available textual features.
  - Image embeddings: thumbnail images aligned to the corresponding videos.
- **Task:** Design a retrieval strategy.
  - Decide whether the agent queries text and image indices separately, or uses a joint multimodal representation.
  - Consider session-aware retrieval so the system can prefer temporally nearby videos when answering history questions.

## 🧠 Phase 3: Agent Workflow (LangGraph)

*Goal: Orchestrate tools and state rather than using a fixed pipeline.*

- **Task:** Define the **Agent State**, including:
  - Current user query.
  - Retrieved videos and metadata for the relevant session or sessions.
  - Conversation memory and any inferred bias profile.
- **Task:** Build specific **Tools** for the agent to route between:
  - **History Retriever:** Fetches videos from a selected user's watch timeline within the dataset subset.
  - **Bias/Polarization Analyzer:** Evaluates titles, categories, and thumbnails to estimate emotional tone, political leaning, sensationalism, or topical narrowing.
  - **Devil's Advocate (Optional):** Suggests missing counter-information or alternative perspectives not present in the watched session.
- **Task:** Implement routing logic so the agent decides:
  - When to retrieve more items from the user's history.
  - When to analyze bias versus simply answering factual questions.
  - When to invoke the Devil's Advocate to suggest balancing information.

## 🧪 Phase 4: Quantitative Evaluation

*Goal: Prove the agent works through rigorous comparison.*

- **The Query Suite:** Draft test queries covering four required families:
  1. **Factual:**
     - "What was the third video I watched in this session?"
     - "Which channel did I watch the most in this segment?"
  2. **Cross-Modal:**
     - "Did I watch any videos with angry or alarming thumbnails in this session?"
     - "Which thumbnails in my session look sensational or clickbait-like?"
  3. **Analytical Multi-Hop:**
     - "Based on my recent watch history, what political or ideological bias am I being exposed to?"
     - "Are my watched videos becoming narrower in topic or viewpoint over time?"
  4. **Conversational/Memory:**
     - "Follow up: What specific topics or channels should I explore to balance that bias?"
     - "Given my history, what is a good counter-rabbit-hole direction to diversify my feed?"
- **The Baselines & Ablations:**
  - **Baseline:** Plain LLM with raw watch history pasted into the prompt, no retrieval or routing.
  - **Ablation:** Fixed RAG pipeline that retrieves top-K videos from history and answers, but without routing or memory.
  - **Final System:** Full LangGraph agent using explicit tools, multimodal retrieval, and stateful routing logic.
- **Metrics:** Track at least:
  - **One Quality Metric:** Task success rate, annotator rating, or LLM-as-a-judge score.
  - **One Efficiency Metric:** Token usage, number of tool calls, latency, or similar.

## 📄 Phase 5: Deliverables

*Goal: Finalize submission for the 20-mark assessment.*

- **Report:**
  - Maximum 4 pages in systems paper style.
  - Must include problem framing, knowledge base design using the Kaggle user-level YouTube dataset, agent workflow, evaluation results, and failure analysis.
- **Codebase:**
  - Clean, documented repository with installation instructions, dependencies, and run instructions.
  - Zip file named `StudentID_Name.zip`.

## Next steps

- [ ] Select the final user/session subset from the YouTube dataset and lock the scope. [web:29]
- [ ] Define what “rabbit hole,” “bias,” and “missing counter-information” mean for this project. [web:42]
- [ ] Decide the three systems to compare: baseline, fixed RAG, and full LangGraph agent. [web:16][web:27]
- [ ] Sketch the LangGraph workflow: state, tools, routing, and outputs. [web:16][web:40]
- [ ] Create the evaluation query set across factual, cross-modal, analytical, and conversational questions. [web:29][web:42]
- [ ] Choose the evaluation metrics for quality and efficiency. [web:26][web:29]
- [ ] Decide the main ablations, such as no routing, no memory, or no multimodal signal. [web:27][web:46]
- [ ] Build and test the baseline system first. [web:16]
- [ ] Build and test the fixed RAG system next. [web:42]
- [ ] Build and test the full LangGraph agent last. [web:16][web:41]
- [ ] Record results, compare systems, and note key failure cases for the report. [web:26][web:43]
- [ ] Write the report around problem framing, system design, evaluation, results, and failure analysis. [web:16]