import streamlit as st
import datetime
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Asrama SMKSMS1", layout="wide")
st.title("📋 Laporan Asrama SMKSMS1")

# ================== SENARAI MURID ==================
MURID = [
    "AUNY HUMAIRAH", "NURUL AIDA", "DHIYA AMNI", "NURIN NAJWA", "DANIA",
    "HAJAR BATRISYIA", "DAMIA", "QASEH ELLYSHA", "AIRIS", "AINNUR HUMAIRA",
    "SHUHADA", "QAISARA", "ARISSA QAIREN", "KHAIYISAH", "NURIN AIREN",
    "FATIHAH DAMIASARA", "NURZAHIRAH", "AMNI NADHIRAH", "NURUL ASYIKIN",
    "SYAHIDATUL", "AMNI DAHLIA", "RAUDHAH", "ALYAA", "NUR FATIHAH",
    "NAJA SYIFA", "SAFEERA", "DAMIA DAYANA", "SYUHADA ERINA", "AMANINA", "HANIM", "NURUL HUSNA",
    "ZULAIFATUL", "AINUL SAKINAH", "FARZANA", "UMMU BARIK", "AMANDA", "AMANI"
]

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ================== FUNGSI GITHUB ==================
def ambil_data_dari_github():
    try:
        file_content = repo.get_contents(FILE_PATH)
        blob = repo.get_git_blob(file_content.sha)
        return json.loads(base64.b64decode(blob.content).decode("utf-8"))
    except:
        return {}

def hantar_data_ke_github(data_baru, msg):
    try:
        file = repo.get_contents(FILE_PATH)
        repo.update_file(path=FILE_PATH, message=msg, content=json.dumps(data_baru, indent=4).encode("utf-8"), sha=file.sha)
        st.session_state.data = data_baru
        st.toast("💾 Data disimpan!", icon="✅")
    except Exception as e:
        st.error(f"❌ Ralat: {e}")

# ================== LOGIK RUMUSAN ==================
def kira_haid_mengikut_bulan(bulan_target):
    total_haid = {}
    if st.session_state.data:
        for date_str, info in st.session_state.data.items():
            try:
                tarikh_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if tarikh_obj.month == bulan_target:
                    haid_list = info.get("haid_hari_ini", info.get("haid_data", {}))
                    if isinstance(haid_list, dict):
                        for m, v in haid_list.items():
                            if v > 0:
                                total_haid[m] = total_haid.get(m, 0) + 1
            except: continue
    return total_haid

def kira_rumusan_salah_laku_keseluruhan():
    total_salah_laku = {}
    if st.session_state.data:
        for info in st.session_state.data.values():
            for kes in info.get("salah_laku_list", info.get("aduan_list", [])):
                nama = kes.get("nama")
                if nama: total_salah_laku[nama] = total_salah_laku.get(nama, 0) + 1
    return total_salah_laku

# ================== INITIALIZATION ==================
if "data" not in st.session_state: st.session_state.data = ambil_data_dari_github()
if "active_date" not in st.session_state: st.session_state.active_date = None

# ================== LAYOUT ==================
col1, col2 = st.columns([2.5, 1])

with col1:
    all_dates = [datetime.date(2026, 6, 1) + datetime.timedelta(days=i) for i in range(188)]
    with st.container(height=650):
        lajur = st.columns(5)
        for i, d in enumerate(all_dates):
            key = d.strftime("%Y-%m-%d")
            has_data = key in st.session_state.data
            if lajur[i % 5].button(f"{'🟢' if has_data else '🔴'} {key}", use_container_width=True):
                st.session_state.active_date = key
                st.rerun()

# ================== DIALOG ==================
@st.dialog("Borang Laporan Harian", width="large")
def papar_popup_laporan(date_key):
    existing = st.session_state.data.get(date_key, {})
    nama = st.text_input("Nama Warden", existing.get("nama_warden", ""))
    pilihan_haid = st.multiselect("Pilih Murid Haid:", options=MURID, default=[m for m in existing.get("haid_hari_ini", {}).keys() if m in MURID])
    
    if st.button("💾 Simpan"):
        existing.update({"nama_warden": nama, "haid_hari_ini": {m: 1 for m in pilihan_haid}})
        pangkalan = ambil_data_dari_github()
        pangkalan[date_key] = existing
        hantar_data_ke_github(pangkalan, f"Laporan {date_key}")
        st.session_state.active_date = None
        st.rerun()

if st.session_state.active_date: papar_popup_laporan(st.session_state.active_date)

# ================== RUMUSAN KANAN ==================
with col2:
    st.markdown("### 📊 Rumusan")
    
    # Bulan 6 (> 8 hari)
    st.write("**🩸 Haid Bulan 6 (> 8 Hari):**")
    res6 = kira_haid_mengikut_bulan(6)
    for n, b in sorted(res6.items(), key=lambda x: x[1], reverse=True):
        if b > 8: st.write(f"👩‍🦰 {n} ({b} Hari)")
    
    st.markdown("---")
    
    # Bulan 7 (Semua)
    st.write("**🩸 Haid Bulan 7:**")
    res7 = kira_haid_mengikut_bulan(7)
    for n, b in sorted(res7.items(), key=lambda x: x[1], reverse=True):
        st.write(f"👩‍🦰 {n} ({b} Hari)")

    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.session_state.data = ambil_data_dari_github()
        st.rerun()