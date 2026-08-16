import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from app.container import get_container
from app.use_cases.query_receipt import AskQuestionInput

st.title("💬 Ask about your receipts")
st.caption(
    "e.g. \"What food did I buy yesterday?\", \"Give me total expenses for food on 20 June\", "
    "\"Where did I buy hamburger from in the last 7 days?\""
)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if st.session_state["chat_history"] and st.button("Clear conversation"):
    st.session_state["chat_history"] = []
    st.rerun()

for message in st.session_state["chat_history"]:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.write(message.text)

question = st.chat_input("Ask a question about your receipts")
if question:
    st.session_state["chat_history"].append(HumanMessage(content=question))
    with st.chat_message("user"):
        st.write(question)

    container = get_container()
    with st.chat_message("assistant"):
        answer = st.write_stream(
            container.ask_question().stream(
                AskQuestionInput(
                    question=question, history=st.session_state["chat_history"][:-1]
                )
            )
        )
    st.session_state["chat_history"].append(AIMessage(content=answer))
