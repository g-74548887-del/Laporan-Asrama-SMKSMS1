import streamlit as st
import datetime

st.set_page_config(page_title="Laporan Warden", layout="wide")

st.title("📋 Laporan Warden")

# Initialize session state
if "submitted_dates" not in st.session_state:
    st.session_state.submitted_dates = {}

# Generate date list
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

# Sidebar list of dates
st.sidebar.header("Senarai Tarikh")
selected_date = None

for d in all_dates:
    date_str = d.strftime("%-d.%-m.%Y")

    if date_str in st.session_state.submitted_dates:
        color = "🟢"
    else:
        color = "🔴"

    if st.sidebar.button(f"{color} {date_str}"):
        selected_date = d

# Main form
if selected_date:
    st.subheader(f"Tarikh: {selected_date.strftime('%-d.%-m.%Y')}")

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
            date_str = selected_date.strftime("%-d.%-m.%Y")
            st.session_state.submitted_dates[date_str] = {
                "nama_warden": nama_warden,
                "warden_oncall": warden_oncall,
                "masa_rondaan": masa_rondaan,
                "bil_murid": bil_murid,
                "murid_tiada": murid_tiada,
                "kes": [kes1, kes2, kes3]
            }
            st.success("Laporan berjaya dihantar!")
            st.rerun()

# Instructions
st.markdown("---")
st.markdown("### Cara Guna:")
st.markdown("1. Klik tarikh di sebelah kiri")
st.markdown("2. Isi maklumat laporan")
st.markdown("3. Tekan butang Hantar")
st.markdown("4. Tarikh akan bertukar hijau jika sudah dihantar")
