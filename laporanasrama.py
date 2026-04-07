import streamlit as st
import datetime
import calendar

st.set_page_config(page_title="Laporan Warden", layout="wide")

st.title("📋 Laporan Warden")

# Initialize session state
if "submitted_dates" not in st.session_state:
    st.session_state.submitted_dates = {}

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

# Function to render calendar-style month
def render_month(year, month):
    st.subheader(f"{calendar.month_name[month]} {year}")

    cal = calendar.monthcalendar(year, month)

    # Header hari
    days = ["Isn", "Sel", "Rab", "Kha", "Jum", "Sab", "Aha"]
    cols = st.columns(7)
    for i, day in enumerate(days):
        cols[i].markdown(f"**{day}**")

    # Tarikh
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                d = datetime.date(year, month, day)
                date_str = d.strftime("%-d.%-m.%Y")

                if date_str in st.session_state.submitted_dates:
                    label = f"🟢 {day}"
                else:
                    label = f"🔴 {day}"

                if cols[i].button(label, key=date_str):
                    st.session_state.selected_date = d

# Render months April–December 2026
for m in range(4, 13):
    render_month(2026, m)

# POPUP STYLE (top section, no scroll needed)
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
            st.rerun()

# Info
st.markdown("---")
st.markdown("🔴 Belum isi | 🟢 Dah hantar laporan")