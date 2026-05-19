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
HAID_FILE = "murid_haid.json"

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
    haid = load_json(HAID_FILE, [])

    if isinstance(data, dict):
        st.session_state.data = data

    if isinstance(haid, list):
        st.session_state.haid = haid

# ================== SESSION ==================
if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

if "haid" not in st.session_state:
    st.session_state.haid = load_json(HAID_FILE, [])

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

        if "haid" in line.lower():

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

        nama = st.text_input(
            "Nama Warden",
            value=existing.get("nama_warden", "")
        )

        oncall = st.text_input(
            "Warden Oncall",
            value=existing.get("oncall", "")
        )

        jumlah = st.number_input(
            "Jumlah Murid",
            min_value=0,
            value=existing.get("jumlah_murid", 0)
        )

        # ================== MURID TIADA ==================
        tiada = st.text_area(
            "Murid Tiada / Sebab",
            value=existing.get("murid_tiada", ""),
            height=180,
            placeholder="""1. AISY - masalah pengangkutan
2. SUMAYYAH - balik rumah
3. INTISAR - MC"""
        )

        masa = st.text_input(
            "Masa Rondaan",
            value=existing.get("masa_rondaan", "")
        )

        # ================== INFO ==================
        st.info(
            """
⚠️ Sila guna format SENARAI

1. NAMA - sebab
2. NAMA - sebab
3. NAMA - sebab

Contoh:
1. AISY - masalah pengangkutan
2. SUMAYYAH - demam

Nama murid HAID pula MESTI HURUF BESAR.

Contoh:
SITI AISYAH haid
NUR AMANI haid
            """
        )

        kes = st.text_area(
            "Laporan Rondaan",
            value=existing.get("kes", ""),
            height=180
        )

        program = st.text_area(
            "Nama Program",
            value=existing.get("catatan_program", ""),
            height=120
        )

        # ================== HANTAR ==================
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

            save_json(
                FILE_PATH,
                st.session_state.data,
                "update laporan"
            )

            # AUTO MASUK MURID HAID
            for n in extract(kes):

                if n not in st.session_state.haid:
                    st.session_state.haid.append(n)

            save_json(
                HAID_FILE,
                st.session_state.haid,
                "update haid"
            )

            st.success("Laporan berjaya dihantar")

            st.session_state.active_date = None
            st.rerun()

        st.markdown("---")

        # ================== RESET TARIKH ==================
        if st.button("🧨 Reset Tarikh Ini"):

            if date_key in st.session_state.data:

                del st.session_state.data[date_key]

                save_json(
                    FILE_PATH,
                    st.session_state.data,
                    "delete tarikh"
                )

            st.success("Tarikh telah dikosongkan")

            st.session_state.active_date = None
            st.rerun()

    form()

# ================== MURID HAID ==================
with col2:

    st.subheader("Murid Haid")

    # ================== KIRA JUMLAH ==================
    kiraan_haid = {}

    for tarikh, info in st.session_state.data.items():

        kes_text = info.get("kes", "")

        for nama in extract(kes_text):

            if nama not in kiraan_haid:
                kiraan_haid[nama] = 0

            kiraan_haid[nama] += 1

    # ================== PAPAR ==================
    if not kiraan_haid:

        st.info("Tiada murid")

    else:

        sorted_list = sorted(
            kiraan_haid.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for i, (nama, jumlah) in enumerate(sorted_list):

            c1, c2 = st.columns([3,1])

            # PAPAR NAMA + JUMLAH
            c1.write(f"{nama} ({jumlah})")

            # DELETE
            if c2.button("❌", key=f"del_{i}"):

                # Buang nama dari semua laporan
                for tarikh, info in st.session_state.data.items():

                    kes_text = info.get("kes", "")

                    lines = kes_text.split("\n")

                    new_lines = []

                    for line in lines:

                        if nama not in line:
                            new_lines.append(line)

                    st.session_state.data[tarikh]["kes"] = "\n".join(new_lines)

                # SAVE
                save_json(
                    FILE_PATH,
                    st.session_state.data,
                    "delete haid"
                )

                st.rerun()

# ================== CONTROL ==================
st.sidebar.header("Control Panel")

# ================== SYNC ==================
if st.sidebar.button("🔄 Sync Data"):

    sync_from_github()
    st.rerun()

# ================== RESET SEMUA ==================
if st.sidebar.button("🧨 Reset Semua Data"):

    st.session_state.data = {}
    st.session_state.haid = []
    st.session_state.active_date = None

    save_json(FILE_PATH, {}, "RESET semua")
    save_json(HAID_FILE, [], "RESET semua haid")

    st.rerun()