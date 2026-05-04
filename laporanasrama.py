import streamlit as st
import datetime
import json
from github import Github

st.set_page_config(page_title="Laporan Warden", layout="wide")
st.title("📋 Laporan Warden")

# ================== GITHUB ==================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"
DENDA_FILE = "murid_denda.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ================== LOAD ==================
def load_json(path, default):
    try:
        file = repo.get_contents(path)
        return json.loads(file.decoded_content.decode())
    except:
        return default

def save_json(path, data, msg):
    try:
        file = repo.get_contents(path)
        repo.update_file(path, msg, json.dumps(data, indent=4), file.sha)
    except:
        repo.create_file(path, msg, json.dumps(data, indent=4))

# ================== SYNC ==================
def sync_from_github():
    data = load_json(FILE_PATH, {})
    denda = load_json(DENDA_FILE, [])

    if isinstance(data, dict):
        st.session_state.data = data
    if isinstance(denda, list):
        st.session_state.denda = denda

# ================== SESSION ==================
if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

if "denda" not in st.session_state:
    st.session_state.denda = load_json(DENDA_FILE, [])

if "active_date" not in st.session_state:
    st.session_state.active_date = None

if "synced" not in st.session_state:
    sync_from_github()
    st.session_state.synced = True

# ================== DATE ==================
def gen_dates():
    start = datetime.date(2026, 4, 1)
    end = datetime.date(2026, 11, 30)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out

all_dates = gen_dates()

# ================== EXTRACT ==================
def extract(text):
    if not text:
        return []
    res = []
    for line in text.split("\n"):
        words = line.split()
        nama = []
        for w in words:
            if w.isupper():
                nama.append(w)
            else:
                break
        if nama:
            res.append(" ".join(nama))
    return list(set(res))

# ================== OPEN ==================
def open_date(d):
    st.session_state.active_date = d

# ================== UI ==================
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Senarai Tarikh")

    for d in all_dates:
        key = d.strftime("%Y-%m-%d")

        color = "🟢" if key in st.session_state.data else "🔴"

        if st.button(f"{color} {key}", key=key):
            open_date(key)
            st.rerun()

# ================== POPUP ==================
if st.session_state.active_date:

    date_key = st.session_state.active_date

    @st.dialog(f"Laporan {date_key}")
    def form():

        existing = st.session_state.data.get(date_key, {})

        nama = st.text_input("Nama Warden", value=existing.get("nama_warden", ""))
        oncall = st.text_input("Warden Oncall", value=existing.get("oncall", ""))

        jumlah = st.number_input("Jumlah Murid", min_value=0, value=existing.get("jumlah_murid", 0))
        tiada = st.text_input("Murid Tiada / Sebab", value=existing.get("murid_tiada", ""))
        masa = st.text_input("Masa Rondaan", value=existing.get("masa_rondaan", ""))

        st.info(
            "⚠️ Nama murid MESTI HURUF BESAR sahaja.\n"
            "Contoh: SITI NURHALIZA tidak solat subuh berjemaah"
        )

        kes = st.text_area(
            "Laporan Rondaan",
            value=existing.get("kes", "")
        )

        program = st.text_area(
            "Nama Program",
            value=existing.get("catatan_program", "")
        )

        if st.button("Hantar"):

            st.session_state.data[date_key] = {
                "nama_warden": nama,
                "oncall": oncall,
                "jumlah_murid": jumlah,
                "murid_tiada": tiada,
                "masa_rondaan": masa,
                "kes": kes,
                "catatan_program": program
            }

            save_json(FILE_PATH, st.session_state.data, "update laporan")

            for n in extract(kes):
                if n not in st.session_state.denda:
                    st.session_state.denda.append(n)

            save_json(DENDA_FILE, st.session_state.denda, "update denda")

            st.session_state.active_date = None
            st.rerun()

        st.markdown("---")

        if st.button("🧨 Reset Tarikh Ini"):

            if date_key in st.session_state.data:
                del st.session_state.data[date_key]
                save_json(FILE_PATH, st.session_state.data, "delete tarikh")

            st.success("Tarikh telah dikosongkan")
            st.session_state.active_date = None
            st.rerun()

    form()

# ================== DENDA ==================
with col2:
    st.subheader("Murid Denda")

    if not st.session_state.denda:
        st.info("Tiada murid")
    else:
        for i, m in enumerate(st.session_state.denda):
            c1, c2 = st.columns([3,1])
            c1.write(m)

            if c2.button("❌", key=str(i)):
                st.session_state.denda.pop(i)
                save_json(DENDA_FILE, st.session_state.denda, "delete")
                st.rerun()

# ================== CONTROL ==================
st.sidebar.header("Control Panel")

if st.sidebar.button("🔄 Sync Data"):
    sync_from_github()
    st.rerun()

if st.sidebar.button("🧨 Reset Semua Data"):
    st.session_state.data = {}
    st.session_state.denda = []
    st.session_state.active_date = None

    save_json(FILE_PATH, {}, "RESET semua")
    save_json(DENDA_FILE, [], "RESET semua denda")

    st.rerun()