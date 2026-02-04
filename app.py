import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

st.set_page_config(page_title="ระบบสต็อกรถยนต์ (Full Sync)", layout="wide")

# --- เชื่อมต่อ Google Sheets ---
# แนะนำให้ดึง URL จาก Secrets เท่านั้น ไม่ต้องแปะ URL ในโค้ดที่มีภาษาไทย
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # ใช้การเรียกแบบธรรมดา ลดความเสี่ยงเรื่อง Encode
    return conn.read(ttl=0) 

st.title("🚗 ระบบจัดการสต็อกรถยนต์")

# ... ส่วนเมนูต่างๆ เหมือนเดิม ...
