import streamlit as st
import datetime
import json
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
    "NAJA SYIFA","SAFEERA","DAMIA DAYANA","SYUHADA ERINA","AMANINA", "NURUL HUSNA",
    "ZULAIFATUL","AINUL SAKINAH","FARZANA","UMMU BARIK","AMANDA","AMANI"
]

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"
HAID_FILE = "haid_count.json" # Kekal untuk backup/pindahan data lama

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ================== LOAD JSON ==================
def load_json(path, default):
    try:
        return json.loads(
            repo.get_contents(path).decoded_content.decode()
        )
    except:
        return default

# ================== SAVE JSON ==================
def save_json(path, data, msg):
    content = json.dumps(data, indent=4)
    try:
        file = repo.get_contents(path)
        repo.update_file(path, msg, content, file.sha)
    except:
        repo.create_file(path, msg, content)

# ================== SESSION & DATA INITIALIZATION ==================
if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

# --- FUNGSI PINDAH DATA LAMA (MIGRATION) ---
# Jika ada data lama dalam haid_count.json, masukkan ke dalam tarikh 2026-06-01 laporan jika belum dibuat
if "migration_done" not in st.session_state:
    old_haid = load_json(HAID_FILE, {})
    if old_haid and isinstance(old_haid, dict):
        # Semak jika data lama ini mengandungi nama murid (bukan format tarikh baru)
        first_key = list(old_haid.keys())[0] if old_haid else ""
        if first_key in MURID: 
            # Masukkan data haid lama ke tarikh asal permulaan (1 Jun 2026)
            init_date = "2026-06-01"
            if init_date not in st.session_state.data:
                st.session_state.data[init_date] = {}
            if "haid_hari_ini" not in st.session_state.data[init_date]:
                st.session_state.data[init_date]["haid_hari_ini"] = {}
            
            for m, total in old_haid.items():
                st.session_state.data[init_date]["haid_hari_ini"][m] = total
            
            # Simpan semula ke laporan.json
            save_json(FILE_PATH, st.session_state.data, "Migrasi data haid lama ke sistem baru")
            # Kosongkan haid_file supaya tidak berulang
            save_json(HAID_FILE, {"status": "migrated_to_laporan_json"}, "Selesai migrasi")
            
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
# Mengira jumlah haid terkumpul bagi setiap murid daripada keseluruhan tarikh di laporan.json
def kira_rumusan_haid_keseluruhan():
    total_haid = {m: 0 for m in MURID}
    for t, info in st.session_state.data.items():
        haid_tarikh = info.get("haid_hari_ini", {})
        for m, hari in haid_tarikh.items():
            if m in total_haid:
                total_haid[m] += hari
    return total_haid

# ================== LAYOUT ==================
col1, col2 = st.columns([2, 1])

# ================== SENARAI TARIKH ==================
with col1:
    st.subheader("📅 Senarai Tarikh")
    
    with st.container(height=500):
        for d in all_dates:
            key = d.strftime("%Y-%m-%d")
            color = "🟢" if key in st.session_state.data else "🔴"
            
            if st.button(
                f"{color} {key}",
                key=f"btn_{key}",
                use_container_width=True
            ):
                open_date(key)
                st.rerun()

# ================== DIALOG FORM ==================
@st.dialog("Borang Laporan")
def papar_borang(date_key):
    st.write(f"### Laporan Tarikh: {date_key}")
    
    # Ambil data sedia ada atau sediakan dict baru
    if date_key not in st.session_state.data:
        st.session_state.data[date_key] = {}
        
    existing = st.session_state.data.get(date_key, {})

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

    murid_pilih = st.selectbox("Nama Murid", MURID, key="sel_murid")
    aduan_text = st.text_area("Aduan", key="txt_aduan")

    if st.button("➕ Tambah Aduan", key="btn_add_aduan"):
        if aduan_text.strip() != "":
            aduan_list.append({
                "nama": murid_pilih,
                "aduan": aduan_text
            })
            existing["aduan_list"] = aduan_list
            st.session_state.data[date_key] = existing
            save_json(FILE_PATH, st.session_state.data, "update aduan")
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
                    st.session_state.data[date_key] = existing
                    save_json(FILE_PATH, st.session_state.data, "delete aduan")
                    st.rerun()
    else:
        st.info("Tiada aduan untuk tarikh ini.")

    st.markdown("---")

    # ================== HAID (SISTEM REKOD MENGIKUT TARIKH) ==================
    st.subheader("🩸 Rekod Haid Tarikh Ini")
    st.caption("Nota: Sila tekan ➕ untuk tambah 1 hari, atau ➖ jika tersilap.")
    
    # Dapatkan rekod haid khusus untuk tarikh ini sahaja
    haid_hari_ini = existing.get("haid_hari_ini", {})

    with st.container(height=300):
        for m in MURID:
            hari_semasa = haid_hari_ini.get(m, 0)
            
            colH1, colH2, colH3 = st.columns([4, 1, 1])
            with colH1:
                # Papar status tanda jika murid sedang haid pada tarikh ini
                status_tanda = f"🔴 **{m}** (Tanda: {hari_semasa} hari)" if hari_semasa > 0 else f"⚪ {m}"
                st.write(status_tanda)
            
            with colH2:
                # Button Tambah
                if st.button("➕", key=f"haid_add_{m}_{date_key}"):
                    haid_hari_ini[m] = hari_semasa + 1
                    existing["haid_hari_ini"] = haid_hari_ini
                    st.session_state.data[date_key] = existing
                    save_json(FILE_PATH, st.session_state.data, f"Tambah haid {m} pada {date_key}")
                    st.rerun()
                    
            with colH3:
                # Button Tolak
                if st.button("➖", key=f"haid_sub_{m}_{date_key}"):
                    if hari_semasa > 0:
                        haid_hari_ini[m] = hari_semasa - 1
                        # Jika kembali 0, buang dari list tarikh tersebut untuk kekemasan data
                        if haid_hari_ini[m] == 0:
                            haid_hari_ini.pop(m, None)
                        existing["haid_hari_ini"] = haid_hari_ini
                        st.session_state.data[date_key] = existing
                        save_json(FILE_PATH, st.session_state.data, f"Kurangkan haid {m} pada {date_key}")
                        st.rerun()

    st.markdown("---")

    # ================== SIMPAN ==================
    if st.button("💾 Simpan Semua Laporan", use_container_width=True, key="btn_save_laporan"):
        st.session_state.data[date_key] = {
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "aduan_list": aduan_list,
            "haid_hari_ini": haid_hari_ini # Kekal disimpan dalam tarikh ini
        }
        save_json(FILE_PATH, st.session_state.data, f"update {date_key}")
        st.success("Laporan berjaya disimpan!")
        st.session_state.active_date = None 
        st.rerun()

if st.session_state.active_date:
    papar_borang(st.session_state.active_date)

# ================== RUMUSAN GLOBAL (COL 2) ==================
with col2:
    st.subheader("📊 Rumusan Haid Keseluruhan")
    
    # Kira data kumulatif terus dari semua tarikh laporan
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
        # Untuk sistem baru, reset bermaksud memadam rekod 'haid_hari_ini' dalam setiap tarikh lama
        for t in st.session_state.data:
            if "haid_hari_ini" in st.session_state.data[t]:
                st.session_state.data[t]["haid_hari_ini"] = {}
                
        save_json(FILE_PATH, st.session_state.data, "Reset data haid bulanan")
        st.success("Semua rekod haid telah dikosongkan untuk bulan baru.")
        st.rerun()

    st.markdown("---")
    st.subheader("📌 Rumusan Aduan Keseluruhan")
    total_aduan = {}

    for t, info in st.session_state.data.items():
        for a in info.get("aduan_list", []):
            total_aduan[a["nama"]] = total_aduan.get(a["nama"], 0) + 1

    if total_aduan:
        for n, v in sorted(total_aduan.items(), key=lambda x: x[1], reverse=True):
            colA, colB = st.columns([6, 1])
            with colA:
                st.write(f"⚠️ {n} ({v} Aduan)")
            with colB:
                if st.button("❌", key=f"clear_{n}"):
                    for t in st.session_state.data:
                        if "aduan_list" in st.session_state.data[t]:
                            st.session_state.data[t]["aduan_list"] = [
                                a for a in st.session_state.data[t]["aduan_list"] if a["nama"] != n
                            ]
                    save_json(FILE_PATH, st.session_state.data, "clear aduan")
                    st.rerun()
    else:
        st.info("Tiada rekod aduan buat masa ini.")

# ================== SIDEBAR ==================
st.sidebar.header("⚙️ Control Panel")

if st.sidebar.button("🔄 Sync Data", use_container_width=True):
    st.session_state.data = load_json(FILE_PATH, {})
    st.rerun()

if st.sidebar.button("🧨 Reset Semua Data", use_container_width=True):
    st.session_state.data = {}
    save_json(FILE_PATH, {}, "RESET semua laporan")
    st.rerun()