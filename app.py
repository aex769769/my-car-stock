import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os

# --- ตั้งค่าฐานข้อมูล ---
def init_db():
    conn = sqlite3.connect('used_car_stock_v3.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id TEXT PRIMARY KEY,
            brand TEXT, model TEXT, year INTEGER, color TEXT,
            plate_number TEXT, buy_price REAL, repair_cost REAL,
            sell_price_no_vat REAL, vat_amount REAL, total_sell_price REAL,
            status TEXT, link TEXT, image_path TEXT, date_added DATE
        )
    ''')
    conn.commit()
    return conn

if not os.path.exists("car_images"):
    os.makedirs("car_images")

conn = init_db()

st.set_page_config(page_title="ระบบสต็อกรถยนต์", layout="wide")

# --- ฟังก์ชันช่วยอัปเดตข้อมูล ---
def update_car_data(car_id, brand, model, year, color, plate, sell_price, status, link):
    vat = sell_price * 0.07
    total = sell_price + vat
    c = conn.cursor()
    c.execute('''UPDATE cars SET brand=?, model=?, year=?, color=?, plate_number=?, 
                 sell_price_no_vat=?, vat_amount=?, total_sell_price=?, status=?, link=? 
                 WHERE id=?''', 
              (brand, model, year, color, plate, sell_price, vat, total, status, link, car_id))
    conn.commit()

# --- เมนูหลัก ---
menu = ["ดูสต็อกรถ", "เพิ่มรถเข้าใหม่", "คำนวณการผ่อน", "สรุปกำไร"]
choice = st.sidebar.selectbox("เมนูหลัก", menu)

if choice == "ดูสต็อกรถ":
    st.subheader("📋 รายการรถในสต็อก")
    df = pd.read_sql_query("SELECT * FROM cars", conn)
    
    if not df.empty:
        for index, row in df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 2, 1.5])
                with col1:
                    if row['image_path'] and os.path.exists(row['image_path']):
                        st.image(row['image_path'], use_container_width=True)
                    else:
                        st.write("📷 ไม่มีรูปภาพ")
                
                with col2:
                    st.markdown(f"### {row['brand']} {row['model']} ({row['year']})")
                    st.write(f"**รหัส:** {row['id']} | **สี:** {row['color']} | **ทะเบียน:** {row['plate_number']}")
                    st.write(f"**สถานะ:** :blue[{row['status']}]")
                    if row['link']:
                        st.markdown(f"[🔗 ลิงก์ประกาศ]({row['link']})")
                
                with col3:
                    st.write(f"**ราคาสุทธิ:** {row['total_sell_price']:,.2f} บาท")
                    
                    # --- ปุ่มแก้ไข (ใช้ Modal/Dialog) ---
                    if st.button(f"📝 แก้ไขข้อมูล {row['id']}", key=f"edit_{row['id']}"):
                        st.session_state[f"editing_{row['id']}"] = True

                # --- ส่วนของฟอร์มแก้ไข (จะแสดงเมื่อกดปุ่มแก้ไข) ---
                if st.session_state.get(f"editing_{row['id']}", False):
                    with st.expander(f"แก้ไขรายละเอียด: {row['brand']} {row['model']}", expanded=True):
                        with st.form(key=f"form_{row['id']}"):
                            e_col1, e_col2 = st.columns(2)
                            with e_col1:
                                new_brand = st.text_input("ยี่ห้อ", value=row['brand'])
                                new_model = st.text_input("รุ่น", value=row['model'])
                                new_status = st.selectbox("สถานะ", ["พร้อมขาย", "จองแล้ว", "ขายแล้ว", "กำลังซ่อม"], index=["พร้อมขาย", "จองแล้ว", "ขายแล้ว", "กำลังซ่อม"].index(row['status']))
                            with e_col2:
                                new_sell_price = st.number_input("ราคาขาย (ก่อน VAT)", value=float(row['sell_price_no_vat']))
                                new_plate = st.text_input("ทะเบียน", value=row['plate_number'])
                                new_link = st.text_input("ลิงก์", value=row['link'])
                            
                            if st.form_submit_button("บันทึกการเปลี่ยนแปลง"):
                                update_car_data(row['id'], new_brand, new_model, row['year'], row['color'], new_plate, new_sell_price, new_status, new_link)
                                st.session_state[f"editing_{row['id']}"] = False
                                st.success("อัปเดตข้อมูลสำเร็จ!")
                                st.rerun()
                            
                            if st.button("ยกเลิก", key=f"cancel_{row['id']}"):
                                st.session_state[f"editing_{row['id']}"] = False
                                st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลรถในสต็อก")

# --- (ส่วนเมนูอื่นๆ ยังคงเดิมเหมือนโค้ดก่อนหน้า) ---
elif choice == "เพิ่มรถเข้าใหม่":
    # (Copy โค้ดส่วน "เพิ่มรถเข้าใหม่" จากอันเดิมมาวางที่นี่)
    st.subheader("➕ เพิ่มรถเข้าสต็อก")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            car_id = st.text_input("รหัสสินค้า")
            brand = st.text_input("ยี่ห้อ")
            model = st.text_input("รุ่น")
            year = st.number_input("ปี", min_value=1990, max_value=2026, value=2020)
            color = st.text_input("สีรถ")
        with col2:
            plate = st.text_input("เลขทะเบียน")
            buy_price = st.number_input("ราคารับเข้า", min_value=0.0)
            repair_cost = st.number_input("ค่าซ่อมบำรุง", min_value=0.0)
            sell_price_input = st.number_input("ราคาขายที่ต้องการ (ยังไม่รวม VAT)", min_value=0.0)
            link = st.text_input("ลิงก์ประกาศขาย")
        
        uploaded_file = st.file_uploader("อัปโหลดรูปรถ", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("บันทึกข้อมูล"):
            image_path = os.path.join("car_images", f"{car_id}.jpg") if uploaded_file else ""
            if uploaded_file:
                with open(image_path, "wb") as f: f.write(uploaded_file.getbuffer())
            
            vat_calc = sell_price_input * 0.07
            total_calc = sell_price_input + vat_calc
            c = conn.cursor()
            c.execute('''INSERT INTO cars VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (car_id, brand, model, year, color, plate, buy_price, repair_cost, 
                       sell_price_input, vat_calc, total_calc, "พร้อมขาย", link, image_path, datetime.date.today()))
            conn.commit()
            st.success("บันทึกสำเร็จ!")
            st.rerun()

elif choice == "คำนวณการผ่อน":
    # (Copy โค้ดส่วน "คำนวณการผ่อน" จากอันเดิมมาวางที่นี่)
    st.subheader("🧮 เครื่องคำนวณค่างวด")
    price_net = st.number_input("ราคารถสุทธิ (รวม VAT แล้ว)", min_value=0.0)
    # ... ใส่โค้ดคำนวณเดิม ...

elif choice == "สรุปกำไร":
    # (Copy โค้ดส่วน "สรุปกำไร" จากอันเดิมมาวางที่นี่)
    st.subheader("💰 สรุปกำไร")
    # ... ใส่โค้ดคำนวณกำไรเดิม ...
