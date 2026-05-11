from typing import Annotated

from langchain.agents import create_agent, AgentState as BaseAgentState
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from model_commons import *


@dataclass
class WatchItem:
    video_id: str
    video_title: str
    timestamp: str  # ISO format

    @classmethod
    def from_row(cls, row) -> "WatchItem":
        return cls(
            video_id=row["video_id"],
            video_title=row["video_title"],
            timestamp=row["watch_date"],
        )

    def __repr__(self):  # json
        return str(asdict(self))

class AgentState(BaseAgentState):  # tool-managed state (short-term memory)
    watch_history: list[WatchItem]  # @dataclass

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


SYSTEM_PROMPT = """
You are a YouTube watch-history analysis agent focused on bias, polarization, sensationalism, clickbait, emotional tone, and rabbit-hole effects.

# Rules:
- If you are sure about the user’s intent AND it matches a tool’s purpose, call that tool with appropriately typed arguments. Otherwise, do not call any tool and ask for clarification.
- When asked about bias, polarization, sensationalism, clickbait, emotional tone, or rabbit-hole effects, ensure the watch history was retrieved using the relative tool.
- Base all claims on factual data from watch history and tool results. For each claim, mention a specific example from the watch history that supports it (e.g., a video title or topic). Avoid vague generalizations.
- Be cautious and do not overclaim ideology; if unsure, say that the evidence is weak or ambiguous and optionally ask for clarification.
- When asked to display an image, respond with the [markdown tag](URL), where URL is the best image URL from user input, state, memory, or tools.
- Do not call tools multiple times in the same turn; if you need to call another tool, wait for the next turn to do so.
- Never use tables.
"""

agent = create_agent(
    llm.model_copy(),
    tools=[retrieve_session],
    state_schema=AgentState,
    context_schema=AgentContext,
    system_prompt=SYSTEM_PROMPT,
    middleware=MIDDLEWARE,
    checkpointer=CHECKPOINTER,
)