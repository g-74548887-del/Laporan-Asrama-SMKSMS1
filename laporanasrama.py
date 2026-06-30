import streamlit as st
import datetime
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Asrama SMKSMS1", layout="wide")
st.title("📋 Laporan Asrama SMKSMS1")

MURID = [
    "AUNY HUMAIRAH", "NURUL AIDA", "DHIYA AMNI", "NURIN NAJWA", "DANIA", "HAJAR BATRISYIA", 
    "DAMIA", "QASEH ELLYSHA", "AIRIS", "AINNUR HUMAIRA", "SHUHADA", "QAISARA", "ARISSA QAIREN", 
    "KHAIYISAH", "NURIN AIREN", "FATIHAH DAMIASARA", "NURZAHIRAH", "AMNI NADHIRAH", "NURUL ASYIKIN",
    "SYAHIDATUL", "AMNI DAHLIA", "RAUDHAH", "ALYAA", "NUR FATIHAH", "NAJA SYIFA", "SAFEERA", 
    "DAMIA DAYANA", "SYUHADA ERINA", "AMANINA", "HANIM", "NURUL HUSNA", "ZULAIFATUL", 
    "AINUL SAKINAH", "FARZANA", "UMMU BARIK", "AMANDA", "AMANI"
]

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def ambil_data():
    try:
        file = repo.get_contents(FILE_PATH)
        return json.loads(base64.b64decode(repo.get_git_blob(file.sha).content).decode("utf-8"))
    except: return {}

# Pastikan data sentiasa segar
if "data" not in st.session_state: st.session_state.data = ambil_data()

@st.dialog("Borang Laporan Harian", width="large")
def borang_laporan(date_key):
    # Ambil data terkini untuk tarikh tersebut
    current_data = ambil_data().get(date_key, {})
    
    nama_w = st.text_input("Nama Warden", current_data.get("nama_warden", ""))
    oncall = st.text_input("Warden Oncall", current_data.get("oncall", ""))
    kehadiran = st.number_input("Kehadiran ( /36)", 0, 36, current_data.get("kehadiran", 36))
    murid_tiada = st.text_area("Murid Tiada / Sebab", current_data.get("murid_tiada", ""))
    program = st.text_input("Nama Program", current_data.get("program", ""))

    st.subheader("⚠️ Salah Laku Murid")
    # Guna session state untuk list sementara supaya tidak hilang semasa taip
    if "sl_temp" not in st.session_state: st.session_state.sl_temp = current_data.get("salah_laku_list", [])
    
    m_nama = st.selectbox("Pilih Murid", MURID)
    m_kes = st.text_input("Butiran Kesalahan")
    if st.button("➕ Tambah Kes"):
        st.session_state.sl_temp.append({"nama": m_nama, "kes": m_kes})
    
    for idx, item in enumerate(st.session_state.sl_temp):
        st.write(f"{idx+1}. **{item['nama']}** — {item['kes']}")

    st.subheader("🩸 Murid Haid")
    haid = st.multiselect("Pilih Murid", MURID, default=current_data.get("haid", []))
    
    st.file_uploader("Upload Gambar", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if st.button("💾 Hantar Semua Data"):
        pangkalan = ambil_data()
        pangkalan[date_key] = {
            "nama_warden": nama_w, "oncall": oncall, "kehadiran": kehadiran, 
            "murid_tiada": murid_tiada, "program": program,
            "salah_laku_list": st.session_state.sl_temp, "haid": haid
        }
        # Simpan ke GitHub
        file = repo.get_contents(FILE_PATH)
        repo.update_file(FILE_PATH, f"Update {date_key}", json.dumps(pangkalan, indent=4).encode("utf-8"), file.sha)
        st.session_state.data = pangkalan
        del st.session_state.sl_temp
        st.rerun()

# Layout Tarikh & Rumusan (seperti sebelum ini)
c1, c2 = st.columns([3, 1])
with c1:
    with st.container(height=650):
        lajur = st.columns(5)
        all_dates = [datetime.date(2026, 6, 1) + datetime.timedelta(days=i) for i in range(188)]
        per_col = (len(all_dates) + 4) // 5
        for col_idx in range(5):
            for idx in range(col_idx * per_col, min((col_idx + 1) * per_col, len(all_dates))):
                d = all_dates[idx]
                key = d.strftime("%Y-%m-%d")
                if lajur[col_idx].button(f"{'🟢' if key in st.session_state.data else '🔴'} {key}"):
                    if "sl_temp" in st.session_state: del st.session_state.sl_temp
                    st.session_state.active = key
                    st.rerun()

if "active" in st.session_state and st.session_state.active: borang_laporan(st.session_state.active)