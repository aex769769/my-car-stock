import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os

# --- ตั้งค่าฐานข้อมูล ---
def init_db():
    conn = sqlite3.connect('used_car_stock_v2.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id TEXT PRIMARY KEY,
            brand TEXT, model TEXT, year INTEGER, color TEXT,
            plate_number TEXT, buy_price REAL, repair_cost REAL,
            sell_price REAL, status TEXT, link TEXT, 
            image_path TEXT, date_added DATE
        )
    ''')
    conn.commit()
    return conn

# สร้างโฟลเดอร์เก็บรูป
if not os.path.exists("car_images"):
    os.makedirs("car_images")

conn = init_db()

st.set_page_config(page_title="ระบบสต็อกรถมือสอง V2", layout="wide")
st.title("🚗 ระบบสต็อกรถยนต์มือสอง (Full Option)")

menu = ["ดูสต็อกรถ", "เพิ่มรถเข้าใหม่", "คำนวณการผ่อน", "สรุปกำไร"]
choice = st.sidebar.selectbox("เมนูหลัก", menu)

# --- 1. ดูสต็อกรถ ---
if choice == "ดูสต็อกรถ":
    st.subheader("📋 รายการรถในสต็อก")
    df = pd.read_sql_query("SELECT * FROM cars", conn)
    if not df.empty:
        for index, row in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 2])
                with col1:
                    if row['image_path'] and os.path.exists(row['image_path']):
                        st.image(row['image_path'], use_container_width=True)
                    else:
                        st.write("📷 ไม่มีรูปภาพ")
                with col2:
                    st.markdown(f"### {row['brand']} {row['model']} ({row['year']})")
                    st.write(f"**รหัส:** {row['id']} | **สี:** {row['color']}")
                    st.write(f"**ทะเบียน:** {row['plate_number']}")
                    if row['link']:
                        st.markdown(f"[🔗 ดูลิงก์ประกาศขาย]({row['link']})")
                with col3:
                    st.write(f"**ราคาขาย:** {row['sell_price']:,.2f} บาท")
                    st.write(f"**สถานะ:** {row['status']}")
                    if st.button(f"ดูรายละเอียด/แก้ไข {row['id']}"):
                        st.info("ฟีเจอร์แก้ไขกำลังพัฒนา")
                st.divider()
    else:
        st.info("ยังไม่มีข้อมูล")

# --- 2. เพิ่มรถเข้าใหม่ ---
elif choice == "เพิ่มรถเข้าใหม่":
    st.subheader("➕ เพิ่มรถเข้าสต็อก")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            car_id = st.text_input("รหัสสินค้า (เช่น CAR-001)")
            brand = st.text_input("ยี่ห้อ")
            model = st.text_input("รุ่น")
            year = st.number_input("ปี", min_value=1990, max_value=2026, value=2015)
            color = st.text_input("สีรถ")
        with col2:
            plate = st.text_input("เลขทะเบียน")
            buy_price = st.number_input("ราคารับเข้า", min_value=0.0)
            repair_cost = st.number_input("ค่าซ่อม/ปรับสภาพ", min_value=0.0)
            sell_price = st.number_input("ราคาตั้งขาย", min_value=0.0)
            link = st.text_input("ลิงก์ประกาศขาย (ถ้ามี)")
        
        uploaded_file = st.file_uploader("อัปโหลดรูปรถ", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("บันทึกข้อมูล"):
            image_path = ""
            if uploaded_file:
                image_path = os.path.join("car_images", f"{car_id}.jpg")
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO cars VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                          (car_id, brand, model, year, color, plate, buy_price, 
                           repair_cost, sell_price, "พร้อมขาย", link, image_path, datetime.date.today()))
                conn.commit()
                st.success("บันทึกสำเร็จ!")
            except:
                st.error("รหัสสินค้าซ้ำหรือข้อมูลผิดพลาด")

# --- 3. ตารางการผ่อน ---
elif choice == "คำนวณการผ่อน":
    st.subheader("🧮 เครื่องคำนวณค่างวด")
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("ราคารถ", min_value=0.0)
        down = st.number_input("เงินดาวน์", min_value=0.0)
        interest_year = st.number_input("ดอกเบี้ยต่อปี (%)", min_value=0.0, value=4.0)
        years = st.selectbox("จำนวนปีที่ผ่อน", [1, 2, 3, 4, 5, 6, 7])
    
    finance_amount = price - down
    total_interest = finance_amount * (interest_year / 100) * years
    total_debt = finance_amount + total_interest
    monthly_payment = total_debt / (years * 12)
    
    with col2:
        st.write("### ยอดที่ต้องจ่าย")
        st.metric("ผ่อนต่อเดือนโดยประมาณ", f"{monthly_payment:,.2f} บาท")
        st.write(f"ยอดจัดไฟแนนซ์: {finance_amount:,.2f} บาท")
        st.write(f"ดอกเบี้ยรวม ({years} ปี): {total_interest:,.2f} บาท")
        st.write(f"ยอดรวมทั้งหมด: {total_debt:,.2f} บาท")

# --- 4. สรุปกำไร ---
elif choice == "สรุปกำไร":
    st.subheader("💰 สรุปรายรับ-รายจ่าย")
    df = pd.read_sql_query("SELECT * FROM cars", conn)
    if not df.empty:
        total_inv = (df['buy_price'] + df['repair_cost']).sum()
        st.metric("มูลค่ารถในสต็อกทั้งหมด (ต้นทุน)", f"{total_inv:,.2f} บาท")
        st.write("ตารางต้นทุนแยกคัน:")
        df['cost'] = df['buy_price'] + df['repair_cost']
        st.table(df[['id', 'brand', 'model', 'cost', 'status']])