import streamlit as st

from app.container import get_container
from app.domain.entities import Item
from app.domain.exceptions import ReceiptParsingError
from app.use_cases.load_receipt import LoadReceiptInput

st.title("📤 Upload a Receipt")

container = get_container()

uploaded_file = st.file_uploader("Receipt photo", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is None:
    st.session_state.pop("parsed_receipt", None)
    st.session_state.pop("parsed_filename", None)
elif st.session_state.get("saved_filename") == uploaded_file.name:
    st.info("This receipt was already saved. Upload a different photo to add another one.")
else:
    image_bytes = uploaded_file.getvalue()
    st.image(image_bytes, caption=uploaded_file.name, width=300)

    already_parsed = st.session_state.get("parsed_filename") == uploaded_file.name
    if not already_parsed:
        with st.spinner("Reading the receipt..."):
            try:
                parsed = container.parse_receipt().execute(image_bytes)
                st.session_state["parsed_receipt"] = parsed
                st.session_state["parsed_filename"] = uploaded_file.name
            except ReceiptParsingError as exc:
                st.error(f"Couldn't read this receipt: {exc}")
                st.session_state.pop("parsed_receipt", None)

    parsed = st.session_state.get("parsed_receipt")
    if parsed is not None:
        st.subheader("Review extracted details")
        st.caption("The model may misread a receipt -- please double-check before saving.")

        with st.form("confirm_receipt"):
            place = st.text_input("Place", value=parsed.place)
            transaction_date = st.date_input("Transaction date", value=parsed.transaction_date)
            total = st.number_input("Total", value=float(parsed.total), min_value=0.0, step=1000.0)

            st.caption("Items")
            item_rows = st.data_editor(
                [item.model_dump(exclude={"id"}) for item in parsed.items],
                num_rows="dynamic",
                key="item_editor",
                use_container_width=True,
            )

            submitted = st.form_submit_button("Save receipt")

        if submitted:
            edited_items = [
                Item(name=row["name"], price=float(row["price"]), quantity=int(row["quantity"]))
                for row in item_rows
                if row.get("name")
            ]
            edited = parsed.model_copy(
                update={
                    "place": place,
                    "transaction_date": transaction_date,
                    "total": total,
                    "items": edited_items,
                }
            )
            receipt = container.load_receipt().execute(
                LoadReceiptInput(
                    parsed=edited, image_bytes=image_bytes, image_filename=uploaded_file.name
                )
            )
            st.session_state.pop("parsed_receipt", None)
            st.session_state.pop("parsed_filename", None)
            st.session_state["saved_filename"] = uploaded_file.name
            st.success(f"Saved receipt #{receipt.id} from {receipt.place}")
            st.rerun()
