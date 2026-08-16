from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .context import Context
from .state import State

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about the user's uploaded food "
    "purchase receipts. Today's date is {today}. Resolve relative dates such as 'yesterday' "
    "or 'last 7 days' into concrete YYYY-MM-DD date ranges yourself before calling tools. "
    "Always use the provided tools to look up receipts and to compute totals or sums -- "
    "never guess or add numbers up from memory. If the tools return no matching receipts, "
    "say so plainly instead of making up an answer."
)


def create_graph(
    model: BaseChatModel, tools: list[BaseTool]
) -> CompiledStateGraph[State, Context, State, State]:
    model_with_tools = model.bind_tools(tools)

    def call_model(state: State, runtime):
        context: Context = runtime.context
        messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(today=context.today)),
            *state.messages,
        ]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    graph_builder = StateGraph(state_schema=State, context_schema=Context)
    graph_builder.add_node("agent", call_model)
    graph_builder.add_node("tools", ToolNode(tools))

    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    graph_builder.add_edge("tools", "agent")

    return graph_builder.compile()
