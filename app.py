import streamlit as st
import sqlite3
import pandas as pd
import os
import datetime
import base64
from io import BytesIO
from PIL import Image, ImageEnhance
import plotly.express as px

st.set_page_config(page_title="Test", page_icon="📚")

# DB
DB = os.path.join(os.getcwd(), "study_data.db")
os.makedirs(os.path.join(os.getcwd(), "images"), exist_ok=True)

def init_db():
    c = sqlite3.connect(DB); c.execute("""CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY AUTOINCREMENT,date TEXT,type TEXT,subject TEXT,content TEXT,detail TEXT DEFAULT '',image_path TEXT DEFAULT '',review_count INTEGER DEFAULT 0,last_reviewed TEXT DEFAULT '')"""); c.commit(); c.close()
init_db()

def get_conn(): return sqlite3.connect(DB)

def process_image(raw_bytes):
    img = Image.open(BytesIO(raw_bytes)).convert("RGB")
    if img.width > 1920:
        ratio = 1920 / img.width
        img = img.resize((1920, int(img.height * ratio)), Image.Resampling.LANCZOS)
    img = ImageEnhance.Sharpness(img).enhance(1.8)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    b = BytesIO(); img.save(b, format="JPEG", quality=90, optimize=True)
    return base64.b64encode(b.getvalue()).decode()

if "photo_b64" not in st.session_state: st.session_state.photo_b64 = None

st.title("📚 学习库 - 精简测试版")
st.write(f"PIL version: {Image.__version__}")
st.write(f"Streamlit: {st.__version__}")
st.write(f"Python: {__import__('sys').version}")

# Test process_image
if st.button("测试图片处理"):
    from PIL import ImageDraw
    test_img = Image.new("RGB", (4000, 3000), (100,150,200))
    draw = ImageDraw.Draw(test_img); draw.text((100,100), "Test", fill=(255,255,255))
    buf = BytesIO(); test_img.save(buf, format="PNG")
    result = process_image(buf.getvalue())
    st.image(base64.b64decode(result), caption="处理后", use_container_width=True)
    st.write(f"Size: {len(result)/1024:.0f} KB")

# Test photo capture
st.subheader("📷 拍照测试")
cam = st.camera_input("", key="test_cam", label_visibility="collapsed")
if cam:
    raw = cam.getvalue()
    st.session_state.photo_b64 = process_image(raw)
    st.image(base64.b64decode(st.session_state.photo_b64), use_container_width=True)
    st.success("✅ 拍照+处理成功")

# Test DB write
if st.button("测试数据库写入"):
    conn = get_conn()
    conn.execute("INSERT INTO entries (date,type,subject,content,detail) VALUES (?,?,?,?,?)",
                 (datetime.date.today().strftime("%Y-%m-%d"), "知识点", "数学", "测试", "测试"))
    conn.commit(); conn.close()
    st.success("✅ 数据库写入成功")

st.write("---")
st.caption("如果以上测试全部通过，说明基础功能正常。")