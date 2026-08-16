from pathlib import Path

import streamlit as st

from app.container import get_container

PAGES_DIR = Path(__file__).parent / "entrypoints" / "pages"


def main() -> None:
    st.set_page_config(page_title="Food Receipt Tracker", page_icon="🧾", layout="wide")

    get_container()  # warm up the DB pool, schema, and LLM client once per process

    pages = [
        st.Page(PAGES_DIR / "home.py", title="Home", icon="🏠", default=True),
        st.Page(PAGES_DIR / "upload.py", title="Upload Receipt", icon="📤"),
        st.Page(PAGES_DIR / "data.py", title="My Receipts", icon="🧾"),
        st.Page(PAGES_DIR / "agent.py", title="Ask", icon="💬"),
    ]
    st.navigation(pages).run()


if __name__ == "__main__":
    main()
