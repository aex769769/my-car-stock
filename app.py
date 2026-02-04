import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

st.set_page_config(page_title="ระบบสต็อกรถยนต์ (Full Sync)", layout="wide")

# --- เชื่อมต่อ Google Sheets ---
conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันดึงข้อมูลล่าสุด
def get_data():
    return conn.read(ttl="0") # ttl="0" เพื่อให้ดึงข้อมูลใหม่ล่าสุดเสมอเมื่อเรียกใช้งาน

st.title("🚗 ระบบจัดการสต็อกรถยนต์ (Write to Sheets)")

menu = ["ดูสต็อกรถ", "เพิ่มรถเข้าสต็อก", "คำนวณการผ่อน"]
choice = st.sidebar.selectbox("เมนูหลัก", menu)

# --- 1. หน้าดูสต็อกรถ ---
if choice == "ดูสต็อกรถ":
    st.subheader("📋 รายการรถปัจจุบัน")
    df = get_data()
    
    if not df.empty:
        df = df.dropna(subset=['id']) # กรองเฉพาะแถวที่มีรหัสรถ
        for index, row in df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 2, 1.5])
                with col1:
                    if str(row['image_path']) != 'nan' and row['image_path'] != "":
                        st.image(row['image_path'], use_container_width=True)
                    else:
                        st.write("📷 ไม่มีรูปภาพ")
                with col2:
                    st.markdown(f"### {row['brand']} {row['model']} ({int(row['year'])})")
                    st.write(f"**รหัส:** {row['id']} | **สี:** {row['color']} | **ทะเบียน:** {row['plate_number']}")
                    st.write(f"**สถานะ:** :blue[{row['status']}]")
                with col3:
                    sell_no_vat = float(row['sell_price_no_vat'])
                    vat = sell_no_vat * 0.07
                    st.write(f"**ราคาขาย (ก่อน VAT):** {sell_no_vat:,.2f}")
                    st.write(f"**ภาษี VAT 7%:** {vat:,.2f}")
                    st.markdown(f"**ราคาสุทธิ: {sell_no_vat + vat:,.2f} บาท**")
    else:
        st.info("ไม่มีข้อมูลในระบบ")

# --- 2. หน้าเพิ่มรถเข้าสต็อก (เขียนข้อมูลลง Sheets) ---
elif choice == "เพิ่มรถเข้าสต็อก":
    st.subheader("➕ กรอกข้อมูลรถใหม่")
    df = get_data()
    
    with st.form("add_car_form"):
        c1, c2 = st.columns(2)
        with c1:
            car_id = st.text_input("รหัสรถ (Product ID)")
            brand = st.text_input("ยี่ห้อ")
            model = st.text_input("รุ่น")
            year = st.number_input("ปีรถ", value=2020)
        with c2:
            color = st.text_input("สีรถ")
            plate = st.text_input("ทะเบียน")
            sell_price = st.number_input("ราคาขาย (ไม่รวม VAT)", min_value=0.0)
            status = st.selectbox("สถานะ", ["พร้อมขาย", "จองแล้ว", "กำลังซ่อม"])
        
        img_url = st.text_input("ลิงก์รูปภาพ (นำรูปไปฝากเว็บรับฝากรูปแล้วเอาลิงก์มาแปะ)")
        link = st.text_input("ลิงก์หน้าประกาศขาย")
        
        submit = st.form_submit_button("บันทึกข้อมูลลง Google Sheets")
        
        if submit:
            if car_id == "":
                st.error("กรุณาใส่รหัสรถ")
            else:
                # เตรียมข้อมูลใหม่
                new_data = pd.DataFrame([{
                    "id": car_id,
                    "brand": brand,
                    "model": model,
                    "year": year,
                    "color": color,
                    "plate_number": plate,
                    "sell_price_no_vat": sell_price,
                    "status": status,
                    "image_path": img_url,
                    "link": link,
                    "date_added": str(datetime.date.today())
                }])
                
                # รวมข้อมูลเก่ากับใหม่
                updated_df = pd.concat([df, new_data], ignore_index=True)
                
                # เขียนกลับไปที่ Sheets
                conn.update(data=updated_df)
                st.success("บันทึกข้อมูลสำเร็จ! ข้อมูลถูกส่งไปที่ Google Sheets แล้ว")
                st.balloons()

# --- 3. หน้าคำนวณการผ่อน ---
elif choice == "คำนวณการผ่อน":
    st.subheader("🧮 คำนวณค่างวด")
    price = st.number_input("ราคารถสุทธิ (รวม VAT)", min_value=0.0)
    down = st.number_input("เงินดาวน์", min_value=0.0)
    rate = st.number_input("ดอกเบี้ยต่อปี (%)", value=3.5)
    years = st.slider("ระยะเวลาผ่อน (ปี)", 1, 7, 4)
    
    if price > 0:
        loan = price - down
        interest = loan * (rate/100) * years
        monthly = (loan + interest) / (years * 12)
        st.metric("ผ่อนต่อเดือน", f"{monthly:,.2f} บาท")
