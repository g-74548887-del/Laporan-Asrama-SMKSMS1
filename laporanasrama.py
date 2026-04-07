import streamlit as st
import datetime

st.set_page_config(page_title="Laporan Warden", layout="wide")

st.title("📋 Laporan Warden")

# Session state
if "submitted_dates" not in st.session_state:
    st.session_state.submitted_dates = {}

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

# Generate dates
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

# ===== FIX: Proper grid (ikut turutan, tak lompat) =====
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
            st.rerun()  # terus refresh supaya form naik atas

# ===== FORM (muncul terus atas bila klik) =====
if st.session_state.selected_date:
    selected_date = st.session_state.selected_date
    date_str = selected_date.strftime("%-d.%-m.%Y")

    st.markdown("---")
    st.subheader(f"Isi Laporan: {date_str}")

    with st.form("laporan_form"):
        nama_warden = st.text_input("Nama Warden Bertugas")
        warden_oncall = st.text_input("Nama Warden Oncall")
        masa_rondaan = st.text_input("Masa Rondaan (contoh: 9:00 malam)")
        bil_murid = st.number_input("Bilangan Murid", min_value=0)
        murid_tiada = st.text_input("Murid Tiada & Sebab")

        st.markdown("### Kes Salah Laku (3 Rondaan)")
        kes1 = st.text_area("Rondaan 1")
        kes2 = st.text_area("Rondaan 2")
        kes3 = st.text_area("Rondaan 3")

        submitted = st.form_submit_button("Hantar")

        if submitted:
            st.session_state.submitted_dates[date_str] = True
            st.success("Laporan berjaya dihantar!")
            st.session_state.selected_date = None
            st.rerun()

# Info
st.markdown("---")
st.markdown("🔴 Belum isi | 🟢 Dah hantar laporan")