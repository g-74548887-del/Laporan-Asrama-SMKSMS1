import streamlit as st
import datetime
import json
from github import Github

st.set_page_config(page_title="Laporan Warden", layout="wide")
st.title("📋 Laporan Warden (STABLE VERSION)")

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

# ================== SESSION ==================
if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

if "denda" not in st.session_state:
    st.session_state.denda = load_json(DENDA_FILE, [])

if "active_date" not in st.session_state:
    st.session_state.active_date = None   # 🔥 ONLY STRING

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

# ================== EXTRACT NAMA ==================
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

# ================== OPEN POPUP ==================
def open_date(date_str):
    st.session_state.active_date = date_str

# ================== UI ==================
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Senarai Tarikh")

    for d in all_dates:
        key = d.strftime("%Y-%m-%d")

        status = "🟢" if key in st.session_state.data else "🔴"

        if st.button(f"{status} {key}", key=key):
            open_date(key)
            st.rerun()

# ================== POPUP ==================
if st.session_state.active_date:

    date_key = st.session_state.active_date

    @st.dialog(f"Laporan {date_key}")
    def form():

        existing = st.session_state.data.get(date_key, {})

        nama = st.text_input("Warden", value=existing.get("nama_warden", ""))
        oncall = st.text_input("Oncall", value=existing.get("oncall", ""))

        kes1 = st.text_area("R1", value=existing.get("kes", ["","",""])[0])
        kes2 = st.text_area("R2", value=existing.get("kes", ["","",""])[1])
        kes3 = st.text_area("R3", value=existing.get("kes", ["","",""])[2])

        if st.button("Hantar"):

            st.session_state.data[date_key] = {
                "nama_warden": nama,
                "oncall": oncall,
                "kes": [kes1, kes2, kes3]
            }

            save_json(FILE_PATH, st.session_state.data, "update laporan")

            # denda
            all_kes = kes1 + "\n" + kes2 + "\n" + kes3
            for n in extract(all_kes):
                if n not in st.session_state.denda:
                    st.session_state.denda.append(n)

            save_json(DENDA_FILE, st.session_state.denda, "update denda")

            # 🔥 STABLE RESET (INI PENTING)
            st.session_state.active_date = None
            st.rerun()

    form()

# ================== DENDA ==================
with col2:
    st.subheader("Murid Denda")

    for i, m in enumerate(st.session_state.denda):
        c1, c2 = st.columns([3,1])
        c1.write(m)

        if c2.button("❌", key=str(i)):
            st.session_state.denda.pop(i)
            save_json(DENDA_FILE, st.session_state.denda, "delete")
            st.rerun()