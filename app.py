import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

st.set_page_config(page_title="ระบบสต็อกรถมือสอง", layout="wide")

# เชื่อมต่อ Google Sheets ผ่าน Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl=0)

st.title("🚗 ระบบจัดการสต็อกรถยนต์")

menu = ["ดูสต็อกรถ", "เพิ่มรถใหม่", "คำนวณเงินผ่อน"]
choice = st.sidebar.selectbox("เมนู", menu)

if choice == "ดูสต็อกรถ":
    df = get_data()
    if not df.empty:
        df = df.dropna(subset=['id'])
        for _, row in df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    if str(row['image_path']) != 'nan' and row['image_path'] != "":
                        st.image(row['image_path'], use_container_width=True)
                with c2:
                    st.subheader(f"{row['brand']} {row['model']}")
                    st.write(f"ทะเบียน: {row['plate_number']} | สี: {row['color']}")
                with c3:
                    price = float(row['sell_price_no_vat'])
                    st.metric("ราคาสุทธิ (+VAT)", f"{price * 1.07:,.2f}")
    else:
        st.info("ยังไม่มีข้อมูล")

elif choice == "เพิ่มรถใหม่":
    with st.form("add_form"):
        car_id = st.text_input("รหัสรถ")
        brand = st.text_input("ยี่ห้อ")
        model = st.text_input("รุ่น")
        price = st.number_input("ราคาขาย (ไม่รวม VAT)", min_value=0.0)
        img = st.text_input("ลิงก์รูปภาพ")
        if st.form_submit_button("บันทึก"):
            df_old = get_data()
            new_row = pd.DataFrame([{"id": car_id, "brand": brand, "model": model, "sell_price_no_vat": price, "image_path": img, "year": 2024, "status": "พร้อมขาย"}])
            updated_df = pd.concat([df_old, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("บันทึกแล้ว!")
