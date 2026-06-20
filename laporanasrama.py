import streamlit as st
import datetime
import calendar
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Warden SMKSMS1", layout="wide")
st.title("📋 Laporan Warden")

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
HAID_FILE = "haid_count.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ================== LOAD JSON ==================
def load_json(path, default):
    try:
        content = repo.get_contents(path).decoded_content.decode()
        data = json.loads(content)
        
        if isinstance(data, dict):
            for tarikh in data:
                if isinstance(data[tarikh], dict):
                    if "haid_data" in data[tarikh] and "haid_hari_ini" not in data[tarikh]:
                        data[tarikh]["haid_hari_ini"] = data[tarikh].pop("haid_data")
        return data
    except:
        return default

# ================== SAFE SAVE JSON (DIBETULKAN UNTUK MENGELAK DATA HILANG) ==================
def save_json_safe(path, date_key, new_date_data, msg):
    """
    Fungsi ini menarik data terkini dari GitHub terlebih dahulu sebelum menulis semula
    bagi mengelakkan tarikh-tarikh lain (seperti 8/6) terpadam secara tidak sengaja.
    """
    try:
        # 1. Ambil fail asal terkini dari GitHub
        file = repo.get_contents(path)
        current_db = json.loads(file.decoded_content.decode())
    except:
        current_db = {}
        file = None

    if not isinstance(current_db, dict):
        current_db = {}

    # 2. Tukar struktur data lama jika ada
    for tarikh in current_db:
        if isinstance(current_db[tarikh], dict) and "haid_data" in current_db[tarikh]:
            current_db[tarikh]["haid_hari_ini"] = current_db[tarikh].pop("haid_data")

    # 3. Masukkan atau kemas kini data bagi tarikh spesifik sahaja tanpa usik tarikh lain
    current_db[date_key] = new_date_data

    # 4. Kemas kini session state aplikasi tempatan supaya selari
    st.session_state.data = current_db

    # 5. Simpan semula ke GitHub
    content = json.dumps(current_db, indent=4)
    if file:
        repo.update_file(path, msg, content, file.sha)
    else:
        repo.create_file(path, msg, content)

# ================== SESSION & INITIALIZATION ==================
if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

if "migration_done" not in st.session_state:
    old_haid = load_json(HAID_FILE, {})
    if old_haid and isinstance(old_haid, dict):
        first_key = list(old_haid.keys())[0] if old_haid else ""
        if first_key in MURID: 
            init_date = "2026-06-01"
            if init_date not in st.session_state.data:
                st.session_state.data[init_date] = {}
            if "haid_hari_ini" not in st.session_state.data[init_date]:
                st.session_state.data[init_date]["haid_hari_ini"] = {}
            
            for m, total in old_haid.items():
                st.session_state.data[init_date]["haid_hari_ini"][m] = total
            
            # Menggunakan save safe untuk migrasi awal
            save_json_safe(FILE_PATH, init_date, st.session_state.data[init_date], "Migrasi data haid lama ke sistem baru")
            
            content_migrated = json.dumps({"status": "migrated_to_laporan_json"}, indent=4)
            try:
                f_haid = repo.get_contents(HAID_FILE)
                repo.update_file(HAID_FILE, "Selesai migrasi", content_migrated, f_haid.sha)
            except:
                repo.create_file(HAID_FILE, "Selesai migrasi", content_migrated)
                
    st.session_state.migration_done = True

if "active_date" not in st.session_state:
    st.session_state.active_date = None

# ================== TARIKH ==================
def gen_dates():
    start = datetime.date(2026, 6, 1)
    end = datetime.date(2026, 11, 30)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out

all_dates = gen_dates()

def open_date(d):
    st.session_state.active_date = d

# ================== PENGIRAAN RUMUSAN HAID GLOBAL ==================
def kira_rumusan_haid_keseluruhan():
    total_haid = {m: 0 for m in MURID}
    for t, info in st.session_state.data.items():
        haid_tarikh = info.get("haid_hari_ini", {})
        if isinstance(haid_tarikh, dict):
            for m, hari in haid_tarikh.items():
                if m in total_haid:
                    try:
                        total_haid[m] += int(hari)
                    except:
                        pass
    return total_haid

# ================== LAYOUT ==================
col1, col2 = st.columns([2, 1])

# ================== SENARAI TARIKH ==================
with col1:
    st.subheader("📅 Senarai Tarikh")
    with st.container(height=500):
        for d in all_dates:
            key = d.strftime("%Y-%m-%d")
            color = "🟢" if key in st.session_state.data and st.session_state.data[key] else "🔴"
            if st.button(f"{color} {key}", key=f"btn_{key}", use_container_width=True):
                open_date(key)
                st.rerun()

# ================== DIALOG FORM ==================
@st.dialog("Borang Laporan", width="large")
def papar_borang(date_key):
    st.write(f"### Laporan Tarikh: {date_key}")
    
    # Ambil salinan data terkini dari session state untuk diisi pada borang
    if date_key not in st.session_state.data:
        st.session_state.data[date_key] = {}
        
    existing = dict(st.session_state.data.get(date_key, {}))

    # ================== MAKLUMAT ==================
    nama = st.text_input("Nama Warden", existing.get("nama_warden", ""))
    oncall = st.text_input("Warden Oncall", existing.get("oncall", ""))
    jumlah = st.number_input("Jumlah Murid", min_value=0, value=int(existing.get("jumlah_murid", 0)))
    tiada = st.text_area("Murid Tiada / Sebab", existing.get("murid_tiada", ""))
    masa = st.text_input("Masa Rondaan", existing.get("masa_rondaan", ""))

    st.markdown("---")

    # ================== ADUAN ==================
    st.subheader("📌 Aduan Murid")
    aduan_list = existing.get("aduan_list", [])
    if not isinstance(aduan_list, list):
        aduan_list = []
        
    murid_pilih = st.selectbox("Nama Murid", MURID, key="sel_murid")
    aduan_text = st.text_area("Aduan", key="txt_aduan")

    if st.button("➕ Tambah Aduan", key="btn_add_aduan"):
        if aduan_text.strip() != "":
            aduan_list.append({"nama": murid_pilih, "aduan": aduan_text})
            existing["aduan_list"] = aduan_list
            save_json_safe(FILE_PATH, date_key, existing, f"Tambah aduan {murid_pilih}")
            st.rerun()
        else:
            st.warning("Sila isi ruangan aduan terlebih dahulu.")

    st.markdown("### 📌 Rumusan Aduan Harian")
    kiraan = {}
    for a in aduan_list:
        kiraan[a["nama"]] = kiraan.get(a["nama"], 0) + 1

    if kiraan:
        for nama_murid, jumlah_aduan in kiraan.items():
            colA, colB = st.columns([6, 1])
            with colA:
                st.write(f"{nama_murid} ({jumlah_aduan})")
            with colB:
                if st.button("❌", key=f"del_{nama_murid}_{date_key}"):
                    aduan_list = [a for a in aduan_list if a["nama"] != nama_murid]
                    existing["aduan_list"] = aduan_list
                    save_json_safe(FILE_PATH, date_key, existing, f"Padam aduan {nama_murid}")
                    st.rerun()
    else:
        st.info("Tiada aduan untuk tarikh ini.")

    st.markdown("---")

    # ================== HAID ==================
    st.subheader("🩸 Rekod Haid Tarikh Ini")
    st.info("Tekan + jika murid haid. Tolak jika tersilap.")
    
    haid_hari_ini = existing.get("haid_hari_ini", {})
    if not isinstance(haid_hari_ini, dict):
        haid_hari_ini = {}
        
    rumusan_semasa = kira_rumusan_haid_keseluruhan()

    with st.container(height=350):
        for m in MURID:
            hari_tarikh_ini = int(haid_hari_ini.get(m, 0))
            total_terkini = rumusan_semasa.get(m, 0)
            
            col_nama, col_btn1, col_btn2 = st.columns([5, 1, 1])
            
            with col_nama:
                if hari_tarikh_ini > 0:
                    st.markdown(f"🔴 **{m} ({total_terkini})**")
                else:
                    st.write(f"⚪ {m} ({total_terkini})")
            
            with col_btn1:
                if st.button("➕", key=f"add_{m}_{date_key}"):
                    haid_hari_ini[m] = hari_tarikh_ini + 1
                    existing["haid_hari_ini"] = haid_hari_ini
                    save_json_safe(FILE_PATH, date_key, existing, f"Tambah haid {m}")
                    st.rerun()
                    
            with col_btn2:
                if st.button("➖", key=f"sub_{m}_{date_key}"):
                    if hari_tarikh_ini > 0:
                        haid_hari_ini[m] = hari_tarikh_ini - 1
                        if haid_hari_ini[m] == 0:
                            haid_hari_ini.pop(m, None)
                        existing["haid_hari_ini"] = haid_hari_ini
                        save_json_safe(FILE_PATH, date_key, existing, f"Kurangkan haid {m}")
                        st.rerun()

    st.markdown("---")

    # ================== PROGRAM ==================
    st.subheader("🎪 Program Asrama")
    nama_program = st.text_input("Nama Program", existing.get("nama_program", ""))
    
    st.write("📷 Sila muat naik gambar aktiviti (Maksimum 2 Gambar sahaja):")
    
    img_data_list = existing.get("program_images", ["", ""])
    if not isinstance(img_data_list, list):
        img_data_list = ["", ""]
    while len(img_data_list) < 2:
        img_data_list.append("")
        
    uploaded_img1 = st.file_uploader("Gambar 1", type=["png", "jpg", "jpeg"], key=f"img1_{date_key}")
    uploaded_img2 = st.file_uploader("Gambar 2", type=["png", "jpg", "jpeg"], key=f"img2_{date_key}")
    
    if uploaded_img1 is not None:
        bytes_data1 = uploaded_img1.getvalue()
        img_data_list[0] = base64.b64encode(bytes_data1).decode("utf-8")
    
    if uploaded_img2 is not None:
        bytes_data2 = uploaded_img2.getvalue()
        img_data_list[1] = base64.b64encode(bytes_data2).decode("utf-8")

    col_preview1, col_preview2 = st.columns(2)
    with col_preview1:
        if img_data_list[0] != "":
            st.image(base64.b64decode(img_data_list[0]), caption="Gambar 1 Sedia Ada", width=150)
    with col_preview2:
        if img_data_list[1] != "":
            st.image(base64.b64decode(img_data_list[1]), caption="Gambar 2 Sedia Ada", width=150)

    st.markdown("---")

    # ================== SIMPAN GLOBAL ==================
    if st.button("💾 Simpan Semua Laporan", use_container_width=True, key="btn_save_laporan"):
        final_data = {
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "aduan_list": existing.get("aduan_list", []),
            "haid_hari_ini": existing.get("haid_hari_ini", {}),
            "nama_program": nama_program,
            "program_images": img_data_list
        }
        save_json_safe(FILE_PATH, date_key, final_data, f"Kemas kini penuh laporan bagi tarikh {date_key}")
        st.success("Laporan berjaya disimpan!")
        st.session_state.active_date = None 
        st.rerun()

if st.session_state.active_date:
    papar_borang(st.session_state.active_date)

# ================== RUMUSAN GLOBAL (COL 2) ==================
with col2:
    st.subheader("📊 Rumusan Haid Keseluruhan")
    rumusan_haid = kira_rumusan_haid_keseluruhan()
    
    ada_rekod_haid = False
    for nama, jumlah in sorted(rumusan_haid.items(), key=lambda x: x[1], reverse=True):
        if jumlah > 0:
            ada_rekod_haid = True
            if jumlah >= 9:
                st.markdown(f'<div style="color:red; font-weight:bold; font-size:16px;">🚨 {nama} ({jumlah} Hari)</div>', unsafe_allow_html=True)
            else:
                st.write(f"👩‍🦰 {nama} ({jumlah} Hari)")
                
    if not ada_rekod_haid:
        st.info("Tiada rekod haid setakat ini.")

    st.markdown("---")

    if st.button("🔄 Reset Haid Bulan Baru", use_container_width=True, key="btn_reset_haid"):
        # Muat turun pangkalan data terkini dahulu untuk mengelakkan pemadaman komponen laporan lain
        try:
            f = repo.get_contents(FILE_PATH)
            db = json.loads(f.decoded_content.decode())
        except:
            db = st.session_state.data

        for t in db:
            if isinstance(db[t], dict) and "haid_hari_ini" in db[t]:
                db[t]["haid_hari_ini"] = {}

        st.session_state.data = db
        content = json.dumps(db, indent=4)
        try:
            f = repo.get_contents(FILE_PATH)
            repo.update_file(FILE_PATH, "Reset data haid bulanan", content, f.sha)
        except:
            repo.create_file(FILE_PATH, "Reset data haid bulanan", content)
            
        st.success("Semua rekod haid telah dikosongkan untuk bulan baru.")
        st.rerun()

    st.markdown("---")
    st.subheader("📌 Rumusan Aduan Keseluruhan")
    total_aduan = {}

    for t, info in st.session_state.data.items():
        if isinstance(info, dict):
            for a in info.get("aduan_list", []):
                total_aduan[a["nama"]] = total_aduan.get(a["nama"], 0) + 1

    if total_aduan:
        for n, v in sorted(total_aduan.items(), key=lambda x: x[1], reverse=True):
            colA, colB = st.columns([6, 1])
            with colA:
                st.write(f"⚠️ {n} ({v} Aduan)")
            with colB:
                if st.button("❌", key=f"clear_{n}"):
                    try:
                        f = repo.get_contents(FILE_PATH)
                        db = json.loads(f.decoded_content.decode())
                    except:
                        db = st.session_state.data

                    for t in db:
                        if isinstance(db[t], dict) and "aduan_list" in db[t]:
                            db[t]["aduan_list"] = [
                                a for a in db[t]["aduan_list"] if a["nama"] != n
                            ]

                    st.session_state.data = db
                    content = json.dumps(db, indent=4)
                    repo.update_file(FILE_PATH, f"Padam semua aduan {n}", content, f.sha)
                    st.rerun()
    else:
        st.info("Tiada rekod aduan buat masa ini.")

    st.markdown("---")
    
    # ================== KALENDAR VISUAL HAID ==================
    st.subheader("📅 Kalendar Haid Bulanan")
    
    pilihan_bulan = st.selectbox("Pilih Bulan", ["Jun", "Julai", "Ogos", "September", "Oktober", "November"], index=0)
    pilihan_tahun = 2026
    
    bulan_map = {"Jun": 6, "Julai": 7, "Ogos": 8, "September": 9, "Oktober": 10, "November": 11}
    bulan_angka = bulan_map[pilihan_bulan]
    
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(pilihan_tahun, bulan_angka)
    
    html_content = """
    <style>
        .cal-table { width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; background-color: #f9f9f9; }
        .cal-th { background-color: #4A90E2; color: white; padding: 5px; font-size: 12px; border: 1px solid #ddd; width: 14.28%; }
        .cal-td { border: 1px solid #ddd; height: 75px; vertical-align: top; padding: 4px; font-size: 11px; background-color: #ffffff; position: relative; }
        .cal-date-num { font-weight: bold; color: #333; margin-bottom: 3px; display: block; text-align: left;}
        .haid-tag { background-color: #FFD2D2; color: #D0021B; padding: 1px 3px; border-radius: 3px; margin: 1px 0; font-size: 9px; font-weight: bold; display: block; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
        .empty-td { background-color: #eee; border: 1px solid #ddd; }
    </style>
    <table class="cal-table">
        <tr>
            <th class="cal-th">Ahd</th><th class="cal-th">Isn</th><th class="cal-th">Sel</th>
            <th class="cal-th">Rab</th><th class="cal-th">Kha</th><th class="cal-th">Jum</th>
            <th class="cal-th">Sab</th>
        </tr>
    """
    
    for week in weeks:
        html_content += "<tr>"
        for day in week:
            if day == 0:
                html_content += '<td class="empty-td"></td>'
            else:
                date_str = f"{pilihan_tahun}-{bulan_angka:02d}-{day:02d}"
                html_content += f'<td class="cal-td"><span class="cal-date-num">{day}</span>'
                
                if date_str in st.session_state.data:
                    info_tarikh = st.session_state.data[date_str]
                    if isinstance(info_tarikh, dict):
                        haid_list = info_tarikh.get("haid_hari_ini", {})
                        if isinstance(haid_list, dict):
                            for murid_nama, n_hari in haid_list.items():
                                if int(n_hari) > 0:
                                    nama_pendek = " ".join(murid_nama.split()[:2])
                                    html_content += f'<span class="haid-tag">🩸 {nama_pendek}</span>'
                                    
                html_content += "</td>"
        html_content += "</tr>"
        
    html_content += "</table>"
    st.markdown(html_content, unsafe_allow_html=True)

# ================== SIDEBAR ==================
st.sidebar.header("⚙️ Control Panel")

if st.sidebar.button("🔄 Sync Data", use_container_width=True):
    st.session_state.data = load_json(FILE_PATH, {})
    st.rerun()