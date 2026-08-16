from datetime import date

from langgraph.graph.state import CompiledStateGraph

from .context import Context
from .state import State


class AgentRunner:
    def __init__(self, graph: CompiledStateGraph):
        self._graph = graph

    def run(self, state: State) -> State:
        context = Context(today=date.today().isoformat())
        result = self._graph.invoke(state, context=context)
        return State.model_validate(result)
