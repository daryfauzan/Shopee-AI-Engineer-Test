import streamlit as st

from app.container import get_container

st.title("🧾 Food Receipt Tracker")
st.write(
    "Upload photos of your food purchase receipts, browse everything you've uploaded, "
    "and ask natural-language questions about what you bought, where, and how much you spent."
)

container = get_container()
receipts = container.list_receipts().execute()

col1, col2, col3 = st.columns(3)
col1.metric("Receipts uploaded", len(receipts))
col2.metric("Total spent", f"Rp {sum(r.total for r in receipts):,.0f}")
places = {r.place for r in receipts}
col3.metric("Places visited", len(places))

st.subheader("Try asking")
st.markdown(
    "- *What food did I buy yesterday?*\n"
    "- *Give me total expenses for food on 20 June*\n"
    "- *Where did I buy hamburger from in the last 7 days?*"
)
