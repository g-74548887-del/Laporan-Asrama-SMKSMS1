import streamlit as st
import datetime
import calendar
import json
from github import Github

st.set_page_config(page_title="Laporan Asrama", layout="wide")
st.title("📋 Laporan Asrama")

# ================== SENARAI MURID ==================
MURID = [
    "AUNY HUMAIRAH","NURUL AIDA","DHIYA AMNI","NURIN NAJWA","DANIA",
    "HAJAR BATRISYIA","DAMIA","QASEH ELLYSHA","AIRIS","AINNUR HUMAIRA",
    "SHUHADA","QAISARA","ARISSA QAIREN","KHAIYISAH","NURIN AIREN",
    "FATIHAH DAMIASARA","NURZAHIRAH","AMNI NADHIRAH","NURUL ASYIKIN",
    "SYAHIDATUL","AMNI DAHLIA","RAUDHAH","ALYAA","NUR FATIHAH",
    "NAJA SYIFA","SAFEERA","DAMIA DAYANA","SYUHADA ERINA","AMANINA", "HANIM", "NURUL HUSNA",
    "ZULAIFATUL","AINUL SAKINAH","FARZANA","UMMU BARIK","AMANDA","AMANI"
]

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ================== LOAD JSON ==================
def load_json(path, default):
    try:
        content = repo.get_contents(path).decoded_content.decode()
        data = json.loads(content)
        return data if isinstance(data, dict) else default
    except:
        return default

# ================== SAVE JSON ==================
def save_json_global(path, updated_db, msg):
    try:
        file = repo.get_contents(path)
        content = json.dumps(updated_db, indent=4)
        repo.update_file(path, msg, content, file.sha)
        st.session_state.data = updated_db
    except Exception as e:
        st.error(f"Gagal menyimpan ke GitHub: {e}")

# INITIALIZATION
if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

if "active_date" not in st.session_state:
    st.session_state.active_date = None

# ================== CONFIG SELECTION BULAN ==================
st.sidebar.header("⚙️ Pilihan Paparan")
pilihan_bulan = st.sidebar.selectbox("Pilih Bulan", ["Jun", "Julai", "Ogos", "September", "Oktober", "November"], index=0)
bulan_map = {"Jun": 6, "Julai": 7, "Ogos": 8, "September": 9, "Oktober": 10, "November": 11}
bulan_angka = bulan_map[pilihan_bulan]
pilihan_tahun = 2026

# ================== LOGIK PENGIRAAN RUMUSAN ==================
def kira_rumusan_haid(bulan_angka):
    total_haid = {m: 0 for m in MURID}
    for date_str, info in st.session_state.data.items():
        try:
            tarikh_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if tarikh_obj.month == bulan_angka and isinstance(info, dict):
                haid_list = info.get("haid_hari_ini", {})
                if isinstance(haid_list, dict):
                    for m in haid_list.keys():
                        if m in total_haid:
                            total_haid[m] += 1
        except:
            pass
    return total_haid

def kira_rumusan_salah_laku(bulan_angka):
    total_salah_laku = {m: 0 for m in MURID}
    for date_str, info in st.session_state.data.items():
        try:
            tarikh_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if tarikh_obj.month == bulan_angka and isinstance(info, dict):
                salah_laku_list = info.get("salah_laku_list", [])
                if isinstance(salah_laku_list, list):
                    for kes in salah_laku_list:
                        nama = kes.get("nama")
                        if nama in total_salah_laku:
                            total_salah_laku[nama] += 1
        except:
            pass
    return total_salah_laku

# LAYOUT UTAMA
col1, col2 = st.columns([2.2, 1])

with col1:
    st.subheader(f"📅 Kalendar Dinding - {pilihan_bulan} {pilihan_tahun}")
    
    cal = calendar.Calendar(firstweekday=6)  # Ahad di kolum pertama mengikut rujukan gambar
    weeks = cal.monthdayscalendar(pilihan_tahun, bulan_angka)
    
    # Header Hari
    hari_nama = ["AHAD (Sun)", "ISNIN (Mon)", "SELASA (Tue)", "RABU (Wed)", "KHAMIS (Thu)", "JUMAAT (Fri)", "SABTU (Sat)"]
    cols_header = st.columns(7)
    for idx, h in enumerate(hari_nama):
        color = "#D0021B" if idx == 0 else "#333333"
        cols_header[idx].markdown(f"<center><b style='color:{color}; font-size:13px;'>{h}</b></center>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Grid Kalendar
    for week in weeks:
        cols_day = st.columns(7)
        for idx, day in enumerate(week):
            with cols_day[idx]:
                if day != 0:
                    date_str = f"{pilihan_tahun}-{bulan_angka:02d}-{day:02d}"
                    
                    # Semak jika data sudah wujud untuk indikator warna teks / status
                    has_data = date_str in st.session_state.data and any(st.session_state.data[date_str].values())
                    label_color = "blue" if has_data else "black"
                    
                    st.markdown(f"<p style='margin-bottom:0px; font-size:18px; font-weight:bold; color:{label_color};'>{day}</p>", unsafe_allow_html=True)
                    
                    # Paparan ringkas nama murid haid di dalam kotak jika ada
                    if date_str in st.session_state.data:
                        h_list = st.session_state.data[date_str].get("haid_hari_ini", {})
                        if h_list:
                            st.markdown(f"<p style='font-size:11px; color:red; margin:0;'>🩸 {len(h_list)} Murid</p>", unsafe_allow_html=True)
                        
                        sl_list = st.session_state.data[date_str].get("salah_laku_list", [])
                        if sl_list:
                            st.markdown(f"<p style='font-size:11px; color:orange; margin:0;'>⚠️ {len(sl_list)} Kes</p>", unsafe_allow_html=True)

                    # Tekan kotak tarikh untuk buka POPUP
                    if st.button("📝 Edit", key=f"btn_{date_str}", use_container_width=True):
                        st.session_state.active_date = date_str
                        st.rerun()
                else:
                    st.write("")
        st.markdown("<hr style='margin:5px 0px;'/>", unsafe_allow_html=True)

# ================== POPUP DIALOG LAPORAN ASRAMA (EDIT DI SINI) ==================
@st.dialog("Kemaskini Laporan Asrama", width="large")
def papar_popup_laporan(date_key):
    st.write(f"### 📑 Mengedit Laporan Tarikh: **{date_key}**")
    
    if date_key not in st.session_state.data:
        st.session_state.data[date_key] = {}
    existing = dict(st.session_state.data.get(date_key, {}))

    # 1. Bahagian Asas Warden
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        nama = st.text_input("Nama Warden", existing.get("nama_warden", ""))
        oncall = st.text_input("Warden Oncall", existing.get("oncall", ""))
    with col_w2:
        jumlah = st.number_input("Jumlah Murid", min_value=0, value=int(existing.get("jumlah_murid", 0)))
        masa = st.text_input("Masa Rondaan", existing.get("masa_rondaan", ""))
        
    tiada = st.text_area("Murid Tiada / Sebab", existing.get("murid_tiada", ""))
    nama_program = st.text_input("Nama Program (Jika Ada)", existing.get("nama_program", ""))

    st.markdown("---")
    
    # 2. Bahagian Murid Haid (Edit Terus Dalam Popup Menggunakan Kotak Dropdown)
    st.subheader("🩸 Rekod Murid Haid")
    existing_haid = []
    if isinstance(existing.get("haid_hari_ini"), dict):
        existing_haid = [m for m, v in existing["haid_hari_ini"].items() if v > 0]
        
    pilihan_haid = st.multiselect(
        "Pilih Nama Murid Haid (Maksimum 15 Orang):",
        options=MURID,
        default=existing_haid,
        max_selections=15,
        key=f"popup_haid_{date_key}"
    )

    st.markdown("---")
    
    # 3. Bahagian Kes Salah Laku (Menggantikan Aduan)
    st.subheader("⚠️ Rekod Kes Salah Laku")
    salah_laku_list = existing.get("salah_laku_list", [])
    if not isinstance(salah_laku_list, list): 
        salah_laku_list = []
    
    col_sl1, col_sl2 = st.columns([1, 2])
    with col_sl1:
        m_salah = st.selectbox("Nama Murid", MURID, key="sel_salah_laku")
    with col_sl2:
        kesalahan_text = st.text_input("Butiran Kesalahan / Salah Laku", key="txt_salah_laku")
        
    if st.button("➕ Tambah Kes Salah Laku"):
        if kesalahan_text.strip() != "":
            salah_laku_list.append({"nama": m_salah, "kesalahan": kesalahan_text})
            existing["salah_laku_list"] = salah_laku_list
            st.session_state.data[date_key] = existing
            st.toast(f"Kesalahan {m_salah} ditambah sementara. Klik simpan di bawah untuk sahkan.")
            st.rerun()

    # Papar senarai kesalahan hari ini jika ada
    if salah_laku_list:
        st.write("**Senarai Kesalahan Hari Ini:**")
        for idx, item in enumerate(salah_laku_list):
            st.write(f" {idx+1}. **{item['nama']}** — {item['kesalahan']}")

    st.markdown("---")
    
    # Butang Simpan Keseluruhan Ke GitHub
    if st.button("💾 Simpan Semua Rekod Laporan", use_container_width=True):
        existing.update({
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "nama_program": nama_program,
            "haid_hari_ini": {m: 1 for m in pilihan_haid},
            "salah_laku_list": salah_laku_list
        })
        st.session_state.data[date_key] = existing
        save_json_global(FILE_PATH, st.session_state.data, f"Simpan laporan lengkap tarikh {date_key}")
        st.success("Laporan berjaya disimpan ke sistem!")
        st.session_state.active_date = None
        st.rerun()

if st.session_state.active_date:
    papar_popup_laporan(st.session_state.active_date)

# ================== RUMUSAN GLOBAL (KOLUM KANAN) ==================
with col2:
    st.markdown(f"### 📊 Rumusan Laporan ({pilihan_bulan})")
    
    # Rumusan Murid Haid
    st.write("**🩸 Bilangan Hari Haid:**")
    res_haid = kira_rumusan_haid(bulan_angka)
    ada_haid = False
    for nama, bil in sorted(res_haid.items(), key=lambda x: x[1], reverse=True):
        if bil > 0:
            ada_haid = True
            st.write(f"👩‍🦰 {nama} ({bil} Hari)")
    if not ada_haid:
        st.info("Tiada data haid dikeyin.")

    st.markdown("---")
    
    # Rumusan Kes Salah Laku
    st.write("**⚠️ Rumusan Kes Salah Laku Murid:**")
    res_sl = kira_rumusan_salah_laku(bulan_angka)
    ada_sl = False
    for nama, bil in sorted(res_sl.items(), key=lambda x: x[1], reverse=True):
        if bil > 0:
            ada_sl = True
            st.write(f"❌ {nama} ({bil} Kali)")
    if not ada_sl:
        st.info("Tiada rekod salah laku dikeyin.")

    st.markdown("---")
    if st.sidebar.button("🔄 Sync GitHub Data", use_container_width=True):
        st.session_state.data = load_json(FILE_PATH, {})
        st.rerun()