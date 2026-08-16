from collections.abc import Iterator
from datetime import date

from langchain_core.messages import BaseMessageChunk
from langgraph.graph.state import CompiledStateGraph

from .context import Context
from .state import State


class AgentRunner:
    def __init__(self, graph: CompiledStateGraph[State, Context, State, State]):
        self._graph = graph

    def run(self, state: State) -> State:
        context = Context(today=date.today().isoformat())
        result = self._graph.invoke(state, context=context)
        return State.model_validate(result)

    def stream(self, state: State) -> Iterator[str]:
        """Yields the final answer's text as it's generated, token by token.

        Intermediate tool-calling turns produce no (or empty) content, so filtering
        on the "agent" node and non-empty content naturally skips straight to the
        final response once any tool calls have been resolved.
        """
        context = Context(today=date.today().isoformat())
        for chunk, metadata in self._graph.stream(
            state, context=context, stream_mode="messages"
        ):
            if not isinstance(chunk, BaseMessageChunk) or not isinstance(metadata, dict):
                continue
            if metadata.get("langgraph_node") != "agent":
                continue
            # `.text` extracts only the text blocks from `content` -- some providers
            # (e.g. Gemini) return content as a list of blocks that also carry
            # non-text metadata (thought signatures, etc.) we don't want to render.
            text = chunk.text
            if text:
                yield str(text)
