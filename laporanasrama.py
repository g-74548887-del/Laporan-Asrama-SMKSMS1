import streamlit as st
import datetime
import json
from github import Github
from collections import Counter

# ================== PAGE ==================
st.set_page_config(
    page_title="Laporan Warden",
    layout="wide"
)

st.title("📋 Laporan Warden")

# ================== GITHUB ==================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"

FILE_PATH = "laporan.json"
DENDA_FILE = "murid_denda.json"

g = Github(GITHUB_TOKEN)

repo = g.get_repo(REPO_NAME)

# ================== LOAD JSON ==================
def load_json(path, default):

    try:

        file = repo.get_contents(path)

        return json.loads(
            file.decoded_content.decode()
        )

    except:

        return default

# ================== SAVE JSON ==================
def save_json(path, data, msg):

    try:

        file = repo.get_contents(path)

        repo.update_file(
            path,
            msg,
            json.dumps(data, indent=4),
            file.sha
        )

    except:

        repo.create_file(
            path,
            msg,
            json.dumps(data, indent=4)
        )

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

# ================== EXTRACT ==================
def extract(text):

    if not text:
        return []

    res = []

    for line in text.split("\n"):

        parts = line.replace(",", "\n").split("\n")

        for p in parts:

            p = p.strip()

            if p and p.upper() == p:
                res.append(p)

    return list(set(res))

# ================== TRACKING ==================
tiada_counter = Counter()
haid_counter = Counter()

for tarikh, info in st.session_state.data.items():

    # MURID TIADA
    murid_tiada = info.get("murid_tiada", "")

    for nama in extract(murid_tiada):
        tiada_counter[nama] += 1

    # MURID HAID
    murid_haid = info.get("murid_haid", "")

    for nama in extract(murid_haid):
        haid_counter[nama] += 1

# ================== FILTER >10 ==================
murid_tiada_10 = {
    k: v for k, v in tiada_counter.items() if v >= 10
}

murid_haid_10 = {
    k: v for k, v in haid_counter.items() if v >= 10
}

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

# ================== OPEN ==================
def open_date(d):

    st.session_state.active_date = d

# ================== UI ==================
col1, col2 = st.columns([2,1])

# ================== DATE LIST ==================
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

        # ================== INPUT ==================
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
        st.info(
            "⚠️ Tulis nama murid HURUF BESAR supaya "
            "sistem boleh detect murid tiada lebih 10 hari.\n\n"
            "Contoh:\n"
            "AUNY HUMAIRAH, NURUL AIDA, DHIYA AMNI"
        )

        tiada = st.text_area(
            "Murid Tiada / Sebab",
            value=existing.get("murid_tiada", "")
        )

        # ================== MURID HAID ==================
        st.info(
            "⚠️ Tulis nama murid HAID dalam HURUF BESAR "
            "supaya sistem boleh detect murid haid lebih 10 hari.\n\n"
            "Contoh:\n"
            "AUNY HUMAIRAH, NURUL AIDA, DHIYA AMNI"
        )

        murid_haid = st.text_area(
            "Murid Haid",
            value=existing.get("murid_haid", "")
        )

        # ================== MASA ==================
        masa = st.text_input(
            "Masa Rondaan",
            value=existing.get("masa_rondaan", "")
        )

        # ================== KES ==================
        st.info(
            "⚠️ Nama murid mesti HURUF BESAR.\n"
            "Contoh: SITI NURHALIZA tidak solat subuh"
        )

        kes = st.text_area(
            "Laporan Rondaan",
            value=existing.get("kes", "")
        )

        # ================== AKTIVITI ==================
        aktiviti = st.text_area(
            "Nama Aktiviti",
            value=existing.get("nama_aktiviti", "")
        )

        gambar_aktiviti = st.file_uploader(
            "Upload 2 Gambar Aktiviti",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="aktiviti_upload"
        )

        # ================== SISKA ==================
        program_siska = st.text_area(
            "Nama Program SISKA",
            value=existing.get("program_siska", "")
        )

        gambar_siska = st.file_uploader(
            "Upload 2 Gambar SISKA",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="siska_upload"
        )

        # ================== HANTAR ==================
        if st.button("Hantar"):

            st.session_state.data[date_key] = {

                "nama_warden": nama,
                "oncall": oncall,
                "jumlah_murid": jumlah,

                "murid_tiada": tiada,
                "murid_haid": murid_haid,

                "masa_rondaan": masa,
                "kes": kes,

                "nama_aktiviti": aktiviti,
                "program_siska": program_siska
            }

            save_json(
                FILE_PATH,
                st.session_state.data,
                "update laporan"
            )

            # ================== AUTO DENDA ==================
            for n in extract(kes):

                if n not in st.session_state.denda:

                    st.session_state.denda.append(n)

            save_json(
                DENDA_FILE,
                st.session_state.denda,
                "update denda"
            )

            st.success("Data berjaya disimpan")

            st.session_state.active_date = None

            st.rerun()

        st.markdown("---")

        # ================== RESET ==================
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

# ================== SIDEBAR ==================
with col2:

    # ================== DENDA ==================
    st.subheader("Murid Denda")

    st.caption(
        "Tekan ❌ untuk buang nama jika telah ambil tindakan."
    )

    if not st.session_state.denda:

        st.info("Tiada murid")

    else:

        for i, m in enumerate(st.session_state.denda):

            c1, c2 = st.columns([3,1])

            c1.write(m)

            if c2.button("❌", key=f"denda_{i}"):

                st.session_state.denda.pop(i)

                save_json(
                    DENDA_FILE,
                    st.session_state.denda,
                    "delete"
                )

                st.rerun()

    st.markdown("---")

    # ================== TIADA >10 ==================
    st.subheader("Murid Tiada >10 Hari")

    st.caption(
        "Tekan ❌ untuk buang nama jika telah ambil tindakan."
    )

    if not murid_tiada_10:

        st.info("Tiada murid")

    else:

        for i, (nama, total) in enumerate(murid_tiada_10.items()):

            c1, c2 = st.columns([3,1])

            c1.write(f"{nama} ({total} hari)")

            if c2.button("❌", key=f"tiada_{i}"):

                for tarikh in st.session_state.data:

                    text = st.session_state.data[tarikh].get(
                        "murid_tiada",
                        ""
                    )

                    text = text.replace(nama, "")

                    st.session_state.data[tarikh]["murid_tiada"] = text

                save_json(
                    FILE_PATH,
                    st.session_state.data,
                    "remove murid tiada"
                )

                st.rerun()

    st.markdown("---")

    # ================== HAID >10 ==================
    st.subheader("Murid Haid >10 Hari")

    st.caption(
        "Tekan ❌ untuk buang nama jika telah ambil tindakan."
    )

    if not murid_haid_10:

        st.info("Tiada murid")

    else:

        for i, (nama, total) in enumerate(murid_haid_10.items()):

            c1, c2 = st.columns([3,1])

            c1.write(f"{nama} ({total} hari)")

            if c2.button("❌", key=f"haid_{i}"):

                for tarikh in st.session_state.data:

                    text = st.session_state.data[tarikh].get(
                        "murid_haid",
                        ""
                    )

                    text = text.replace(nama, "")

                    st.session_state.data[tarikh]["murid_haid"] = text

                save_json(
                    FILE_PATH,
                    st.session_state.data,
                    "remove murid haid"
                )

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