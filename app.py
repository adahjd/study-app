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

# 鈹€鈹€ Page config 鈹€鈹€
st.set_page_config(
    page_title="涓汉鐭ヨ瘑涓庨敊棰樺簱",
    page_icon="馃摎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 鈹€鈹€ Custom CSS + PWA meta injection 鈹€鈹€
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

    /* 鈹€鈹€ Mobile responsive 鈹€鈹€ */
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

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="瀛︿範搴?>
<meta name="theme-color" content="#667eea">
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%23667eea'/><text x='50' y='68' font-size='52' text-anchor='middle'>馃摎</text></svg>">
<link rel="manifest" href="data:application/json;base64,ewogICJuYW1lIjogIuS4quS6uuefpeivhuS4jumUmeivlemFkyIsCiAgInNob3J0X25hbWUiOiAi5a2m5Lmg5bqTIiwKICAic3RhcnRfdXJsIjogIi4iLAogICJkaXNwbGF5IjogInN0YW5kYWxvbmUiLAogICJiYWNrZ3JvdW5kX2NvbG9yIjogIiNmOGY5ZmEiLAogICJ0aGVtZV9jb2xvciI6ICIjNjY3ZWVhIiwKICAiaWNvbnMiOiBbCiAgICB7CiAgICAgICJzcmMiOiAiZGF0YTppbWFnZS9zdmcreG1sLDxzdmcgeG1sbnM9J2h0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnJyB2aWV3Qm94PScwIDAgMTAwIDEwMCc+PHJlY3Qgd2lkdGg9JzEwMCcgaGVpZ2h0PScxMDAnIHJ4PScyMCcgZmlsbD0nIzY2N2VlYScvPjx0ZXh0IHg9JzUwJyB5PSc2OCcgZm9udC1zaXplPSc1MicgdGV4dC1hbmNob3I9J21pZGRsZSc+8J+TmjwvdGV4dD48L3N2Zz4iLAogICAgICAic2l6ZXMiOiAiMTkyeDE5MiIsCiAgICAgICJ0eXBlIjogImltYWdlL3N2Zyt4bWwiCiAgICB9CiAgXQp9">

<script>
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        const swCode = `
            const CACHE = 'study-v1';
            self.addEventListener('install', e => { self.skipWaiting(); });
            self.addEventListener('activate', e => { e.waitUntil(clients.claim()); });
            self.addEventListener('fetch', e => {
                e.respondWith(
                    caches.match(e.request).then(r => r || fetch(e.request).then(resp => {
                        if (resp.ok) { const clone = resp.clone(); caches.open(CACHE).then(c => c.put(e.request, clone)); }
                        return resp;
                    }))
                );
            });
        `;
        const blob = new Blob([swCode], {type: 'application/javascript'});
        navigator.serviceWorker.register(URL.createObjectURL(blob));
    });
}
</script>
""", unsafe_allow_html=True)

# 鈹€鈹€ Database setup 鈹€鈹€
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


# 鈹€鈹€ DB helpers 鈹€鈹€
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
    knowledge = conn.execute("SELECT COUNT(*) FROM entries WHERE type='鐭ヨ瘑鐐?").fetchone()[0]
    error = conn.execute("SELECT COUNT(*) FROM entries WHERE type='閿欓'").fetchone()[0]
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
        df.to_excel(writer, index=False, sheet_name="瀛︿範璁板綍")
    return output.getvalue()


# 鈹€鈹€ OCR helper 鈹€鈹€
def run_ocr(image: Image.Image) -> str:
    """Run EasyOCR on an image. Returns recognized text or raises."""
    import easyocr

    temp_path = os.path.join(IMAGE_DIR, f"temp_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png")
    image.save(temp_path)

    reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
    results = reader.readtext(temp_path)
    recognized_text = "\n".join([r[1] for r in results])

    if not recognized_text.strip():
        raise ValueError("鏈瘑鍒埌鏂囧瓧锛岃纭繚鍥剧墖娓呮櫚涓斿寘鍚枃瀛楀唴瀹?)

    return recognized_text, temp_path


# 鈹€鈹€ Session state init 鈹€鈹€
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "tab" not in st.session_state:
    st.session_state.tab = "馃搳 鏁版嵁鐪嬫澘"


# 鈹€鈹€ Header 鈹€鈹€
st.markdown('<p class="main-header">馃摎 涓汉鐭ヨ瘑涓庨敊棰樼鐞嗙郴缁?/p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">璁板綍 路 澶嶄範 路 鎺屾彙 路 鎴愰暱</p>', unsafe_allow_html=True)

# 鈹€鈹€ Tabs 鈹€鈹€
tab_labels = ["馃搳 鐪嬫澘", "馃摑 娣诲姞", "馃攳 绠＄悊", "馃摲 鎷嶇収", "馃搵 澶嶄範"]
tabs = st.tabs(tab_labels)

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# TAB 1: Dashboard
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?with tabs[0]:
    stats = get_stats()

    if stats["total"] == 0:
        st.info("馃憢 娆㈣繋锛佺洰鍓嶈繕娌℃湁鏁版嵁锛屽厛鍘汇€屾坊鍔犮€嶆垨銆屾媿鐓с€嶅紑濮嬪惂锛?)
    else:
        # Stats cards 鈥?use 2 cols on mobile via container queries handled by Streamlit auto-wrap
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f'<div class="stat-card"><div class="stat-value">{stats["total"]}</div><div class="stat-label">鎬昏褰?/div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="stat-card green"><div class="stat-value">{stats["knowledge"]}</div><div class="stat-label">鐭ヨ瘑鐐?/div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="stat-card orange"><div class="stat-value">{stats["error"]}</div><div class="stat-label">閿欓</div></div>',
                unsafe_allow_html=True,
            )
        with c4:
            streak = len(stats["recent"]) if not stats["recent"].empty else 0
            st.markdown(
                f'<div class="stat-card blue"><div class="stat-value">{streak}</div><div class="stat-label">娲昏穬澶╂暟</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Charts 鈥?stack on mobile
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("馃搱 姣忔棩璁板綍瓒嬪娍")
            if not stats["recent"].empty:
                recent_df = stats["recent"].sort_values("date")
                fig = px.line(
                    recent_df, x="date", y="cnt", markers=True,
                    labels={"date": "鏃ユ湡", "cnt": "璁板綍鏁?},
                )
                fig.update_traces(line_color="#667eea", marker=dict(size=8, color="#764ba2"))
                fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("鏆傛棤鏁版嵁")

        with col_right:
            st.subheader("馃梻 绉戠洰鍒嗗竷")
            if not stats["subject_counts"].empty:
                fig = px.pie(
                    stats["subject_counts"], names="subject", values="cnt",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.4,
                )
                fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("鏆傛棤鏁版嵁")

        st.markdown("---")

        st.subheader("馃幆 鎺屾彙绋嬪害 / 閿欒鍘熷洜鍒嗗竷")
        if not stats["detail_counts"].empty:
            top_details = stats["detail_counts"].sort_values("cnt", ascending=False).head(10)
            fig = px.bar(
                top_details, x="detail", y="cnt",
                labels={"detail": "鏍囩", "cnt": "鏁伴噺"},
                color="cnt", color_continuous_scale="Viridis",
            )
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("鏆傛棤鏁版嵁")


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# TAB 2: Add Entry
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?with tabs[1]:
    st.subheader("鉁忥笍 璁板綍鏂板唴瀹?)

    if st.session_state.edit_id:
        st.warning(f"鈿狅笍 姝ｅ湪缂栬緫璁板綍 #{st.session_state.edit_id}锛岃鍏堝畬鎴愭垨鍙栨秷缂栬緫")
        if st.button("鉂?鍙栨秷缂栬緫", key="cancel_edit_add"):
            st.session_state.edit_id = None
            st.rerun()
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            data_type = st.selectbox("绫诲瀷", ["鐭ヨ瘑鐐?, "閿欓"], key="add_type")
        with col2:
            subject = st.selectbox("绉戠洰", ["鏁板", "鑻辫", "璇枃", "鐗╃悊", "鍖栧", "鐢熺墿", "鍘嗗彶", "鍦扮悊", "鏀挎不", "鍏朵粬"], key="add_subject")
        with col3:
            entry_date = st.date_input("鏃ユ湡", datetime.date.today(), key="add_date")

        content = st.text_area(
            "鍐呭鎻忚堪",
            placeholder="鐭ヨ瘑鐐癸細鍐欎笅浣犺璁颁綇鐨勫唴瀹?..\n閿欓锛氱矘璐撮鐩垨鎻忚堪閿欒...",
            height=150,
            key="add_content",
        )

        if data_type == "鐭ヨ瘑鐐?:
            detail_label = "鎺屾彙绋嬪害"
            detail_placeholder = "渚嬪锛氬凡鎺屾彙銆佸熀鏈悊瑙ｃ€侀渶澶嶄範銆佸畬鍏ㄤ笉浼?
        else:
            detail_label = "閿欒鍘熷洜鍒嗘瀽"
            detail_placeholder = "渚嬪锛氳绠楀け璇€佹蹇典笉娓呫€佸棰橀敊璇€佸叕寮忚閿?
        detail = st.text_input(detail_label, placeholder=detail_placeholder, key="add_detail")

        if st.button("馃捑 淇濆瓨鍒板簱", use_container_width=True, key="save_entry"):
            if not content.strip():
                st.error("鍐呭鎻忚堪涓嶈兘涓虹┖锛?)
            else:
                add_entry(
                    entry_date.strftime("%Y-%m-%d"),
                    data_type,
                    subject,
                    content.strip(),
                    detail.strip(),
                )
                st.success(f"鉁?鎴愬姛淇濆瓨涓€鏉°€恵data_type}銆戯紒")
                st.rerun()


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# TAB 3: Browse & Manage
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?with tabs[2]:
    st.subheader("馃攳 娴忚 & 绠＄悊")

    df = get_all_entries()

    if df.empty:
        st.info("馃摥 搴撻噷杩樻病鏈夋暟鎹紝鍘绘坊鍔犱竴浜涘惂锛?)
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            filter_type = st.selectbox("绫诲瀷绛涢€?, ["鍏ㄩ儴", "鐭ヨ瘑鐐?, "閿欓"], key="browse_type")
        with f2:
            all_subjects = sorted(df["subject"].unique())
            filter_subject = st.multiselect("绉戠洰绛涢€?, all_subjects, default=all_subjects, key="browse_subject")
        with f3:
            search_term = st.text_input("馃攷 鎼滅储", placeholder="杈撳叆鍏抽敭璇?..", key="browse_search")

        filtered = df.copy()
        if filter_type != "鍏ㄩ儴":
            filtered = filtered[filtered["type"] == filter_type]
        if filter_subject:
            filtered = filtered[filtered["subject"].isin(filter_subject)]
        if search_term:
            filtered = filtered[
                filtered["content"].str.contains(search_term, case=False, na=False)
                | filtered["detail"].str.contains(search_term, case=False, na=False)
            ]

        st.caption(f"鍏?{len(filtered)} 鏉¤褰?)

        for i, row in filtered.iterrows():
            rid = row["id"]
            preview = row["content"][:50].replace("\n", " ")
            with st.expander(f"#{rid} | {row['date']} | {row['type']} | {row['subject']} | {preview}...", expanded=(st.session_state.edit_id == rid)):
                if st.session_state.edit_id == rid:
                    subjects_list = ["鏁板", "鑻辫", "璇枃", "鐗╃悊", "鍖栧", "鐢熺墿", "鍘嗗彶", "鍦扮悊", "鏀挎不", "鍏朵粬"]
                    subj_idx = subjects_list.index(row["subject"]) if row["subject"] in subjects_list else 0
                    e1, e2, e3 = st.columns(3)
                    with e1:
                        new_type = st.selectbox("绫诲瀷", ["鐭ヨ瘑鐐?, "閿欓"], index=0 if row["type"] == "鐭ヨ瘑鐐? else 1, key=f"ed_type_{rid}")
                    with e2:
                        new_subject = st.selectbox("绉戠洰", subjects_list, index=subj_idx, key=f"ed_subject_{rid}")
                    with e3:
                        new_date = st.date_input("鏃ユ湡", datetime.datetime.strptime(row["date"], "%Y-%m-%d").date(), key=f"ed_date_{rid}")
                    new_content = st.text_area("鍐呭", value=row["content"], height=120, key=f"ed_content_{rid}")
                    new_detail = st.text_input("鎺屾彙绋嬪害/閿欒鍘熷洜", value=row["detail"] if row["detail"] else "", key=f"ed_detail_{rid}")

                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("馃捑 淇濆瓨淇敼", key=f"save_ed_{rid}"):
                            update_entry(rid, new_date.strftime("%Y-%m-%d"), new_type, new_subject, new_content.strip(), new_detail.strip())
                            st.session_state.edit_id = None
                            st.success("鉁?淇敼宸蹭繚瀛橈紒")
                            st.rerun()
                    with bc2:
                        if st.button("鉂?鍙栨秷", key=f"cancel_ed_{rid}"):
                            st.session_state.edit_id = None
                            st.rerun()

                    if st.button("馃棏 鍒犻櫎", key=f"del_ed_{rid}", type="secondary"):
                        delete_entry(rid)
                        st.session_state.edit_id = None
                        st.success("馃棏 宸插垹闄わ紒")
                        st.rerun()
                else:
                    st.markdown(f"**鍐呭锛?* {row['content']}")
                    if row["detail"]:
                        st.markdown(f"**鎺屾彙绋嬪害/閿欒鍘熷洜锛?* {row['detail']}")
                    if row["image_path"] and os.path.exists(row["image_path"]):
                        st.image(row["image_path"], caption="闄勪欢鍥剧墖", width=300)
                    st.caption(f"澶嶄範 {row['review_count']} 娆?| 鏈€杩戝涔? {row['last_reviewed'] or '浠庢湭'}")

                    bc1, bc2, bc3 = st.columns(3)
                    with bc1:
                        if st.button("鉁忥笍 缂栬緫", key=f"edit_{rid}"):
                            st.session_state.edit_id = rid
                            st.rerun()
                    with bc2:
                        if st.button("鉁?宸插涔?, key=f"review_{rid}"):
                            mark_reviewed(rid)
                            st.success("宸叉爣璁板涔狅紒")
                            st.rerun()
                    with bc3:
                        if st.button("馃棏 鍒犻櫎", key=f"del_{rid}"):
                            delete_entry(rid)
                            st.success("宸插垹闄わ紒")
                            st.rerun()

        st.markdown("---")
        ec1, ec2 = st.columns(2)
        with ec1:
            excel_data = export_df(filtered[["date", "type", "subject", "content", "detail", "review_count", "last_reviewed"]])
            st.download_button(
                "馃摜 瀵煎嚭 Excel", excel_data, "瀛︿範璁板綍瀵煎嚭.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with ec2:
            csv_data = filtered[["date", "type", "subject", "content", "detail"]].to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "馃摜 瀵煎嚭 CSV", csv_data, "瀛︿範璁板綍瀵煎嚭.csv", "text/csv",
                use_container_width=True,
            )


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# TAB 4: Photo Capture (camera + album)
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?with tabs[3]:
    st.subheader("馃摲 鎷嶇収鏀堕泦閿欓")
    st.caption("鐢ㄧ浉鏈烘媿鐓ф垨浠庣浉鍐岄€夋嫨锛岃嚜鍔ㄨ瘑鍒枃瀛?)

    # Two options: camera or album
    capture_method = st.radio(
        "閫夋嫨鏂瑰紡",
        ["馃摳 鐩存帴鎷嶇収", "馃柤 浠庣浉鍐岄€夋嫨"],
        horizontal=True,
        key="capture_method",
    )

    uploaded_image = None

    if capture_method == "馃摳 鐩存帴鎷嶇収":
        camera_img = st.camera_input("瀵瑰噯閿欓鎷嶇収", key="camera_input", label_visibility="collapsed")
        if camera_img:
            uploaded_image = Image.open(camera_img)
            st.image(uploaded_image, caption="鎷嶆憚鐨勭収鐗?, use_container_width=True)
    else:
        file_img = st.file_uploader("浠庣浉鍐岄€夋嫨", type=["png", "jpg", "jpeg", "webp"], key="file_upload", label_visibility="collapsed")
        if file_img:
            uploaded_image = Image.open(file_img)
            st.image(uploaded_image, caption="閫夋嫨鐨勫浘鐗?, use_container_width=True)

    # OCR section 鈥?shared by both inputs
    if uploaded_image:
        if st.button("馃攳 寮€濮嬭瘑鍒枃瀛?, use_container_width=True, key="run_ocr"):
            with st.spinner("鈴?姝ｅ湪鍔犺浇 OCR 寮曟搸锛堥娆′娇鐢ㄩ渶涓嬭浇妯″瀷锛岀害闇€ 1-2 鍒嗛挓锛?.."):
                try:
                    recognized_text, saved_path = run_ocr(uploaded_image)
                    st.session_state.ocr_text = recognized_text
                    st.session_state.ocr_image_path = saved_path
                    st.success(f"鉁?璇嗗埆鎴愬姛锛?)
                    st.text_area("璇嗗埆鍐呭", recognized_text, height=200, key="ocr_result_display")
                except ValueError as e:
                    st.warning(f"鈿狅笍 {e}")
                    st.session_state.ocr_text = ""
                    st.session_state.ocr_image_path = ""
                except Exception as e:
                    err_msg = str(e)
                    if "Downloading" in err_msg or "download" in err_msg.lower():
                        st.error("馃寪 OCR 妯″瀷涓嬭浇澶辫触锛岃妫€鏌ョ綉缁滆繛鎺ュ悗閲嶈瘯銆傚鏋滃湪 Streamlit Cloud 涓婏紝鍐峰惎鍔ㄦ椂涓嬭浇鍙兘瓒呮椂锛岃绋嶇瓑鐗囧埢鍐嶈瘯銆?)
                    else:
                        st.error(f"OCR 璇嗗埆澶辫触: {e}")
                    st.session_state.ocr_text = ""
                    st.session_state.ocr_image_path = ""

        # Show save form if OCR completed
        if "ocr_text" in st.session_state and st.session_state.ocr_text:
            st.markdown("---")
            st.markdown("### 馃捑 淇濆瓨涓洪敊棰?)

            sc1, sc2 = st.columns(2)
            with sc1:
                ocr_subject = st.selectbox("绉戠洰", ["鏁板", "鑻辫", "璇枃", "鐗╃悊", "鍖栧", "鐢熺墿", "鍘嗗彶", "鍦扮悊", "鏀挎不", "鍏朵粬"], key="ocr_subject")
            with sc2:
                ocr_reason = st.text_input("閿欒鍘熷洜鍒嗘瀽", placeholder="渚嬪锛氳绠楀け璇€佹蹇典笉娓?..", key="ocr_reason")

            ocr_content = st.text_area("閿欓鍐呭锛堝彲缂栬緫锛?, value=st.session_state.ocr_text, height=150, key="ocr_content_edit")

            if st.button("馃捑 淇濆瓨閿欓", use_container_width=True, key="save_ocr"):
                if ocr_content.strip():
                    add_entry(
                        datetime.date.today().strftime("%Y-%m-%d"),
                        "閿欓",
                        ocr_subject,
                        ocr_content.strip(),
                        ocr_reason.strip(),
                        st.session_state.get("ocr_image_path", ""),
                    )
                    st.success("鉁?閿欓宸蹭繚瀛橈紒")
                    for k in ["ocr_text", "ocr_image_path"]:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()
                else:
                    st.error("鍐呭涓嶈兘涓虹┖锛?)


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?# TAB 5: Review Mode
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?with tabs[4]:
    st.subheader("馃搵 鏅鸿兘澶嶄範")

    df = get_all_entries()

    if df.empty:
        st.info("杩樻病鏈夋暟鎹紝鍏堟坊鍔犱竴浜涜褰曞惂锛?)
    else:
        r1, r2, r3 = st.columns(3)
        with r1:
            review_type = st.selectbox("绫诲瀷", ["鍏ㄩ儴", "鐭ヨ瘑鐐?, "閿欓"], key="review_type")
        with r2:
            review_subject = st.selectbox("绉戠洰", ["鍏ㄩ儴"] + sorted(df["subject"].unique().tolist()), key="review_subject")
        with r3:
            sort_method = st.selectbox("鎺掑簭", ["鏈€灏戝涔犱紭鍏?, "鏈€涔呮湭澶嶄範浼樺厛", "闅忔満"], key="review_sort")

        review_df = df.copy()
        if review_type != "鍏ㄩ儴":
            review_df = review_df[review_df["type"] == review_type]
        if review_subject != "鍏ㄩ儴":
            review_df = review_df[review_df["subject"] == review_subject]

        if sort_method == "鏈€灏戝涔犱紭鍏?:
            review_df = review_df.sort_values(["review_count", "last_reviewed"])
        elif sort_method == "鏈€涔呮湭澶嶄範浼樺厛":
            def date_sort_key(d):
                return d if d and d != "" else "2000-01-01"
            review_df["_sort_date"] = review_df["last_reviewed"].apply(date_sort_key)
            review_df = review_df.sort_values("_sort_date")
        else:
            review_df = review_df.sample(frac=1)

        if review_df.empty:
            st.info("娌℃湁绗﹀悎鏉′欢鐨勮褰?)
        else:
            if "review_index" not in st.session_state:
                st.session_state.review_index = 0

            total_review = len(review_df)
            idx = st.session_state.review_index

            if idx >= total_review:
                st.session_state.review_index = 0
                idx = 0

            st.progress((idx + 1) / total_review, f"绗?{idx+1} / {total_review} 鏉?)

            row = review_df.iloc[idx]

            with st.container(border=True):
                st.markdown(f"### #{row['id']} | {row['type']} | {row['subject']}")
                st.markdown(f"**鏃ユ湡锛?* {row['date']}")
                st.markdown("---")
                st.markdown(f"**鍐呭锛?*")
                st.markdown(f"> {row['content']}")

                if "reveal" not in st.session_state:
                    st.session_state.reveal = False

                rev_col1, rev_col2, rev_col3 = st.columns(3)
                with rev_col1:
                    if st.button("馃憗 鏄剧ず绛旀", use_container_width=True, key=f"reveal_{idx}"):
                        st.session_state.reveal = True
                        st.rerun()
                with rev_col2:
                    if st.button("鉁?宸叉帉鎻?, use_container_width=True, key=f"mastered_{idx}"):
                        mark_reviewed(row["id"])
                        st.session_state.review_index += 1
                        st.session_state.reveal = False
                        st.rerun()
                with rev_col3:
                    if st.button("鈴?璺宠繃", use_container_width=True, key=f"skip_{idx}"):
                        st.session_state.review_index += 1
                        st.session_state.reveal = False
                        st.rerun()

                if st.session_state.reveal:
                    st.markdown("---")
                    label = "鎺屾彙绋嬪害" if row["type"] == "鐭ヨ瘑鐐? else "閿欒鍘熷洜鍒嗘瀽"
                    st.markdown(f"**{label}锛?*")
                    st.info(row["detail"] if row["detail"] else "锛堟湭璁板綍锛?)
                    if row["image_path"] and os.path.exists(row["image_path"]):
                        st.image(row["image_path"], width=300)
                    st.caption(f"宸插涔?{row['review_count']} 娆?| 鏈€杩? {row['last_reviewed'] or '浠庢湭'}")

            nav1, nav2, nav3 = st.columns([1, 2, 1])
            with nav1:
                if st.button("猬?涓婁竴鏉?, disabled=(idx == 0), use_container_width=True):
                    st.session_state.review_index -= 1
                    st.session_state.reveal = False
                    st.rerun()
            with nav3:
                if st.button("涓嬩竴鏉?鉃?, disabled=(idx == total_review - 1), use_container_width=True):
                    st.session_state.review_index += 1
                    st.session_state.reveal = False
                    st.rerun()

            if st.button("馃攧 閲嶆柊寮€濮?, use_container_width=True):
                st.session_state.review_index = 0
                st.session_state.reveal = False
                st.rerun()
