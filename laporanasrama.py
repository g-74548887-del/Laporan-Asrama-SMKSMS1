import streamlit as st
import datetime
import json
from github import Github

st.set_page_config(page_title="Laporan Warden", layout="wide")

st.title("📋 Laporan Warden")

# ================== GITHUB CONFIG ==================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  # lebih selamat
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"

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

# ================== SESSION ==================
if "submitted_dates" not in st.session_state:
    st.session_state.submitted_dates = load_data()

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

# ================== GENERATE TARIKH ==================
def generate_dates(start, end):
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += datetime.timedelta(days=1)
    return dates

start_date = datetime.date(2026, 4, 1)
end_date = datetime.date(2026, 12, 31)
all_dates = generate_dates(start_date, end_date)

# ================== POPUP FORM ==================
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

            st.markdown("### Kes Salah Laku")
            kes_list = existing.get("kes", ["", "", ""])

            kes1 = st.text_area("Rondaan 1", value=kes_list[0])
            kes2 = st.text_area("Rondaan 2", value=kes_list[1])
            kes3 = st.text_area("Rondaan 3", value=kes_list[2])

            submitted = st.form_submit_button("Hantar")

            if submitted:
                st.session_state.submitted_dates[date_str] = {
                    "nama_warden": nama_warden,
                    "warden_oncall": warden_oncall,
                    "masa_rondaan": masa_rondaan,
                    "bil_murid": bil_murid,
                    "murid_tiada": murid_tiada,
                    "kes": [kes1, kes2, kes3]
                }

                save_data(st.session_state.submitted_dates)

                st.success("✅ Laporan disimpan (kekal)")
                st.session_state.selected_date = None
                st.rerun()

    laporan_popup()

# ================== GRID TARIKH ==================
st.subheader("Senarai Tarikh")

num_cols = 6
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

# ================== INFO ==================
st.markdown("---")
st.markdown("🔴 Belum isi | 🟢 Dah hantar laporan")