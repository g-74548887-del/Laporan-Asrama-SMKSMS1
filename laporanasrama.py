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
HAID_FILE = "haid_count.json"

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
        repo.update_file(
            path,
            msg,
            content,
            file.sha
        )
    except:
        repo.create_file(
            path,
            msg,
            content
        )

# ================== SESSION ==================
if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

if "active_date" not in st.session_state:
    st.session_state.active_date = None

if "show_haid_popup" not in st.session_state:
    st.session_state.show_haid_popup = False

# ================== TARIKH ==================
def gen_dates():
    # START BULAN 6 (2026)
    start = datetime.date(2026, 6, 1)
    end = datetime.date(2026, 11, 30)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out

all_dates = gen_dates()

# ================== OPEN TARIKH ==================
def open_date(d):
    st.session_state.active_date = d

# ================== LAYOUT ==================
col1, col2 = st.columns([2, 1])

# ================== SENARAI TARIKH ==================
with col1:
    st.subheader("📅 Senarai Tarikh")
    
    # Menggunakan container untuk scroll jika senarai terlalu panjang
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
# Pengisytiharan fungsi dialog diletakkan di luar struktur lajur untuk mengelakkan ralat Streamlit
@st.dialog("Borang Laporan")
def papar_borang(date_key):
    st.write(f"### Laporan Tarikh: {date_key}")
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

    # ================== HAID ==================
    st.subheader("🩸 Murid Haid")
    haid_count = load_json(HAID_FILE, {})

    # Menggunakan container kecil supaya borang tidak terlalu panjang ke bawah
    with st.container(height=250):
        for m in MURID:
            jumlah_hari = haid_count.get(m, 0)
            colH1, colH2 = st.columns([5, 1])
            with colH1:
                st.write(f"{m} ({jumlah_hari})")
            with colH2:
                if st.button("➕", key=f"haid_{m}_{date_key}"):
                    haid_count[m] = jumlah_hari + 1
                    save_json(HAID_FILE, haid_count, "update haid")
                    st.rerun()

    st.markdown("---")

    # ================== SIMPAN ==================
    if st.button("💾 Simpan Laporan", use_container_width=True, key="btn_save_laporan"):
        st.session_state.data[date_key] = {
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "aduan_list": aduan_list
        }
        save_json(FILE_PATH, st.session_state.data, f"update {date_key}")
        st.success("Laporan berjaya disimpan!")
        st.session_state.active_date = None # Tutup atau reset active date selepas simpan
        st.rerun()

# Kemas kini panggilan dialog secara automatik jika ada tarikh aktif dipilih
if st.session_state.active_date:
    papar_borang(st.session_state.active_date)

# ================== RUMUSAN HAID & ADUAN (COL 2) ==================
with col2:
    st.subheader("📊 Rumusan Haid Keseluruhan")
    haid_count = load_json(HAID_FILE, {})

    if haid_count:
        for nama, jumlah in sorted(haid_count.items(), key=lambda x: x[1], reverse=True):
            if jumlah > 0:
                if jumlah >= 9:
                    st.markdown(f'<div style="color:red; font-weight:bold; font-size:16px;">🚨 {nama} ({jumlah} Hari)</div>', unsafe_allow_html=True)
                else:
                    st.write(f"👩‍🦰 {nama} ({jumlah} Hari)")
    else:
        st.info("Tiada rekod haid.")

    st.markdown("---")

    if st.button("🔄 Reset Haid Bulan Baru", use_container_width=True, key="btn_reset_haid"):
        save_json(HAID_FILE, {}, "reset haid")
        st.success("Rekod haid telah direset")
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
    save_json(FILE_PATH, {}, "RESET semua")
    save_json(HAID_FILE, {}, "RESET semua haid")
    st.rerun()