import streamlit as st
import datetime
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Warden", layout="wide")
st.title("📋 Laporan Warden")

# ================== GITHUB ==================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"

FILE_PATH = "laporan.json"
DENDA_FILE = "murid_denda.json"
SISKA_FILE = "program_siska.json"
CERIA_FILE = "keceriaan.json"
ROHANI_FILE = "kerohanian.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ================== UTIL ==================
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

def img_to_base64(file):
    if file:
        return base64.b64encode(file.read()).decode()
    return None

# ================== SESSION ==================
defaults = {
    "data": {},
    "denda": [],
    "siska": {},
    "ceria": {},
    "rohani": {},
    "popup_type": None,
    "popup_key": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================== SYNC ==================
def sync_from_github():
    st.session_state.data = load_json(FILE_PATH, {})
    st.session_state.denda = load_json(DENDA_FILE, [])
    st.session_state.siska = load_json(SISKA_FILE, {})
    st.session_state.ceria = load_json(CERIA_FILE, {})
    st.session_state.rohani = load_json(ROHANI_FILE, {})

if "synced" not in st.session_state:
    sync_from_github()
    st.session_state.synced = True

# ================== DATE ==================
def gen_dates():
    start = datetime.date(2026, 4, 1)
    end = datetime.date(2026, 11, 30)
    return [(start + datetime.timedelta(days=i)) for i in range((end-start).days+1)]

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

# ================== OPEN POPUP ==================
def open_popup(t, k):
    st.session_state.popup_type = t
    st.session_state.popup_key = k
    st.rerun()

def close_popup():
    st.session_state.popup_type = None
    st.session_state.popup_key = None
    st.rerun()

# ================== UI ==================
col1, col2 = st.columns([2,1])

# ================== TARIKH ==================
with col1:
    st.subheader("Senarai Tarikh")

    for d in all_dates:
        key = d.strftime("%Y-%m-%d")
        color = "🟢" if key in st.session_state.data else "🔴"

        if st.button(f"{color} {key}", key=key):
            open_popup("tarikh", key)

    st.markdown("---")
    st.subheader("Program SISKA")

    for i in range(1, 11):
        key = f"SISKA_{i}"
        color = "🟢" if key in st.session_state.siska else "🔴"

        if st.button(f"{color} SISKA {i}", key=key):
            open_popup("siska", key)

    st.markdown("---")
    st.subheader("Keceriaan Asrama")

    tempat = ["Dorm","Bilik Prep","Surau","Tandas","Dewan","Koridor","Warden"]

    for t in tempat:
        key = f"CERIA_{t}"
        color = "🟢" if key in st.session_state.ceria else "🔴"

        if st.button(f"{color} {t}", key=key):
            open_popup("ceria", key)

    st.markdown("---")
    st.subheader("Kerohanian")

    for i in range(1, 11):
        key = f"ROHANI_{i}"
        color = "🟢" if key in st.session_state.rohani else "🔴"

        if st.button(f"{color} Kerohanian {i}", key=key):
            open_popup("rohani", key)

# ================== POPUP SYSTEM ==================
if st.session_state.popup_type == "tarikh":

    k = st.session_state.popup_key
    ex = st.session_state.data.get(k, {})

    st.markdown(f"## 📋 Laporan {k}")

    nama = st.text_input("Nama Warden", value=ex.get("nama_warden",""))
    oncall = st.text_input("Warden Oncall", value=ex.get("oncall",""))
    jumlah = st.number_input("Jumlah Murid", 0, value=ex.get("jumlah_murid",0))
    tiada = st.text_input("Murid Tiada", value=ex.get("murid_tiada",""))
    masa = st.text_input("Masa Rondaan", value=ex.get("masa_rondaan",""))
    kes = st.text_area("Laporan", value=ex.get("kes",""))
    program = st.text_area("Program", value=ex.get("catatan_program",""))

    if st.button("Hantar"):
        st.session_state.data[k] = {
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "kes": kes,
            "catatan_program": program
        }

        save_json(FILE_PATH, st.session_state.data, "update")

        for n in extract(kes):
            if n not in st.session_state.denda:
                st.session_state.denda.append(n)

        save_json(DENDA_FILE, st.session_state.denda, "update")

        close_popup()

    if st.button("Reset"):
        if k in st.session_state.data:
            del st.session_state.data[k]
            save_json(FILE_PATH, st.session_state.data, "delete")
        close_popup()

# ================== SISKA ==================
if st.session_state.popup_type == "siska":

    k = st.session_state.popup_key
    ex = st.session_state.siska.get(k, {})

    st.markdown(f"## 🎯 SISKA {k}")

    nama = st.text_input("Nama Program", value=ex.get("nama",""))
    ulasan = st.text_area("Ulasan", value=ex.get("ulasan",""))

    if st.button("Hantar"):
        st.session_state.siska[k] = {
            "nama": nama,
            "ulasan": ulasan
        }

        save_json(SISKA_FILE, st.session_state.siska, "update")
        close_popup()

# ================== CERIA ==================
if st.session_state.popup_type == "ceria":

    k = st.session_state.popup_key
    ex = st.session_state.ceria.get(k, {})

    st.markdown(f"## 🌿 Keceriaan {k}")

    g1 = st.file_uploader("Gambar 1")
    g2 = st.file_uploader("Gambar 2")

    if st.button("Hantar"):
        st.session_state.ceria[k] = {
            "gambar1": img_to_base64(g1) if g1 else ex.get("gambar1"),
            "gambar2": img_to_base64(g2) if g2 else ex.get("gambar2")
        }

        save_json(CERIA_FILE, st.session_state.ceria, "update")
        close_popup()

# ================== ROHANI ==================
if st.session_state.popup_type == "rohani":

    k = st.session_state.popup_key
    ex = st.session_state.rohani.get(k, {})

    st.markdown(f"## 📖 Kerohanian {k}")

    nama = st.text_input("Nama Penyampai", value=ex.get("nama",""))
    topik = st.text_input("Topik", value=ex.get("topik",""))
    ulasan = st.text_area("Ulasan", value=ex.get("ulasan",""))

    if st.button("Hantar"):
        st.session_state.rohani[k] = {
            "nama": nama,
            "topik": topik,
            "ulasan": ulasan
        }

        save_json(ROHANI_FILE, st.session_state.rohani, "update")
        close_popup()

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

# ================== SIDEBAR ==================
st.sidebar.header("Control")

if st.sidebar.button("Sync"):
    sync_from_github()
    st.rerun()

if st.sidebar.button("Reset Semua"):
    for k in defaults:
        if isinstance(st.session_state[k], dict):
            st.session_state[k] = {}
        elif isinstance(st.session_state[k], list):
            st.session_state[k] = []

    save_json(FILE_PATH, {}, "reset")
    save_json(DENDA_FILE, [], "reset")
    save_json(SISKA_FILE, {}, "reset")
    save_json(CERIA_FILE, {}, "reset")
    save_json(ROHANI_FILE, {}, "reset")

    st.rerun()