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

# ================== SYNC ==================
def sync_from_github():
    st.session_state.data = load_json(FILE_PATH, {})
    st.session_state.denda = load_json(DENDA_FILE, [])
    st.session_state.siska = load_json(SISKA_FILE, {})
    st.session_state.ceria = load_json(CERIA_FILE, {})
    st.session_state.rohani = load_json(ROHANI_FILE, {})

# ================== SESSION ==================
defaults = {
    "data": {},
    "denda": [],
    "siska": {},
    "ceria": {},
    "rohani": {},
    "active_date": None,
    "active_siska": None,
    "active_ceria": None,
    "active_rohani": None
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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

# ================== UI ==================
col1, col2 = st.columns([2,1])

# ================== TARIKH ==================
with col1:
    st.subheader("Senarai Tarikh")

    for d in all_dates:
        key = d.strftime("%Y-%m-%d")
        color = "🟢" if key in st.session_state.data else "🔴"

        if st.button(f"{color} {key}", key=key):
            st.session_state.active_date = key
            st.rerun()

    # ================== SISKA ==================
    st.markdown("---")
    st.subheader("Program SISKA")

    for i in range(1, 11):
        key = f"SISKA_{i}"
        color = "🟢" if key in st.session_state.siska else "🔴"

        if st.button(f"{color} Program SISKA {i}", key=key):
            st.session_state.active_siska = key
            st.rerun()

    # ================== KECERIAAN ==================
    st.markdown("---")
    st.subheader("Keceriaan Asrama")

    tempat = ["Dorm","Bilik Prep","Surau","Tandas","Dewan Makan","Koridor","Bilik Warden"]

    for t in tempat:
        key = f"CERIA_{t}"
        color = "🟢" if key in st.session_state.ceria else "🔴"

        if st.button(f"{color} {t}", key=key):
            st.session_state.active_ceria = key
            st.rerun()

    # ================== KEROHANIAN ==================
    st.markdown("---")
    st.subheader("Kelas Kerohanian")

    for i in range(1, 11):
        key = f"ROHANI_{i}"
        color = "🟢" if key in st.session_state.rohani else "🔴"

        if st.button(f"{color} Kelas Kerohanian {i}", key=key):
            st.session_state.active_rohani = key
            st.rerun()

# ================== POPUP TARIKH ==================
if st.session_state.active_date:

    key = st.session_state.active_date

    @st.dialog(f"Laporan {key}")
    def form():

        ex = st.session_state.data.get(key, {})

        nama = st.text_input("Nama Warden", value=ex.get("nama_warden",""))
        oncall = st.text_input("Warden Oncall", value=ex.get("oncall",""))
        jumlah = st.number_input("Jumlah Murid", 0, value=ex.get("jumlah_murid",0))
        tiada = st.text_input("Murid Tiada / Sebab", value=ex.get("murid_tiada",""))
        masa = st.text_input("Masa Rondaan", value=ex.get("masa_rondaan",""))

        st.info("Nama murid mesti HURUF BESAR sahaja")

        kes = st.text_area("Laporan Rondaan", value=ex.get("kes",""))
        program = st.text_area("Nama Program", value=ex.get("catatan_program",""))

        if st.button("Hantar"):
            st.session_state.data[key] = {
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

            st.session_state.active_date = None
            st.rerun()

        if st.button("Reset"):
            if key in st.session_state.data:
                del st.session_state.data[key]
                save_json(FILE_PATH, st.session_state.data, "delete")
            st.session_state.active_date = None
            st.rerun()

    form()

# ================== POPUP SISKA ==================
if st.session_state.active_siska:

    key = st.session_state.active_siska

    @st.dialog(key)
    def siska():

        ex = st.session_state.siska.get(key, {})

        nama = st.text_input("Nama Program", value=ex.get("nama",""))
        tarikh = st.date_input("Tarikh", datetime.date.today())
        hadir = st.number_input("Kehadiran", 0, value=ex.get("hadir",0))
        ulasan = st.text_area("Ulasan", value=ex.get("ulasan",""))

        if ex.get("gambar1"):
            st.image(base64.b64decode(ex["gambar1"]))

        if ex.get("gambar2"):
            st.image(base64.b64decode(ex["gambar2"]))

        g1 = st.file_uploader("Gambar 1")
        g2 = st.file_uploader("Gambar 2")

        if st.button("Hantar"):
            st.session_state.siska[key] = {
                "nama": nama,
                "tarikh": str(tarikh),
                "hadir": hadir,
                "ulasan": ulasan,
                "gambar1": img_to_base64(g1) if g1 else ex.get("gambar1"),
                "gambar2": img_to_base64(g2) if g2 else ex.get("gambar2")
            }

            save_json(SISKA_FILE, st.session_state.siska, "update")
            st.session_state.active_siska = None
            st.rerun()

    siska()

# ================== POPUP KECERIAAN ==================
if st.session_state.active_ceria:

    key = st.session_state.active_ceria

    @st.dialog(key)
    def ceria():

        st.info("Upload 2 gambar keceriaan kawasan ini sepanjang tahun")

        ex = st.session_state.ceria.get(key, {})

        if ex.get("gambar1"):
            st.image(base64.b64decode(ex["gambar1"]))

        if ex.get("gambar2"):
            st.image(base64.b64decode(ex["gambar2"]))

        g1 = st.file_uploader("Gambar 1")
        g2 = st.file_uploader("Gambar 2")

        if st.button("Hantar"):
            st.session_state.ceria[key] = {
                "gambar1": img_to_base64(g1) if g1 else ex.get("gambar1"),
                "gambar2": img_to_base64(g2) if g2 else ex.get("gambar2")
            }

            save_json(CERIA_FILE, st.session_state.ceria, "update")
            st.session_state.active_ceria = None
            st.rerun()

    ceria()

# ================== POPUP KEROHANIAN ==================
if st.session_state.active_rohani:

    key = st.session_state.active_rohani

    @st.dialog(key)
    def rohani():

        ex = st.session_state.rohani.get(key, {})

        nama = st.text_input("Nama Penyampai", value=ex.get("nama",""))
        jumlah = st.number_input("Jumlah Murid", 0, value=ex.get("jumlah",0))
        tiada = st.text_input("Murid Tiada / Sebab", value=ex.get("tiada",""))
        topik = st.text_input("Topik", value=ex.get("topik",""))
        ulasan = st.text_area("Ulasan", value=ex.get("ulasan",""))

        if ex.get("gambar1"):
            st.image(base64.b64decode(ex["gambar1"]))

        if ex.get("gambar2"):
            st.image(base64.b64decode(ex["gambar2"]))

        g1 = st.file_uploader("Gambar 1")
        g2 = st.file_uploader("Gambar 2")

        if st.button("Hantar"):
            st.session_state.rohani[key] = {
                "nama": nama,
                "jumlah": jumlah,
                "tiada": tiada,
                "topik": topik,
                "ulasan": ulasan,
                "gambar1": img_to_base64(g1) if g1 else ex.get("gambar1"),
                "gambar2": img_to_base64(g2) if g2 else ex.get("gambar2")
            }

            save_json(ROHANI_FILE, st.session_state.rohani, "update")
            st.session_state.active_rohani = None
            st.rerun()

    rohani()

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
st.sidebar.header("Control Panel")

if st.sidebar.button("Sync"):
    sync_from_github()
    st.rerun()

if st.sidebar.button("Reset Semua"):
    for k in ["data","denda","siska","ceria","rohani"]:
        st.session_state[k] = {} if k != "denda" else []

    save_json(FILE_PATH, {}, "reset")
    save_json(DENDA_FILE, [], "reset")
    save_json(SISKA_FILE, {}, "reset")
    save_json(CERIA_FILE, {}, "reset")
    save_json(ROHANI_FILE, {}, "reset")

    st.rerun()