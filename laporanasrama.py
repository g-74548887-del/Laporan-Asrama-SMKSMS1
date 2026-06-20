import streamlit as st
import datetime
import calendar
import json
import base64
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

# ================== JANA TARIKH (MULA STRAT 2026-06-08 HINGGA BULAN 11) ==================
def gen_dates():
    start = datetime.date(2026, 6, 8)  # Bermula mengikut kehendak anda
    end = datetime.date(2026, 11, 30)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out

all_dates = gen_dates()

# ================== CONFIG SELECTION BULAN ==================
st.sidebar.header("⚙️ Tetapan Paparan")
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

# LAYOUT SKRIN UTAMA (KIRI UTAMA & KANAN RUMUSAN)
col1, col2 = st.columns([2.2, 1])

with col1:
    # FORMAT AWAL DULU: Senarai tarikh menegak (Merah/Hijau)
    st.subheader(f"📅 Senarai Tarikh Laporan - Bulan {pilihan_bulan}")
    with st.container(height=350):
        for d in all_dates:
            if d.month == bulan_angka:
                key = d.strftime("%Y-%m-%d")
                
                # Format semak warna jika data laporan asas warden wujud
                color = "🟢" if key in st.session_state.data and st.session_state.data[key].get("nama_warden") else "🔴"
                if st.button(f"{color} Laporan Harian {key}", key=f"list_btn_{key}", use_container_width=True):
                    st.session_state.active_date = key
                    st.rerun()

    st.markdown("---")

    # FORMAT KALENDAR: Diletakkan di bahagian bawah untuk edit murid haid
    st.subheader(f"🧱 Kalendar Suntingan Rekod Haid ({pilihan_bulan} {pilihan_tahun})")
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(pilihan_tahun, bulan_angka)
    
    hari_nama = ["AHAD (Sun)", "ISNIN (Mon)", "SELASA (Tue)", "RABU (Wed)", "KHAMIS (Thu)", "JUMAAT (Fri)", "SABTU (Sat)"]
    cols_header = st.columns(7)
    for idx, h in enumerate(hari_nama):
        c_color = "#D0021B" if idx == 0 else "#333333"
        cols_header[idx].markdown(f"<center><b style='color:{c_color}; font-size:12px;'>{h}</b></center>", unsafe_allow_html=True)
        
    for week in weeks:
        cols_day = st.columns(7)
        for idx, day in enumerate(week):
            with cols_day[idx]:
                if day != 0:
                    date_str = f"{pilihan_tahun}-{bulan_angka:02d}-{day:02d}"
                    
                    # Papar nombor tarikh kecil
                    st.markdown(f"**{day}**")
                    
                    # Paparan status ringkas haid murid
                    existing_haid = []
                    if date_str in st.session_state.data:
                        h_list = st.session_state.data[date_str].get("haid_hari_ini", {})
                        if isinstance(h_list, dict):
                            existing_haid = [m for m, v in h_list.items() if v > 0]
                    
                    # Dropdown pelbagai pilihan (Maksimum 15 orang murid haid)
                    pilihan_baru = st.multiselect(
                        "Haid:", options=MURID, default=existing_haid, max_selections=15,
                        key=f"cal_haid_{date_str}", label_visibility="collapsed"
                    )
                    
                    if set(pilihan_baru) != set(existing_haid):
                        db = dict(st.session_state.data)
                        if date_str not in db:
                            db[date_str] = {}
                        db[date_str]["haid_hari_ini"] = {m: 1 for m in pilihan_baru}
                        save_json_global(FILE_PATH, db, f"Kemaskini rekod haid {date_str} dari kalendar bawah")
                        st.rerun()
                else:
                    st.write("")
        st.markdown("<hr style='margin:3px 0px;'/>", unsafe_allow_html=True)

# ================== POPUP BORANG DETIALS LAPORAN HARIAN ==================
@st.dialog("Borang Laporan Harian Warden", width="large")
def papar_popup_laporan(date_key):
    st.write(f"### 📑 Mengisi / Mengedit Laporan Tarikh: **{date_key}**")
    if date_key not in st.session_state.data:
        st.session_state.data[date_key] = {}
    existing = dict(st.session_state.data.get(date_key, {}))

    # Input Laporan Asas
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        nama = st.text_input("Nama Warden", existing.get("nama_warden", ""))
        oncall = st.text_input("Warden Oncall", existing.get("oncall", ""))
    with col_w2:
        jumlah = st.number_input("Jumlah Murid", min_value=0, value=int(existing.get("jumlah_murid", 0)))
        masa = st.text_input("Masa Rondaan", existing.get("masa_rondaan", ""))
        
    tiada = st.text_area("Murid Tiada / Sebab", existing.get("murid_tiada", ""))
    
    # Ruangan Nama Program (Tertinggal sebelum ini)
    nama_program = st.text_input("Nama Program", existing.get("nama_program", ""))

    st.markdown("---")
    
    # Suntingan Murid Haid Dalam Popup
    st.subheader("🩸 Rekod Murid Haid")
    ex_haid_popup = []
    if isinstance(existing.get("haid_hari_ini"), dict):
        ex_haid_popup = [m for m, v in existing["haid_hari_ini"].items() if v > 0]
        
    pilihan_haid_popup = st.multiselect(
        "Pilih Nama Murid Haid (Maksimum 15 Orang):", options=MURID, default=ex_haid_popup, max_selections=15, key=f"pop_haid_{date_key}"
    )

    st.markdown("---")
    
    # Ruangan Kes Salah Laku
    st.subheader("⚠️ Rekod Kes Salah Laku")
    salah_laku_list = existing.get("salah_laku_list", [])
    if not isinstance(salah_laku_list, list): 
        salah_laku_list = []
        
    col_sl1, col_sl2 = st.columns([1, 2])
    with col_sl1:
        m_salah = st.selectbox("Nama Murid", MURID, key="sel_pop_salah")
    with col_sl2:
        kesalahan_text = st.text_input("Butiran Kesalahan", key="txt_pop_salah")
        
    if st.button("➕ Tambah Kes Salah Laku"):
        if kesalahan_text.strip() != "":
            salah_laku_list.append({"nama": m_salah, "kesalahan": kesalahan_text})
            existing["salah_laku_list"] = salah_laku_list
            st.session_state.data[date_key] = existing
            st.rerun()

    if salah_laku_list:
        for idx, item in enumerate(salah_laku_list):
            st.write(f" {idx+1}. **{item['nama']}** — {item['kesalahan']}")

    st.markdown("---")
    
    # Ruangan Muat Naik 2 Gambar
    st.subheader("📸 Lampiran Laporan (Maksimum 2 Gambar)")
    
    # Penyimpanan Base64 imej sedia ada
    img_list = existing.get("images_base64", [])
    if not isinstance(img_list, list): img_list = []
    
    uploaded_files = st.file_uploader("Pilih gambar laporan asrama", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="uploader_gambar")
    
    # Proses tukar fail gambar ke string base64 untuk disimpan dalam JSON GitHub
    if uploaded_files:
        img_list = []
        for f in uploaded_files[:2]:  # Hadkan kepada 2 fail sahaja
            bytes_data = f.read()
            b64_str = base64.b64encode(bytes_data).decode()
            img_list.append(b64_str)

    # Paparan preview gambar jika sudah disimpan sebelum ini
    if img_list:
        st.write("Preview Gambar Sedia Ada:")
        cols_img = st.columns(len(img_list))
        for idx, b64_img in enumerate(img_list):
            cols_img[idx].image(base64.b64decode(b64_img), use_container_width=True)

    st.markdown("---")
    if st.button("💾 Simpan Semua Rekod Laporan", use_container_width=True):
        existing.update({
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "nama_program": nama_program,
            "haid_hari_ini": {m: 1 for m in pilihan_haid_popup},
            "salah_laku_list": salah_laku_list,
            "images_base64": img_list
        })
        st.session_state.data[date_key] = existing
        save_json_global(FILE_PATH, st.session_state.data, f"Simpan laporan penuh bertarikh {date_key}")
        st.success("Berjaya disimpan!")
        st.session_state.active_date = None
        st.rerun()

if st.session_state.active_date:
    papar_popup_laporan(st.session_state.active_date)

# ================== RUMUSAN DI SEBELAH KANAN ==================
with col2:
    st.markdown(f"### 📊 Rumusan Keseluruhan ({pilihan_bulan})")
    
    # Rumusan Murid Haid
    st.write("**🩸 Bilangan Hari Haid:**")
    res_haid = kira_rumusan_haid(bulan_angka)
    ada_haid = False
    for nama, bil in sorted(res_haid.items(), key=lambda x: x[1], reverse=True):
        if bil > 0:
            ada_haid = True
            st.write(f"👩‍🦰 {nama} ({bil} Hari)")
    if not ada_haid:
        st.info("Tiada rekod data murid haid.")

    st.markdown("---")
    
    # Rumusan Kes Salah Laku
    st.write("**⚠️ Rumusan Kes Salah Laku:**")
    res_sl = kira_rumusan_salah_laku(bulan_angka)
    ada_sl = False
    for nama, bil in sorted(res_sl.items(), key=lambda x: x[1], reverse=True):
        if bil > 0:
            ada_sl = True
            st.write(f"❌ {nama} ({bil} Kali)")
    if not ada_sl:
        st.info("Tiada kes salah laku direkodkan.")

    st.markdown("---")
    if st.sidebar.button("🔄 Ambil Data Terkini GitHub", use_container_width=True):
        st.session_state.data = load_json(FILE_PATH, {})
        st.rerun()