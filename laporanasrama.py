import streamlit as st
import datetime
import json
from github import Github

st.set_page_config(page_title="Laporan Warden", layout="wide")

st.title("📋 Laporan Warden")

# ================== GITHUB CONFIG ==================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"
DENDA_FILE = "murid_denda.json"

# ================== LOAD DATA ==================
def load_data():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        content = file.decoded_content.decode()
        return json.loads(content)
    except:
        return {}

def load_denda():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(DENDA_FILE)
        content = file.decoded_content.decode()
        return json.loads(content)
    except:
        return []

# ================== SAVE DATA ==================
def save_data(data):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    try:
        file = repo.get_contents(FILE_PATH)
        repo.update_file(
            FILE_PATH,
            "update laporan",
            json.dumps(data, indent=4),
            file.sha
        )
    except:
        repo.create_file(
            FILE_PATH,
            "create laporan",
            json.dumps(data, indent=4)
        )

def save_denda(data):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    try:
        file = repo.get_contents(DENDA_FILE)
        repo.update_file(
            DENDA_FILE,
            "update denda",
            json.dumps(data, indent=4),
            file.sha
        )
    except:
        repo.create_file(
            DENDA_FILE,
            "create denda",
            json.dumps(data, indent=4)
        )

# ================== SESSION ==================
if "submitted_dates" not in st.session_state:
    st.session_state.submitted_dates = load_data()

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

if "murid_denda" not in st.session_state:
    st.session_state.murid_denda = load_denda()

# ================== FUNCTION ==================
def generate_dates(start, end):
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += datetime.timedelta(days=1)
    return dates

def extract_nama(text):
    if not text:
        return []
    names = text.replace("\n", ",").split(",")
    names = [n.strip() for n in names if n.strip() != ""]
    return names

# ================== TARIKH ==================
start_date = datetime.date(2026, 4, 1)
end_date = datetime.date(2026, 12, 31)
all_dates = generate_dates(start_date, end_date)

# ================== POPUP ==================
if st.session_state.selected_date:

    selected_date = st.session_state.selected_date
    date_str = selected_date.strftime("%-d.%-m.%Y")

    @st.dialog(f"📋 Isi Laporan: {date_str}")
    def laporan_popup():

        existing = st.session_state.submitted_dates.get(date_str, {})

        with st.form("laporan_form"):

            nama_warden = st.text_input(
                "Nama Warden Bertugas",
                value=existing.get("nama_warden", "")
            )

            warden_oncall = st.text_input(
                "Nama Warden Oncall",
                value=existing.get("warden_oncall", "")
            )

            masa_rondaan = st.text_input(
                "Masa Rondaan",
                value=existing.get("masa_rondaan", "")
            )

            bil_murid = st.number_input(
                "Bilangan Murid",
                min_value=0,
                value=existing.get("bil_murid", 0)
            )

            murid_tiada = st.text_input(
                "Murid Tiada & Sebab",
                value=existing.get("murid_tiada", "")
            )

            # ================== KES ==================
            st.markdown("### Kes Salah Laku")
            kes_list = existing.get("kes", ["", "", ""])

            kes1 = st.text_area("Rondaan 1", value=kes_list[0])
            kes2 = st.text_area("Rondaan 2", value=kes_list[1])
            kes3 = st.text_area("Rondaan 3", value=kes_list[2])

            # ================== CATATAN ==================
            st.markdown("### Catatan / Program")
            catatan_program = st.text_area(
                "Catatan / Program",
                value=existing.get("catatan_program", "")
            )

            submitted = st.form_submit_button("Hantar")

            if submitted:

                # SIMPAN LAPORAN
                st.session_state.submitted_dates[date_str] = {
                    "nama_warden": nama_warden,
                    "warden_oncall": warden_oncall,
                    "masa_rondaan": masa_rondaan,
                    "bil_murid": bil_murid,
                    "murid_tiada": murid_tiada,
                    "kes": [kes1, kes2, kes3],
                    "catatan_program": catatan_program
                }

                save_data(st.session_state.submitted_dates)

                # ================== SIMPAN MURID DENDA ==================
                all_kes = kes1 + "," + kes2 + "," + kes3
                nama_list = extract_nama(all_kes)

                for nama in nama_list:
                    st.session_state.murid_denda.append({
                        "nama": nama,
                        "tarikh": date_str
                    })

                save_denda(st.session_state.murid_denda)

                st.success("✅ Laporan & murid denda disimpan")
                st.session_state.selected_date = None
                st.rerun()

    laporan_popup()

# ================== LAYOUT KIRI-KANAN ==================
col_left, col_right = st.columns([2,1])

# ================== KIRI (TARIKH) ==================
with col_left:

    st.subheader("Senarai Tarikh")

    num_cols = 3
    rows = [all_dates[i:i+num_cols] for i in range(0, len(all_dates), num_cols)]

    for row in rows:
        cols = st.columns(num_cols)
        for i, d in enumerate(row):
            date_str = d.strftime("%-d.%-m.%Y")

            if date_str in st.session_state.submitted_dates:
                label = f"🟢 {date_str}"
            else:
                label = f"🔴 {date_str}"

            if cols[i].button(label, key=date_str):
                st.session_state.selected_date = d
                st.rerun()

    st.markdown("---")
    st.markdown("🔴 Belum isi | 🟢 Dah hantar laporan")

# ================== KANAN (MURID DENDA) ==================
with col_right:

    st.subheader("📌 Murid Denda")

    if len(st.session_state.murid_denda) == 0:
        st.info("Tiada murid")
    else:
        for i, murid in enumerate(st.session_state.murid_denda):

            c1, c2 = st.columns([3,1])

            c1.write(f"👤 {murid['nama']}\n📅 {murid['tarikh']}")

            if c2.button("❌", key=f"del_{i}"):
                st.session_state.murid_denda.pop(i)
                save_denda(st.session_state.murid_denda)
                st.rerun()