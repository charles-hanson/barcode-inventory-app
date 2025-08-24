
import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import pandas as pd
import io

# Custom CSS for red, black, and white theme
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
        }
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #d00000;
        }
        .css-1cpxqw2, .css-1v0mbdj, .css-1x8cf1d {
            background-color: #d00000 !important;
            color: #ffffff !important;
        }
        .stButton>button {
            background-color: #d00000;
            color: white;
            border: none;
            padding: 0.5em 1em;
            border-radius: 5px;
        }
        .stTextInput>div>input, .stNumberInput>div>input {
            border: 1px solid #d00000;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Barcode Scanner Inventory App")

st.write("Use your phone camera to scan a barcode or manually enter items to log inventory.")

uploaded_image = st.camera_input("Scan a barcode")

if "inventory" not in st.session_state:
    st.session_state.inventory = {}

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    decoded_objects = decode(image)

    if decoded_objects:
        for obj in decoded_objects:
            barcode_data = obj.data.decode("utf-8")
            if barcode_data in st.session_state.inventory:
                st.session_state.inventory[barcode_data] += 1
            else:
                st.session_state.inventory[barcode_data] = 1
            st.success(f"Scanned and added to inventory: {barcode_data}")
    else:
        st.warning("No barcode detected. Please try again.")

st.subheader("Manual Entry")
manual_name = st.text_input("Item Name")
manual_quantity = st.number_input("Quantity", min_value=1, step=1)
if st.button("Add Item Manually"):
    if manual_name:
        if manual_name in st.session_state.inventory:
            st.session_state.inventory[manual_name] += manual_quantity
        else:
            st.session_state.inventory[manual_name] = manual_quantity
        st.success(f"Manually added: {manual_name} x{manual_quantity}")
    else:
        st.warning("Please enter an item name.")

st.subheader("Inventory List")
updated_inventory = {}
for item, qty in st.session_state.inventory.items():
    new_qty = st.number_input(f"{item}", value=qty, min_value=0, step=1, key=item)
    updated_inventory[item] = new_qty
st.session_state.inventory = updated_inventory

if st.button("Export to Excel"):
    df = pd.DataFrame(list(st.session_state.inventory.items()), columns=["Item", "Quantity"])
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")
    st.download_button(label="Download Inventory Excel File",
                       data=excel_buffer.getvalue(),
                       file_name="inventory.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
