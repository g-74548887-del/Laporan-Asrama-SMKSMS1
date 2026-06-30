import streamlit as st
import datetime
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Asrama SMKSMS1", layout="wide")
st.title("📋 Laporan Asrama SMKSMS1")

# ================== SENARAI MURID ==================
MURID = [
    "AUNY HUMAIRAH", "NURUL AIDA", "DHIYA AMNI", "NURIN NAJWA", "DANIA", "HAJAR BATRISYIA", 
    "DAMIA", "QASEH ELLYSHA", "AIRIS", "AINNUR HUMAIRA", "SHUHADA", "QAISARA", "ARISSA QAIREN", 
    "KHAIYISAH", "NURIN AIREN", "FATIHAH DAMIASARA", "NURZAHIRAH", "AMNI NADHIRAH", "NURUL ASYIKIN",
    "SYAHIDATUL", "AMNI DAHLIA", "RAUDHAH", "ALYAA", "NUR FATIHAH", "NAJA SYIFA", "SAFEERA", 
    "DAMIA DAYANA", "SYUHADA ERINA", "AMANINA", "HANIM", "NURUL HUSNA", "ZULAIFATUL", 
    "AINUL SAKINAH", "FARZANA", "UMMU BARIK", "AMANDA", "AMANI"
]

# GitHub Config
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ================== FUNGSI GITHUB ==================
def ambil_data():
    try:
        file = repo.get_contents(FILE_PATH)
        return json.loads(base64.b64decode(repo.get_git_blob(file.sha).content).decode("utf-8"))
    except: return {}

def simpan_data(data, msg):
    file = repo.get_contents(FILE_PATH)
    repo.update_file(FILE_PATH, msg, json.dumps(data, indent=4).encode("utf-8"), file.sha)
    st.session_state.data = data

if "data" not in st.session_state: st.session_state.data = ambil_data()

# ================== POPUP BORANG ==================
@st.dialog("Borang Laporan Harian", width="large")
def borang_laporan(date_key):
    data = st.session_state.data.get(date_key, {})
    
    col1, col2 = st.columns(2)
    with col1:
        nama_w = st.text_input("Nama Warden", data.get("nama_warden", ""))
        oncall = st.text_input("Warden Oncall", data.get("oncall", ""))
        kehadiran = st.number_input("Kehadiran ( /36)", 0, 36, data.get("kehadiran", 36))
    with col2:
        murid_tiada = st.text_area("Murid Tiada / Sebab", data.get("murid_tiada", ""))
        program = st.text_input("Nama Program", data.get("program", ""))

    st.subheader("⚠️ Salah Laku Murid")
    sl_list = data.get("salah_laku_list", [])
    m_nama = st.selectbox("Pilih Murid", MURID)
    m_kes = st.text_input("Butiran Kesalahan")
    if st.button("➕ Tambah Kes"):
        sl_list.append({"nama": m_nama, "kes": m_kes})
        data["salah_laku_list"] = sl_list
    
    for idx, item in enumerate(sl_list):
        st.write(f"{idx+1}. **{item['nama']}** — {item['kes']}")

    st.subheader("🩸 Murid Haid")
    haid = st.multiselect("Pilih Murid", MURID, default=[m for m in data.get("haid", [])])
    
    # Upload Gambar
    uploaded_files = st.file_uploader("Upload 2 Gambar", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if st.button("💾 Simpan Semua Data"):
        pangkalan = ambil_data()
        pangkalan[date_key] = {
            "nama_warden": nama_w, "oncall": oncall, "kehadiran": kehadiran, 
            "murid_tiada": murid_tiada, "program": program,
            "salah_laku_list": sl_list, "haid": haid
        }
        simpan_data(pangkalan, f"Laporan {date_key}")
        st.rerun()

# ================== LAYOUT TARIKH (BLOK) ==================
start_date = datetime.date(2026, 6, 1)
end_date = datetime.date(2026, 12, 5)
all_dates = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]

c1, c2 = st.columns([3, 1])
with c1:
    with st.container(height=650):
        lajur = st.columns(5)
        per_col = (len(all_dates) + 4) // 5
        for col_idx in range(5):
            with lajur[col_idx]:
                start_idx = col_idx * per_col
                end_idx = min(start_idx + per_col, len(all_dates))
                for idx in range(start_idx, end_idx):
                    d = all_dates[idx]
                    key = d.strftime("%Y-%m-%d")
                    if st.button(f"{'🟢' if key in st.session_state.data else '🔴'} {key}", use_container_width=True):
                        st.session_state.active = key
                        st.rerun()

if "active" in st.session_state and st.session_state.active:
    borang_laporan(st.session_state.active)

# ================== RUMUSAN ==================
with c2:
    st.header("📊 Rumusan")
    
    # Haid B6 (>8 hari)
    st.write("**🩸 Haid B6 (>8 hari):**")
    haid6 = {}
    for k, v in st.session_state.data.items():
        if k.startswith("2026-06"):
            for m in v.get("haid", []): haid6[m] = haid6.get(m, 0) + 1
    for m, b in sorted(haid6.items(), key=lambda x: x[1], reverse=True):
        if b > 8: st.write(f"👩‍🦰 {m}: **{b} hari**")
    
    # Haid B7
    st.write("**🩸 Haid B7:**")
    haid7 = {}
    for k, v in st.session_state.data.items():
        if k.startswith("2026-07"):
            for m in v.get("haid", []): haid7[m] = haid7.get(m, 0) + 1
    for m, b in sorted(haid7.items(), key=lambda x: x[1], reverse=True):
        st.write(f"👩‍🦰 {m}: **{b} hari**")

    # Salah Laku
    st.write("**⚠️ Salah Laku:**")
    sl_total = {}
    for v in st.session_state.data.values():
        for item in v.get("salah_laku_list", []):
            nama = item["nama"]
            sl_total[nama] = sl_total.get(nama, 0) + 1
    for m, b in sorted(sl_total.items(), key=lambda x: x[1], reverse=True):
        st.write(f"❌ {m}: **{b} kali**")