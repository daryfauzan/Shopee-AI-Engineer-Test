import streamlit as st

from app.container import get_container

st.title("🧾 My Receipts")

container = get_container()
receipts = container.list_receipts().execute()

if not receipts:
    st.info("No receipts uploaded yet. Head to the Upload Receipt page to add one.")
else:
    image_store = container.image_store()
    for receipt in receipts:
        date_label = receipt.transaction_date or "unknown date"
        with st.expander(f"{receipt.place} — Rp {receipt.total:,.0f} ({date_label})"):
            left, right = st.columns([1, 2])
            with left:
                try:
                    st.image(image_store.read(receipt.image_path), width=250)
                except FileNotFoundError:
                    st.caption("Image not available")
            with right:
                st.caption(f"Uploaded {receipt.uploaded_at:%Y-%m-%d %H:%M}")
                st.table(
                    [
                        {
                            "Item": item.name,
                            "Qty": item.quantity,
                            "Price": f"Rp {item.price:,.0f}",
                        }
                        for item in receipt.items
                    ]
                )
