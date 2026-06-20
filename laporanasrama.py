import streamlit as st
import datetime
import calendar
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Warden SMKSMS1", layout="wide")
st.title("📋 Laporan Warden & Rekod Haid")

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

# ================== INITIALIZATION ==================
if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

if "active_date" not in st.session_state:
    st.session_state.active_date = None

# ================== TARIKH JANA ==================
def gen_dates():
    start = datetime.date(2026, 6, 1)
    end = datetime.date(2026, 11, 30)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out

all_dates = gen_dates()

# ================== LOGIK PENGIRAAN RUMUSAN HAID BERSANDARKAN KALENDAR ==================
def kira_rumusan_haid_kalendar(bulan_angka):
    total_haid = {m: 0 for m in MURID}
    for date_str, info in st.session_state.data.items():
        try:
            # Pastikan tarikh sepadan dengan bulan yang sedang dilihat
            tarikh_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if tarikh_obj.month == bulan_angka:
                if isinstance(info, dict):
                    haid_list = info.get("haid_hari_ini", {})
                    if isinstance(haid_list, dict):
                        for m, nilai in haid_list.items():
                            if m in total_haid and int(nilai) > 0:
                                total_haid[m] += 1  # Kira 1 hari bagi setiap kemunculan tarikh
        except:
            pass
    return total_haid

# ================== PILIHAN BULAN UTAMA ==================
st.sidebar.header("⚙️ Tetapan Paparan")
pilihan_bulan = st.sidebar.selectbox("Pilih Bulan Kalendar", ["Jun", "Julai", "Ogos", "September", "Oktober", "November"], index=0)
bulan_map = {"Jun": 6, "Julai": 7, "Ogos": 8, "September": 9, "Oktober": 10, "November": 11}
bulan_angka = bulan_map[pilihan_bulan]
pilihan_tahun = 2026

# LAYOUT UTAMA
col1, col2 = st.columns([2, 1])

with col1:
    # TAB 1: LAPORAN HARIAN WARDEN
    tab1, tab2 = st.tabs(["📋 Laporan Harian Warden", "📝 Edit Rekod Haid (Kalendar)"])
    
    with tab1:
        st.subheader("📅 Senarai Tarikh Laporan")
        with st.container(height=400):
            for d in all_dates:
                if d.month == bulan_angka:
                    key = d.strftime("%Y-%m-%d")
                    color = "🟢" if key in st.session_state.data and st.session_state.data[key] else "🔴"
                    if st.button(f"{color} Laporan {key}", key=f"btn_{key}", use_container_width=True):
                        st.session_state.active_date = key
                        st.rerun()

    # TAB 2: MASUKKAN DATA HAID TERUS PADA KALENDAR (SISTEM BAHARU)
    with tab2:
        st.subheader("🩸 Tanda Haid Murid Terus Pada Kalendar")
        st.info("Cara Guna: Pilih nama murid terlebih dahulu, kemudian klik pada butang TARIKH di bawah untuk Tanda (🔴) atau Padam (⚪) rekod haid.")
        
        # Dropdown Pilih Nama
        murid_dipilih = st.selectbox("🎯 Pilih Nama Murid Yang Ingin Diedit:", MURID, key="pilih_murid_haid")
        
        # Bina Grid Kalendar Interaktif
        cal = calendar.Calendar(firstweekday=6)
        weeks = cal.monthdayscalendar(pilihan_tahun, bulan_angka)
        
        # Headers Hari
        cols_header = st.columns(7)
        hari_nama = ["Ahd", "Isn", "Sel", "Rab", "Kha", "Jum", "Sab"]
        for idx, h in enumerate(hari_nama):
            cols_header[idx].markdown(f"<center><b>{h}</b></center>", unsafe_allow_html=True)
            
        # Isi Tarikh Kalendar
        for week in weeks:
            cols_day = st.columns(7)
            for idx, day in enumerate(week):
                if day != 0:
                    date_str = f"{pilihan_tahun}-{bulan_angka:02d}-{day:02d}"
                    
                    # Semak status haid murid terpilih pada tarikh ini
                    is_haid = False
                    if date_str in st.session_state.data:
                        h_list = st.session_state.data[date_str].get("haid_hari_ini", {})
                        if isinstance(h_list, dict) and h_list.get(murid_dipilih, 0) > 0:
                            is_haid = True
                    
                    btn_label = f"🔴\n{day}" if is_haid else f"⚪\n{day}"
                    
                    if cols_day[idx].button(btn_label, key=f"cal_edit_{date_str}", use_container_width=True):
                        db = dict(st.session_state.data)
                        if date_str not in db:
                            db[date_str] = {}
                        if "haid_hari_ini" not in db[date_str] or not isinstance(db[date_str]["haid_hari_ini"], dict):
                            db[date_str]["haid_hari_ini"] = {}
                        
                        # Toggle Pasang / Padam
                        if is_haid:
                            db[date_str]["haid_hari_ini"].pop(murid_dipilih, None)
                            msg = f"Padam haid {murid_dipilih} pada {date_str}"
                        else:
                            db[date_str]["haid_hari_ini"][murid_dipilih] = 1
                            msg = f"Tanda haid {murid_dipilih} pada {date_str}"
                            
                        save_json_global(FILE_PATH, db, msg)
                        st.rerun()
                else:
                    cols_day[idx].write("")

# ================== DIALOG FORM LAPORAN WARDEN ==================
@st.dialog("Borang Laporan Harian", width="large")
def papar_borang(date_key):
    st.write(f"### Laporan Tarikh: {date_key}")
    if date_key not in st.session_state.data:
        st.session_state.data[date_key] = {}
    existing = dict(st.session_state.data.get(date_key, {}))

    nama = st.text_input("Nama Warden", existing.get("nama_warden", ""))
    oncall = st.text_input("Warden Oncall", existing.get("oncall", ""))
    jumlah = st.number_input("Jumlah Murid", min_value=0, value=int(existing.get("jumlah_murid", 0)))
    tiada = st.text_area("Murid Tiada / Sebab", existing.get("murid_tiada", ""))
    masa = st.text_input("Masa Rondaan", existing.get("masa_rondaan", ""))

    st.markdown("---")
    st.subheader("📌 Aduan Murid")
    aduan_list = existing.get("aduan_list", [])
    if not isinstance(aduan_list, list): aduan_list = []
    
    m_pilih = st.selectbox("Nama Murid", MURID, key="sel_murid_aduan")
    a_text = st.text_area("Aduan", key="txt_aduan_baru")

    if st.button("➕ Tambah Aduan"):
        if a_text.strip() != "":
            aduan_list.append({"nama": m_pilih, "aduan": a_text})
            existing["aduan_list"] = aduan_list
            st.session_state.data[date_key] = existing
            save_json_global(FILE_PATH, st.session_state.data, f"Tambah aduan {m_pilih} pada {date_key}")
            st.rerun()

    # Papar aduan harian
    if aduan_list:
        for idx, item in enumerate(aduan_list):
            st.write(f"• **{item['nama']}**: {item['aduan']}")

    st.markdown("---")
    st.subheader("🎪 Program Asrama")
    nama_program = st.text_input("Nama Program", existing.get("nama_program", ""))

    if st.button("💾 Simpan Semua Laporan", use_container_width=True):
        existing.update({
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "nama_program": nama_program,
            "aduan_list": aduan_list,
            "haid_hari_ini": existing.get("haid_hari_ini", {})  # Kekalkan data haid dari kalendar
        })
        st.session_state.data[date_key] = existing
        save_json_global(FILE_PATH, st.session_state.data, f"Kemas kini laporan penuh {date_key}")
        st.success("Laporan berjaya disimpan!")
        st.session_state.active_date = None
        st.rerun()

if st.session_state.active_date:
    papar_borang(st.session_state.active_date)

# ================== RUMUSAN GLOBAL (KOLUM KANAN) ==================
with col2:
    st.subheader(f"📊 Rumusan Haid ({pilihan_bulan})")
    rumusan_haid = kira_rumusan_haid_kalendar(bulan_angka)
    
    ada_haid = False
    for nama, jumlah in sorted(rumusan_haid.items(), key=lambda x: x[1], reverse=True):
        if jumlah > 0:
            ada_haid = True
            if jumlah >= 9:
                st.markdown(f'<div style="color:red; font-weight:bold; font-size:16px;">🚨 {nama} ({jumlah} Hari)</div>', unsafe_allow_html=True)
            else:
                st.write(f"👩‍🦰 {nama} ({jumlah} Hari)")
                
    if not ada_haid:
        st.info("Tiada rekod haid dikeyin bulan ini.")

    st.markdown("---")
    st.subheader("📌 Rumusan Aduan Keseluruhan")
    total_aduan = {}
    for t, info in st.session_state.data.items():
        if isinstance(info, dict):
            for a in info.get("aduan_list", []):
                total_aduan[a["nama"]] = total_aduan.get(a["nama"], 0) + 1

    if total_aduan:
        for n, v in sorted(total_aduan.items(), key=lambda x: x[1], reverse=True):
            st.write(f"⚠️ {n} ({v} Aduan)")
    else:
        st.info("Tiada rekod aduan.")

    st.markdown("---")
    if st.sidebar.button("🔄 Sync Data GitHub", use_container_width=True):
        st.session_state.data = load_json(FILE_PATH, {})
        st.rerun()