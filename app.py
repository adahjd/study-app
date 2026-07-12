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

# ── Page config ──
st.set_page_config(
    page_title="个人知识与错题库",
    page_icon="📚",
    layout="wide",
)

# ── Custom CSS + PWA meta injection ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header { font-size: 2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0; }
    .sub-header { font-size: 0.9rem; color: #6b7280; margin-top: -0.5rem; margin-bottom: 1rem; }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px; padding: 1.2rem; color: white;
        text-align: center; box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    .stat-card.green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); box-shadow: 0 4px 15px rgba(17,153,142,0.3); }
    .stat-card.orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 4px 15px rgba(240,147,251,0.3); }
    .stat-card.blue { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); box-shadow: 0 4px 15px rgba(79,172,254,0.3); }
    .stat-value { font-size: 2rem; font-weight: 700; }
    .stat-label { font-size: 0.85rem; opacity: 0.9; }
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    .stButton > button {
        border-radius: 8px !important; font-weight: 600 !important;
        transition: all 0.2s !important; border: none !important;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important; }

    /* ── Mobile responsive ── */
    @media (max-width: 768px) {
        .main-header { font-size: 1.3rem !important; }
        .sub-header { font-size: 0.75rem !important; }
        .stat-card { padding: 0.8rem !important; }
        .stat-value { font-size: 1.4rem !important; }
        .stat-label { font-size: 0.7rem !important; }
        .stButton > button {
            font-size: 0.9rem !important;
            padding: 0.7rem 0.5rem !important;
            min-height: 44px !important;
        }
        section[data-testid="stSidebar"] { display: none !important; }
        .stTabs [role="tab"] { font-size: 0.75rem !important; padding: 0.5rem 0.4rem !important; }
    }

    @media (max-width: 480px) {
        .main-header { font-size: 1.1rem !important; }
        .stat-value { font-size: 1.2rem !important; }
        .stTabs [role="tab"] { font-size: 0.65rem !important; padding: 0.4rem 0.25rem !important; }
    }
</style>

""", unsafe_allow_html=True)

# ── Database setup ──
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_data.db")
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(IMAGE_DIR, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            detail TEXT DEFAULT '',
            image_path TEXT DEFAULT '',
            review_count INTEGER DEFAULT 0,
            last_reviewed TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ── DB helpers ──
def get_conn():
    return sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)


def add_entry(date, entry_type, subject, content, detail, image_path=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO entries (date, type, subject, content, detail, image_path) VALUES (?,?,?,?,?,?)",
        (date, entry_type, subject, content, detail, image_path),
    )
    conn.commit()
    conn.close()


def update_entry(entry_id, date, entry_type, subject, content, detail):
    conn = get_conn()
    conn.execute(
        "UPDATE entries SET date=?, type=?, subject=?, content=?, detail=? WHERE id=?",
        (date, entry_type, subject, content, detail, entry_id),
    )
    conn.commit()
    conn.close()


def delete_entry(entry_id):
    conn = get_conn()
    row = conn.execute("SELECT image_path FROM entries WHERE id=?", (entry_id,)).fetchone()
    if row and row[0] and os.path.exists(row[0]):
        os.remove(row[0])
    conn.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()


def mark_reviewed(entry_id):
    conn = get_conn()
    today = datetime.date.today().strftime("%Y-%m-%d")
    conn.execute(
        "UPDATE entries SET review_count = review_count + 1, last_reviewed = ? WHERE id = ?",
        (today, entry_id),
    )
    conn.commit()
    conn.close()


def get_all_entries():
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT id, date, type, subject, content, detail, image_path, review_count, last_reviewed FROM entries ORDER BY id DESC",
        conn,
    )
    conn.close()
    return df


def get_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    knowledge = conn.execute("SELECT COUNT(*) FROM entries WHERE type='知识点'").fetchone()[0]
    error = conn.execute("SELECT COUNT(*) FROM entries WHERE type='错题'").fetchone()[0]
    subject_counts = pd.read_sql_query(
        "SELECT subject, COUNT(*) as cnt FROM entries GROUP BY subject", conn
    )
    detail_counts = pd.read_sql_query(
        "SELECT detail, COUNT(*) as cnt FROM entries WHERE detail != '' GROUP BY detail", conn
    )
    recent = pd.read_sql_query(
        "SELECT date, COUNT(*) as cnt FROM entries GROUP BY date ORDER BY date DESC LIMIT 14", conn
    )
    conn.close()
    return {
        "total": total,
        "knowledge": knowledge,
        "error": error,
        "subject_counts": subject_counts,
        "detail_counts": detail_counts,
        "recent": recent,
    }


def export_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="学习记录")
    return output.getvalue()


# ── Session state init ──
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "tab" not in st.session_state:
    st.session_state.tab = "📊 数据看板"


# ── Header ──
st.markdown('<p class="main-header">📚 个人知识与错题管理系统</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">记录 · 复习 · 掌握 · 成长</p>', unsafe_allow_html=True)

# ── Tabs ──
tab_labels = ["📊 看板", "📝 添加", "🔍 管理", "📷 拍照", "📋 复习"]
tabs = st.tabs(tab_labels)

# ═══════════════════════════════════════
# TAB 1: Dashboard
# ═══════════════════════════════════════
with tabs[0]:
    stats = get_stats()

    if stats["total"] == 0:
        st.info("👋 欢迎！目前还没有数据，先去「添加」或「拍照」开始吧！")
    else:
        # Stats cards — use 2 cols on mobile via container queries handled by Streamlit auto-wrap
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f'<div class="stat-card"><div class="stat-value">{stats["total"]}</div><div class="stat-label">总记录</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="stat-card green"><div class="stat-value">{stats["knowledge"]}</div><div class="stat-label">知识点</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="stat-card orange"><div class="stat-value">{stats["error"]}</div><div class="stat-label">错题</div></div>',
                unsafe_allow_html=True,
            )
        with c4:
            streak = len(stats["recent"]) if not stats["recent"].empty else 0
            st.markdown(
                f'<div class="stat-card blue"><div class="stat-value">{streak}</div><div class="stat-label">活跃天数</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Charts — stack on mobile
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📈 每日记录趋势")
            if not stats["recent"].empty:
                recent_df = stats["recent"].sort_values("date")
                fig = px.line(
                    recent_df, x="date", y="cnt", markers=True,
                    labels={"date": "日期", "cnt": "记录数"},
                )
                fig.update_traces(line_color="#667eea", marker=dict(size=8, color="#764ba2"))
                fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无数据")

        with col_right:
            st.subheader("🗂 科目分布")
            if not stats["subject_counts"].empty:
                fig = px.pie(
                    stats["subject_counts"], names="subject", values="cnt",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.4,
                )
                fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无数据")

        st.markdown("---")

        st.subheader("🎯 掌握程度 / 错误原因分布")
        if not stats["detail_counts"].empty:
            top_details = stats["detail_counts"].sort_values("cnt", ascending=False).head(10)
            fig = px.bar(
                top_details, x="detail", y="cnt",
                labels={"detail": "标签", "cnt": "数量"},
                color="cnt", color_continuous_scale="Viridis",
            )
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据")


# ═══════════════════════════════════════
# TAB 2: Add Entry
# ═══════════════════════════════════════
with tabs[1]:
    st.subheader("✏️ 记录新内容")

    if st.session_state.edit_id:
        st.warning(f"⚠️ 正在编辑记录 #{st.session_state.edit_id}，请先完成或取消编辑")
        if st.button("❌ 取消编辑", key="cancel_edit_add"):
            st.session_state.edit_id = None
            st.rerun()
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            data_type = st.selectbox("类型", ["知识点", "错题"], key="add_type")
        with col2:
            subject = st.selectbox("科目", ["数学", "英语", "语文", "物理", "化学", "生物", "历史", "地理", "政治", "其他"], key="add_subject")
        with col3:
            entry_date = st.date_input("日期", datetime.date.today(), key="add_date")

        content = st.text_area(
            "内容描述",
            placeholder="知识点：写下你要记住的内容...\n错题：粘贴题目或描述错误...",
            height=150,
            key="add_content",
        )

        if data_type == "知识点":
            detail_label = "掌握程度"
            detail_placeholder = "例如：已掌握、基本理解、需复习、完全不会"
        else:
            detail_label = "错误原因分析"
            detail_placeholder = "例如：计算失误、概念不清、审题错误、公式记错"
        detail = st.text_input(detail_label, placeholder=detail_placeholder, key="add_detail")

        if st.button("💾 保存到库", use_container_width=True, key="save_entry"):
            if not content.strip():
                st.error("内容描述不能为空！")
            else:
                add_entry(
                    entry_date.strftime("%Y-%m-%d"),
                    data_type,
                    subject,
                    content.strip(),
                    detail.strip(),
                )
                st.success(f"✅ 成功保存一条【{data_type}】！")
                st.rerun()


# ═══════════════════════════════════════
# TAB 3: Browse & Manage
# ═══════════════════════════════════════
with tabs[2]:
    st.subheader("🔍 浏览 & 管理")

    df = get_all_entries()

    if df.empty:
        st.info("📭 库里还没有数据，去添加一些吧！")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            filter_type = st.selectbox("类型筛选", ["全部", "知识点", "错题"], key="browse_type")
        with f2:
            all_subjects = sorted(df["subject"].unique())
            filter_subject = st.multiselect("科目筛选", all_subjects, default=all_subjects, key="browse_subject")
        with f3:
            search_term = st.text_input("🔎 搜索", placeholder="输入关键词...", key="browse_search")

        filtered = df.copy()
        if filter_type != "全部":
            filtered = filtered[filtered["type"] == filter_type]
        if filter_subject:
            filtered = filtered[filtered["subject"].isin(filter_subject)]
        if search_term:
            filtered = filtered[
                filtered["content"].str.contains(search_term, case=False, na=False)
                | filtered["detail"].str.contains(search_term, case=False, na=False)
            ]

        st.caption(f"共 {len(filtered)} 条记录")

        for i, row in filtered.iterrows():
            rid = row["id"]
            preview = row["content"][:50].replace("\n", " ")
            with st.expander(f"#{rid} | {row['date']} | {row['type']} | {row['subject']} | {preview}...", expanded=(st.session_state.edit_id == rid)):
                if st.session_state.edit_id == rid:
                    subjects_list = ["数学", "英语", "语文", "物理", "化学", "生物", "历史", "地理", "政治", "其他"]
                    subj_idx = subjects_list.index(row["subject"]) if row["subject"] in subjects_list else 0
                    e1, e2, e3 = st.columns(3)
                    with e1:
                        new_type = st.selectbox("类型", ["知识点", "错题"], index=0 if row["type"] == "知识点" else 1, key=f"ed_type_{rid}")
                    with e2:
                        new_subject = st.selectbox("科目", subjects_list, index=subj_idx, key=f"ed_subject_{rid}")
                    with e3:
                        new_date = st.date_input("日期", datetime.datetime.strptime(row["date"], "%Y-%m-%d").date(), key=f"ed_date_{rid}")
                    new_content = st.text_area("内容", value=row["content"], height=120, key=f"ed_content_{rid}")
                    new_detail = st.text_input("掌握程度/错误原因", value=row["detail"] if row["detail"] else "", key=f"ed_detail_{rid}")

                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("💾 保存修改", key=f"save_ed_{rid}"):
                            update_entry(rid, new_date.strftime("%Y-%m-%d"), new_type, new_subject, new_content.strip(), new_detail.strip())
                            st.session_state.edit_id = None
                            st.success("✅ 修改已保存！")
                            st.rerun()
                    with bc2:
                        if st.button("❌ 取消", key=f"cancel_ed_{rid}"):
                            st.session_state.edit_id = None
                            st.rerun()

                    if st.button("🗑 删除", key=f"del_ed_{rid}", type="secondary"):
                        delete_entry(rid)
                        st.session_state.edit_id = None
                        st.success("🗑 已删除！")
                        st.rerun()
                else:
                    st.markdown(f"**内容：** {row['content']}")
                    if row["detail"]:
                        st.markdown(f"**掌握程度/错误原因：** {row['detail']}")
                    if row["image_path"] and os.path.exists(row["image_path"]):
                        st.image(row["image_path"], caption="附件图片", width=300)
                    st.caption(f"复习 {row['review_count']} 次 | 最近复习: {row['last_reviewed'] or '从未'}")

                    bc1, bc2, bc3 = st.columns(3)
                    with bc1:
                        if st.button("✏️ 编辑", key=f"edit_{rid}"):
                            st.session_state.edit_id = rid
                            st.rerun()
                    with bc2:
                        if st.button("✅ 已复习", key=f"review_{rid}"):
                            mark_reviewed(rid)
                            st.success("已标记复习！")
                            st.rerun()
                    with bc3:
                        if st.button("🗑 删除", key=f"del_{rid}"):
                            delete_entry(rid)
                            st.success("已删除！")
                            st.rerun()

        st.markdown("---")
        ec1, ec2 = st.columns(2)
        with ec1:
            excel_data = export_df(filtered[["date", "type", "subject", "content", "detail", "review_count", "last_reviewed"]])
            st.download_button(
                "📥 导出 Excel", excel_data, "学习记录导出.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with ec2:
            csv_data = filtered[["date", "type", "subject", "content", "detail"]].to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 导出 CSV", csv_data, "学习记录导出.csv", "text/csv",
                use_container_width=True,
            )


# ═══════════════════════════════════════

# TAB 4: Photo Capture (camera + album)
# ═══════════════════════════════════════
with tabs[3]:
    st.subheader("📷 拍照收集错题")
    st.caption("拍照或从相册选择，直接保存照片")

    capture_method = st.radio(
        "选择方式",
        ["📸 直接拍照", "🖼 从相册选择"],
        horizontal=True,
        key="capture_method",
    )

    img_bytes = None

    if capture_method == "📸 直接拍照":
        img_bytes = st.camera_input("对准错题拍照", key="camera_input", label_visibility="collapsed")
    else:
        img_bytes = st.file_uploader("从相册选择", type=["png", "jpg", "jpeg", "webp"], key="file_upload", label_visibility="collapsed")

    if img_bytes:
        # Read bytes first (avoid stream consumption issues)
        img_data = img_bytes.getvalue() if hasattr(img_bytes, "getvalue") else img_bytes.read()
        img_bytes.seek(0)  # Reset for Image.open
        uploaded_image = Image.open(img_bytes)
        st.image(uploaded_image, caption="预览", use_container_width=True)

        # Save raw bytes to disk (more reliable than PIL save)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        saved_path = os.path.join(IMAGE_DIR, f"photo_{timestamp}.png")
        with open(saved_path, "wb") as f:
            f.write(img_data)

        st.markdown("---")
        st.markdown("### 💾 保存为错题")

        sc1, sc2 = st.columns(2)
        with sc1:
            photo_subject = st.selectbox("科目", ["数学", "英语", "语文", "物理", "化学", "生物", "历史", "地理", "政治", "其他"], key="photo_subject")
        with sc2:
            photo_reason = st.text_input("错误原因分析", placeholder="例如：计算失误、概念不清...", key="photo_reason")

        photo_desc = st.text_area("题目描述（可选）", placeholder="简要描述这道错题...", height=80, key="photo_desc")

        if st.button("💾 保存错题", use_container_width=True, key="save_photo"):
            add_entry(
                datetime.date.today().strftime("%Y-%m-%d"),
                "错题",
                photo_subject,
                photo_desc.strip() or "（拍照错题）",
                photo_reason.strip(),
                saved_path,
            )
            st.success("✅ 错题照片已保存！")
            st.rerun()

# TAB 5: Review Mode
# ═══════════════════════════════════════
with tabs[4]:
    st.subheader("📋 智能复习")

    df = get_all_entries()

    if df.empty:
        st.info("还没有数据，先添加一些记录吧！")
    else:
        r1, r2, r3 = st.columns(3)
        with r1:
            review_type = st.selectbox("类型", ["全部", "知识点", "错题"], key="review_type")
        with r2:
            review_subject = st.selectbox("科目", ["全部"] + sorted(df["subject"].unique().tolist()), key="review_subject")
        with r3:
            sort_method = st.selectbox("排序", ["最少复习优先", "最久未复习优先", "随机"], key="review_sort")

        review_df = df.copy()
        if review_type != "全部":
            review_df = review_df[review_df["type"] == review_type]
        if review_subject != "全部":
            review_df = review_df[review_df["subject"] == review_subject]

        if sort_method == "最少复习优先":
            review_df = review_df.sort_values(["review_count", "last_reviewed"])
        elif sort_method == "最久未复习优先":
            def date_sort_key(d):
                return d if d and d != "" else "2000-01-01"
            review_df["_sort_date"] = review_df["last_reviewed"].apply(date_sort_key)
            review_df = review_df.sort_values("_sort_date")
        else:
            review_df = review_df.sample(frac=1)

        if review_df.empty:
            st.info("没有符合条件的记录")
        else:
            if "review_index" not in st.session_state:
                st.session_state.review_index = 0

            total_review = len(review_df)
            idx = st.session_state.review_index

            if idx >= total_review:
                st.session_state.review_index = 0
                idx = 0

            st.progress((idx + 1) / total_review, f"第 {idx+1} / {total_review} 条")

            row = review_df.iloc[idx]

            with st.container(border=True):
                st.markdown(f"### #{row['id']} | {row['type']} | {row['subject']}")
                st.markdown(f"**日期：** {row['date']}")
                st.markdown("---")
                st.markdown(f"**内容：**")
                st.markdown(f"> {row['content']}")

                if "reveal" not in st.session_state:
                    st.session_state.reveal = False

                rev_col1, rev_col2, rev_col3 = st.columns(3)
                with rev_col1:
                    if st.button("👁 显示答案", use_container_width=True, key=f"reveal_{idx}"):
                        st.session_state.reveal = True
                        st.rerun()
                with rev_col2:
                    if st.button("✅ 已掌握", use_container_width=True, key=f"mastered_{idx}"):
                        mark_reviewed(row["id"])
                        st.session_state.review_index += 1
                        st.session_state.reveal = False
                        st.rerun()
                with rev_col3:
                    if st.button("⏭ 跳过", use_container_width=True, key=f"skip_{idx}"):
                        st.session_state.review_index += 1
                        st.session_state.reveal = False
                        st.rerun()

                if st.session_state.reveal:
                    st.markdown("---")
                    label = "掌握程度" if row["type"] == "知识点" else "错误原因分析"
                    st.markdown(f"**{label}：**")
                    st.info(row["detail"] if row["detail"] else "（未记录）")
                    if row["image_path"] and os.path.exists(row["image_path"]):
                        st.image(row["image_path"], width=300)
                    st.caption(f"已复习 {row['review_count']} 次 | 最近: {row['last_reviewed'] or '从未'}")

            nav1, nav2, nav3 = st.columns([1, 2, 1])
            with nav1:
                if st.button("⬅ 上一条", disabled=(idx == 0), use_container_width=True):
                    st.session_state.review_index -= 1
                    st.session_state.reveal = False
                    st.rerun()
            with nav3:
                if st.button("下一条 ➡", disabled=(idx == total_review - 1), use_container_width=True):
                    st.session_state.review_index += 1
                    st.session_state.reveal = False
                    st.rerun()

            if st.button("🔄 重新开始", use_container_width=True):
                st.session_state.review_index = 0
                st.session_state.reveal = False
                st.rerun()
