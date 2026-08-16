import streamlit as st
from dependency_injector import containers, providers

from app.adapters import (
    LocalReceiptImageStore,
    build_chat_model,
    build_connection_pool,
    init_schema,
)
from app.agent.graph import create_graph
from app.agent.runner import AgentRunner
from app.agent.tools import build_tools
from app.config import Settings, get_settings
from app.infrastructure.db_repo import PostgresReceiptRepository
from app.use_cases.load_receipt import LoadReceipt
from app.use_cases.parse_receipt import ParseReceipt
from app.use_cases.query_receipt import (
    AskQuestion,
    GetReceipt,
    ListReceipts,
    SearchReceipts,
    SumExpenses,
)


class Container(containers.DeclarativeContainer):
    config: Settings = providers.Configuration()  # ty: ignore[invalid-assignment]

    connection_pool = providers.Singleton(
        build_connection_pool,
        dsn=config.database.dsn,
        min_size=config.database.min_pool_size,
        max_size=config.database.max_pool_size,
    )

    chat_model = providers.Singleton(
        build_chat_model,
        api_key=config.llm.google_api_key,
        model_name=config.llm.model_name,
    )

    image_store = providers.Singleton(
        LocalReceiptImageStore, base_dir=config.storage.receipts_dir
    )

    receipt_repository = providers.Singleton(
        PostgresReceiptRepository, pool=connection_pool
    )

    parse_receipt = providers.Factory(ParseReceipt, vision_model=chat_model)
    load_receipt = providers.Factory(
        LoadReceipt, repository=receipt_repository, image_store=image_store
    )

    list_receipts = providers.Factory(ListReceipts, repository=receipt_repository)
    get_receipt = providers.Factory(GetReceipt, repository=receipt_repository)
    search_receipts = providers.Factory(SearchReceipts, repository=receipt_repository)
    sum_expenses = providers.Factory(SumExpenses, repository=receipt_repository)

    agent_tools = providers.Singleton(
        build_tools, search_receipts=search_receipts, sum_expenses=sum_expenses
    )
    agent_graph = providers.Singleton(create_graph, model=chat_model, tools=agent_tools)
    agent_runner = providers.Singleton(AgentRunner, graph=agent_graph)

    ask_question = providers.Factory(AskQuestion, runner=agent_runner)


@st.cache_resource
def get_container() -> Container:
    container = Container()
    container.config.from_pydantic(get_settings())  # ty: ignore[unresolved-attribute]
    init_schema(container.connection_pool())
    return container
