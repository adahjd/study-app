import streamlit as st
import sqlite3
import pandas as pd
import os
import datetime
import base64
from io import BytesIO
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="个人知识与错题库", page_icon="📚", layout="wide")


# ── CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
    .stApp { background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 50%, #f8fafc 100%); }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 20px; }
    ::-webkit-scrollbar-thumb:hover { background: #a5b4fc; }

    /* ── Header ── */
    .main-header {
        font-size: 2.1rem; font-weight: 800; letter-spacing: -0.02em;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 40%, #a855f7 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 0.15rem;
    }
    .sub-header { font-size: 0.9rem; color: #94a3b8; font-weight: 500; letter-spacing: 0.3em; text-transform: uppercase; }

    /* ── Stat Cards ── */
    .stat-card {
        background: white; border-radius: 16px; padding: 1.4rem 1rem;
        text-align: center; border: 1px solid #e8ecf1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative; overflow: hidden;
    }
    .stat-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        border-radius: 16px 16px 0 0;
    }
    .stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.08); }
    .stat-card.purple::before { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
    .stat-card.green::before { background: linear-gradient(90deg, #059669, #10b981); }
    .stat-card.orange::before { background: linear-gradient(90deg, #f59e0b, #f97316); }
    .stat-card.blue::before { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
    .stat-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
    .stat-value {
        font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em;
        color: #1e293b;
    }
    .stat-label { font-size: 0.8rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

    /* ── Tabs ── */
    .stTabs [role="tablist"] {
        background: white; border-radius: 14px; padding: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid #e8ecf1; gap: 2px;
    }
    .stTabs [role="tab"] {
        border-radius: 10px !important; padding: 0.55rem 1rem !important;
        font-weight: 600 !important; font-size: 0.85rem !important;
        transition: all 0.2s ease !important; border: none !important;
        color: #94a3b8 !important; background: transparent !important;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important; box-shadow: 0 2px 8px rgba(99,102,241,0.35);
    }
    .stTabs [role="tab"]:hover:not([aria-selected="true"]) {
        background: #f1f5f9 !important; color: #6366f1 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 10px !important; font-weight: 600 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important; letter-spacing: 0.01em;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stButton > button:hover {
        transform: translateY(-1.5px);
        box-shadow: 0 6px 20px rgba(99,102,241,0.2) !important;
    }
    .stButton > button:active { transform: translateY(0); }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important;
    }
    .stButton > button[kind="secondary"] {
        background: white !important; color: #ef4444 !important; border: 1.5px solid #fecaca !important;
    }

    /* ── Expander ── */
    .stExpander {
        border-radius: 12px !important; border: 1px solid #e8ecf1 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03); transition: all 0.2s ease;
        background: white !important;
    }
    .stExpander:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.06); }

    /* ── Review Card ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important; border: 1px solid #e8ecf1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        background: white !important; overflow: hidden;
    }

    /* ── Progress bar ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a855f7) !important;
        border-radius: 20px !important;
    }
    .stProgress { border-radius: 20px !important; background: #e2e8f0 !important; }

    /* ── Inputs ── */
    .stTextInput input, .stTextArea textarea {
        border-radius: 10px !important; border: 1.5px solid #e2e8f0 !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
    }

    /* ── Dividers ── */
    hr { border: none; height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 1.2rem 0; }

    /* ── Camera / Upload ── */
    section[data-testid="stCameraInput"] {
        border-radius: 16px !important; overflow: hidden;
        border: 2px dashed #c7d2fe !important; background: #f8faff;
    }
    .stFileUploader {
        border-radius: 16px !important; border: 2px dashed #c7d2fe !important; background: #f8faff;
    }

    /* ── Radio buttons ── */
    div[role="radiogroup"] { background: white; border-radius: 12px; padding: 4px; border: 1px solid #e8ecf1; }
    div[role="radiogroup"] label {
        border-radius: 9px !important; padding: 0.45rem 0.9rem !important;
        font-weight: 500 !important; transition: all 0.2s ease !important;
    }
    div[role="radiogroup"] label[data-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important; color: white !important;
    }

    /* ── Mobile ── */
    @media (max-width: 768px) {
        .main-header { font-size: 1.4rem !important; }
        .stat-value { font-size: 1.6rem !important; }
        .stat-card { padding: 0.9rem 0.6rem !important; }
        .stat-icon { font-size: 1.2rem !important; }
        .stButton > button { font-size: 0.85rem !important; padding: 0.6rem 0.5rem !important; min-height: 44px !important; }
        .stTabs [role="tab"] { font-size: 0.7rem !important; padding: 0.4rem 0.55rem !important; }
    }
</style>
""", unsafe_allow_html=True)
# ── Helpers ──
def display_image(img_path_or_b64, caption="", width=300):
    """Display image from base64 string or file path."""
    if not img_path_or_b64:
        return
    try:
        img_data = base64.b64decode(img_path_or_b64)
        st.image(img_data, caption=caption, width=width)
    except Exception:
        if os.path.exists(img_path_or_b64):
            st.image(img_path_or_b64, caption=caption, width=width)

DB_FILE = os.path.join(os.getcwd(), "study_data.db")
IMAGE_DIR = os.path.join(os.getcwd(), "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, type TEXT NOT NULL,
        subject TEXT NOT NULL, content TEXT NOT NULL, detail TEXT DEFAULT '',
        image_path TEXT DEFAULT '', review_count INTEGER DEFAULT 0,
        last_reviewed TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit(); conn.close()

init_db()

def get_conn():
    return sqlite3.connect(DB_FILE)

def add_entry(date, entry_type, subject, content, detail, image_path=""):
    conn = get_conn()
    conn.execute("INSERT INTO entries (date,type,subject,content,detail,image_path) VALUES (?,?,?,?,?,?)",
                 (date, entry_type, subject, content, detail, image_path))
    conn.commit(); conn.close()

def update_entry(entry_id, date, entry_type, subject, content, detail):
    conn = get_conn()
    conn.execute("UPDATE entries SET date=?,type=?,subject=?,content=?,detail=? WHERE id=?",
                 (date, entry_type, subject, content, detail, entry_id))
    conn.commit(); conn.close()

def delete_entry(entry_id):
    conn = get_conn()
    row = conn.execute("SELECT image_path FROM entries WHERE id=?", (entry_id,)).fetchone()
    if row and row[0]:
        try: base64.b64decode(row[0])
        except:
            if os.path.exists(row[0]): os.remove(row[0])
    conn.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit(); conn.close()

def mark_reviewed(entry_id):
    conn = get_conn()
    today = datetime.date.today().strftime("%Y-%m-%d")
    conn.execute("UPDATE entries SET review_count=review_count+1, last_reviewed=? WHERE id=?", (today, entry_id))
    conn.commit(); conn.close()

def get_all_entries():
    conn = get_conn()
    df = pd.read_sql_query("SELECT id,date,type,subject,content,detail,image_path,review_count,last_reviewed FROM entries ORDER BY id DESC", conn)
    conn.close(); return df

def get_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    knowledge = conn.execute("SELECT COUNT(*) FROM entries WHERE type='知识点'").fetchone()[0]
    error = conn.execute("SELECT COUNT(*) FROM entries WHERE type='错题'").fetchone()[0]
    subject_counts = pd.read_sql_query("SELECT subject, COUNT(*) as cnt FROM entries GROUP BY subject", conn)
    detail_counts = pd.read_sql_query("SELECT detail, COUNT(*) as cnt FROM entries WHERE detail!='' GROUP BY detail", conn)
    recent = pd.read_sql_query("SELECT date, COUNT(*) as cnt FROM entries GROUP BY date ORDER BY date DESC LIMIT 14", conn)
    conn.close()
    return {"total": total, "knowledge": knowledge, "error": error, "subject_counts": subject_counts, "detail_counts": detail_counts, "recent": recent}

def export_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as w: df.to_excel(w, index=False, sheet_name="学习记录")
    return output.getvalue()

# ── Session ──
if "edit_id" not in st.session_state: st.session_state.edit_id = None
if "photo_b64" not in st.session_state: st.session_state.photo_b64 = None

# ── Header ──
st.markdown('<p class="main-header">📚 个人知识与错题管理系统</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">记录 · 复习 · 掌握 · 成长</p>', unsafe_allow_html=True)

tabs = st.tabs(["📊 看板", "📝 添加", "🔍 管理", "📷 拍照", "📋 复习"])

# ══ TAB 1: Dashboard ══
with tabs[0]:
    stats = get_stats()
    if stats["total"] == 0:
        st.info("👋 欢迎！目前还没有数据，先去「添加」或「拍照」开始吧！")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-card purple"><div class="stat-icon">📋</div><div class="stat-value">{stats["total"]}</div><div class="stat-label">总记录</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card green"><div class="stat-icon">💡</div><div class="stat-value">{stats["knowledge"]}</div><div class="stat-label">知识点</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card orange"><div class="stat-icon">❌</div><div class="stat-value">{stats["error"]}</div><div class="stat-label">错题</div></div>', unsafe_allow_html=True)
        with c4:
            streak = len(stats["recent"]) if not stats["recent"].empty else 0
            st.markdown(f'<div class="stat-card blue"><div class="stat-icon">🔥</div><div class="stat-value">{streak}</div><div class="stat-label">活跃天数</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("📈 每日记录趋势")
            if not stats["recent"].empty:
                recent_df = stats["recent"].sort_values("date")
                fig = px.line(recent_df, x="date", y="cnt", markers=True, labels={"date": "日期", "cnt": "记录数"})
                fig.update_traces(line_color="#667eea", marker=dict(size=8, color="#764ba2"))
                fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("暂无数据")
        with col_right:
            st.subheader("🗂 科目分布")
            if not stats["subject_counts"].empty:
                fig = px.pie(stats["subject_counts"], names="subject", values="cnt", color_discrete_sequence=px.colors.qualitative.Set2, hole=0.4)
                fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("暂无数据")

# ══ TAB 2: Add Entry ══
with tabs[1]:
    st.subheader("✏️ 记录新内容")
    if st.session_state.edit_id:
        st.warning(f"⚠️ 正在编辑记录 #{st.session_state.edit_id}")
        if st.button("❌ 取消编辑", key="cancel_edit_add"): st.session_state.edit_id = None; st.rerun()
    else:
        col1, col2, col3 = st.columns(3)
        with col1: data_type = st.selectbox("类型", ["知识点", "错题"], key="add_type")
        with col2: subject = st.selectbox("科目", ["数学", "英语", "语文", "物理", "化学", "生物", "历史", "地理", "政治", "其他"], key="add_subject")
        with col3: entry_date = st.date_input("日期", datetime.date.today(), key="add_date")
        content = st.text_area("内容描述", placeholder="知识点内容或错题描述...", height=150, key="add_content")
        detail_label = "掌握程度" if data_type == "知识点" else "错误原因分析"
        detail = st.text_input(detail_label, placeholder="例如：已掌握 / 计算失误...", key="add_detail")
        if st.button("💾 保存到库", use_container_width=True, key="save_entry"):
            if not content.strip(): st.error("内容描述不能为空！")
            else: add_entry(entry_date.strftime("%Y-%m-%d"), data_type, subject, content.strip(), detail.strip()); st.success(f"✅ 成功保存！"); st.rerun()

# ══ TAB 3: Browse ══
with tabs[2]:
    st.subheader("🔍 浏览 & 管理")
    df = get_all_entries()
    if df.empty:
        st.info("📭 还没有数据")
    else:
        f1, f2, f3 = st.columns(3)
        with f1: filter_type = st.selectbox("类型筛选", ["全部", "知识点", "错题"], key="browse_type")
        with f2:
            all_subjects = sorted(df["subject"].unique())
            filter_subject = st.multiselect("科目筛选", all_subjects, default=all_subjects, key="browse_subject")
        with f3: search_term = st.text_input("🔎 搜索", placeholder="关键词...", key="browse_search")
        filtered = df.copy()
        if filter_type != "全部": filtered = filtered[filtered["type"] == filter_type]
        if filter_subject: filtered = filtered[filtered["subject"].isin(filter_subject)]
        if search_term: filtered = filtered[filtered["content"].str.contains(search_term, case=False, na=False) | filtered["detail"].str.contains(search_term, case=False, na=False)]
        st.caption(f"共 {len(filtered)} 条记录")
        for i, row in filtered.iterrows():
            rid = row["id"]
            preview = row["content"][:50].replace("\n", " ")
            with st.expander(f"#{rid} | {row['date']} | {row['type']} | {row['subject']} | {preview}...", expanded=(st.session_state.edit_id == rid)):
                if st.session_state.edit_id == rid:
                    subjects_list = ["数学", "英语", "语文", "物理", "化学", "生物", "历史", "地理", "政治", "其他"]
                    subj_idx = subjects_list.index(row["subject"]) if row["subject"] in subjects_list else 0
                    e1, e2, e3 = st.columns(3)
                    with e1: new_type = st.selectbox("类型", ["知识点", "错题"], index=0 if row["type"]=="知识点" else 1, key=f"ed_type_{rid}")
                    with e2: new_subject = st.selectbox("科目", subjects_list, index=subj_idx, key=f"ed_subject_{rid}")
                    with e3: new_date = st.date_input("日期", datetime.datetime.strptime(row["date"], "%Y-%m-%d").date(), key=f"ed_date_{rid}")
                    new_content = st.text_area("内容", value=row["content"], height=120, key=f"ed_content_{rid}")
                    new_detail = st.text_input("掌握程度/错误原因", value=row["detail"] or "", key=f"ed_detail_{rid}")
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("💾 保存修改", key=f"save_ed_{rid}"):
                            update_entry(rid, new_date.strftime("%Y-%m-%d"), new_type, new_subject, new_content.strip(), new_detail.strip())
                            st.session_state.edit_id = None; st.success("✅ 已保存！"); st.rerun()
                    with bc2:
                        if st.button("❌ 取消", key=f"cancel_ed_{rid}"): st.session_state.edit_id = None; st.rerun()
                else:
                    st.markdown(f"**内容：** {row['content']}")
                    if row["detail"]: st.markdown(f"**掌握/原因：** {row['detail']}")
                    display_image(row["image_path"], "附件图片", 300)
                    st.caption(f"复习 {row['review_count']} 次 | 最近: {row['last_reviewed'] or '从未'}")
                    bc1, bc2, bc3, bc4 = st.columns(4)
                    with bc1:
                        if st.button("✏️ 编辑", key=f"edit_{rid}"): st.session_state.edit_id = rid; st.rerun()
                    with bc2:
                        if st.button("✅ 已复习", key=f"review_{rid}"): mark_reviewed(rid); st.success("已标记！"); st.rerun()
                    with bc3:
                        if st.button("🗑 删除", key=f"del_{rid}"): delete_entry(rid); st.success("已删除！"); st.rerun()
        st.markdown("---")
        ec1, ec2 = st.columns(2)
        with ec1:
            excel_data = export_df(filtered[["date","type","subject","content","detail","review_count","last_reviewed"]])
            st.download_button("📥 导出 Excel", excel_data, "学习记录导出.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with ec2:
            csv_data = filtered[["date","type","subject","content","detail"]].to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 导出 CSV", csv_data, "学习记录导出.csv", "text/csv", use_container_width=True)


# ══ TAB 4: Photo Capture ══
with tabs[3]:
    st.markdown("""
    <style>
        .photo-step-row { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 1.5rem; }
        .photo-step-dot { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 1rem; font-weight: 700; background: #e2e8f0; color: #94a3b8; transition: all 0.3s ease; }
        .photo-step-dot.active { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; box-shadow: 0 2px 8px rgba(99,102,241,0.4); }
        .photo-step-dot.done { background: #10b981; color: white; }
        .photo-step-line { flex: 1; height: 2px; max-width: 40px; background: #e2e8f0; border-radius: 2px; }
        .photo-step-line.active { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
        .photo-step-line.done { background: #10b981; }
        .photo-step-label { font-size: 0.7rem; color: #94a3b8; text-align: center; font-weight: 500; margin-top: 2px; }
        .photo-step-label.active { color: #6366f1; font-weight: 700; }
        .photo-step-label.done { color: #10b981; }
        .photo-camera-card {
            background: linear-gradient(135deg, #f8faff 0%, #eef2ff 100%);
            border: 2px dashed #c7d2fe; border-radius: 20px; padding: 1.5rem;
            text-align: center; transition: all 0.3s ease;
        }
        .photo-camera-card:hover { border-color: #818cf8; box-shadow: 0 4px 20px rgba(99,102,241,0.08); }
        .photo-camera-icon { font-size: 3rem; margin-bottom: 0.5rem; }
        .photo-camera-title { font-size: 1.1rem; font-weight: 700; color: #6366f1; margin-bottom: 0.3rem; }
        .photo-camera-hint { font-size: 0.8rem; color: #94a3b8; }
        .photo-preview-frame {
            border-radius: 16px; overflow: hidden; border: 3px solid white;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
            margin-bottom: 1rem;
        }
        .photo-save-card {
            background: white; border-radius: 16px; padding: 1.5rem;
            border: 1px solid #e8ecf1; box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }
    </style>
    """, unsafe_allow_html=True)

    # Step indicator
    has_photo = st.session_state.photo_b64 is not None
    step1 = "active" if not has_photo else "done"
    step2 = "active" if has_photo else ""
    st.markdown(f"""
    <div class="photo-step-row">
        <div style="text-align:center">
            <div class="photo-step-dot {step1}">📸</div>
            <div class="photo-step-label {step1}">拍照</div>
        </div>
        <div class="photo-step-line {step1}"></div>
        <div style="text-align:center">
            <div class="photo-step-dot {step2}">💾</div>
            <div class="photo-step-label {step2}">保存</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    capture_method = st.radio("", ["📸 直接拍照", "🖼 从相册选择"], horizontal=True, key="capture_method", label_visibility="collapsed")

    img_bytes = None
    if capture_method == "📸 直接拍照":
        st.markdown("""
        <div class="photo-camera-card">
            <div class="photo-camera-icon">📸</div>
            <div class="photo-camera-title">对准错题，点击下方拍照</div>
            <div class="photo-camera-hint">确保题目清晰可见，光线充足</div>
        </div>
        """, unsafe_allow_html=True)
        img_bytes = st.camera_input("", key="camera_input", label_visibility="collapsed")
    else:
        st.markdown("""
        <div class="photo-camera-card">
            <div class="photo-camera-icon">🖼</div>
            <div class="photo-camera-title">从相册选择错题照片</div>
            <div class="photo-camera-hint">支持 PNG / JPG / WebP 格式</div>
        </div>
        """, unsafe_allow_html=True)
        img_bytes = st.file_uploader("", type=["png", "jpg", "jpeg", "webp"], key="file_upload", label_visibility="collapsed")

    if img_bytes:
        raw_bytes = img_bytes.getvalue() if hasattr(img_bytes, "getvalue") else img_bytes.read()
        st.session_state.photo_b64 = base64.b64encode(raw_bytes).decode("utf-8")
        st.markdown('<div class="photo-preview-frame">', unsafe_allow_html=True)
        st.image(raw_bytes, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.photo_b64:
        st.markdown('<div class="photo-save-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 错题信息")
        sc1, sc2 = st.columns(2)
        with sc1: photo_subject = st.selectbox("科目", ["数学", "英语", "语文", "物理", "化学", "生物", "历史", "地理", "政治", "其他"], key="photo_subject")
        with sc2: photo_reason = st.text_input("错误原因", placeholder="计算失误、概念不清...", key="photo_reason")
        photo_desc = st.text_area("题目描述（可选）", placeholder="简要描述这道错题，方便日后复习...", height=70, key="photo_desc")
        bc1, bc2, bc3 = st.columns([2, 1, 1])
        with bc1:
            if st.button("💾 保存错题", use_container_width=True, key="save_photo", type="primary"):
                try:
                    conn = get_conn()
                    conn.execute("INSERT INTO entries (date,type,subject,content,detail,image_path) VALUES (?,?,?,?,?,?)",
                                 (datetime.date.today().strftime("%Y-%m-%d"), "错题", photo_subject,
                                  photo_desc.strip() or "（拍照错题）", photo_reason.strip(), st.session_state.photo_b64))
                    conn.commit(); conn.close()
                    st.success("✅ 错题照片已保存！")
                    st.session_state.photo_b64 = None
                    st.rerun()
                except Exception as e:
                    st.error(f"保存失败: {e}")
        with bc3:
            if st.button("❌ 取消", key="cancel_photo", use_container_width=True): st.session_state.photo_b64 = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══ TAB 5: Review ══
with tabs[4]:
    st.subheader("📋 智能复习")
    df = get_all_entries()
    if df.empty:
        st.info("还没有数据")
    else:
        r1, r2, r3 = st.columns(3)
        with r1: review_type = st.selectbox("类型", ["全部", "知识点", "错题"], key="review_type")
        with r2: review_subject = st.selectbox("科目", ["全部"] + sorted(df["subject"].unique().tolist()), key="review_subject")
        with r3: sort_method = st.selectbox("排序", ["最少复习优先", "最久未复习优先", "随机"], key="review_sort")
        review_df = df.copy()
        if review_type != "全部": review_df = review_df[review_df["type"] == review_type]
        if review_subject != "全部": review_df = review_df[review_df["subject"] == review_subject]
        if sort_method == "最少复习优先": review_df = review_df.sort_values(["review_count", "last_reviewed"])
        elif sort_method == "最久未复习优先":
            review_df["_sort"] = review_df["last_reviewed"].apply(lambda d: d if d and d != "" else "2000-01-01")
            review_df = review_df.sort_values("_sort")
        else: review_df = review_df.sample(frac=1)
        if review_df.empty: st.info("没有符合条件的记录")
        else:
            if "review_index" not in st.session_state: st.session_state.review_index = 0
            if "reveal" not in st.session_state: st.session_state.reveal = False
            total_review = len(review_df)
            idx = st.session_state.review_index % total_review
            st.progress((idx + 1) / total_review, f"第 {idx+1} / {total_review} 条")
            row = review_df.iloc[idx]
            with st.container(border=True):
                st.markdown(f"### #{row['id']} | {row['type']} | {row['subject']}")
                st.markdown(f"**日期：** {row['date']}")
                st.markdown("---")
                st.markdown(f"**内容：**\n> {row['content']}")
                rev_col1, rev_col2, rev_col3 = st.columns(3)
                with rev_col1:
                    if st.button("👁 显示答案", use_container_width=True, key=f"reveal_btn_{idx}"): st.session_state.reveal = True; st.rerun()
                with rev_col2:
                    if st.button("✅ 已掌握", use_container_width=True, key=f"mastered_{idx}"):
                        mark_reviewed(row["id"]); st.session_state.review_index += 1; st.session_state.reveal = False; st.rerun()
                with rev_col3:
                    if st.button("⏭ 跳过", use_container_width=True, key=f"skip_{idx}"):
                        st.session_state.review_index += 1; st.session_state.reveal = False; st.rerun()
                if st.session_state.reveal:
                    st.markdown("---")
                    label = "掌握程度" if row["type"] == "知识点" else "错误原因分析"
                    st.markdown(f"**{label}：**")
                    st.info(row["detail"] or "（未记录）")
                    display_image(row["image_path"], "", 300)
                    st.caption(f"已复习 {row['review_count']} 次 | 最近: {row['last_reviewed'] or '从未'}")
            nav1, _, nav3 = st.columns([1, 2, 1])
            with nav1:
                if st.button("⬅ 上一条", disabled=(idx == 0), use_container_width=True): st.session_state.review_index -= 1; st.session_state.reveal = False; st.rerun()
            with nav3:
                if st.button("下一条 ➡", disabled=(idx == total_review - 1), use_container_width=True): st.session_state.review_index += 1; st.session_state.reveal = False; st.rerun()
            if st.button("🔄 重新开始", use_container_width=True): st.session_state.review_index = 0; st.session_state.reveal = False; st.rerun()
