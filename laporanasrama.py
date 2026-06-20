import streamlit as st
import datetime
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Asrama SMKSMS1", layout="wide")
st.title("📋 Laporan Asrama SMKSMS1")

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

# ================== JANA SEMUA TARIKH (2026-06-08 HINGGA 2026-12-05) ==================
def gen_dates():
    start = datetime.date(2026, 6, 8)
    end = datetime.date(2026, 12, 5)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out

all_dates = gen_dates()

# ================== LOGIK PENGIRAAN RUMUSAN GLOBAL ==================
def kira_rumusan_haid_keseluruhan():
    total_haid = {m: 0 for m in MURID}
    for date_str, info in st.session_state.data.items():
        if isinstance(info, dict):
            haid_list = info.get("haid_hari_ini", info.get("haid_data", {}))
            if isinstance(haid_list, dict):
                for m, v in haid_list.items():
                    if m in total_haid and v > 0:
                        total_haid[m] += 1
    return total_haid

def kira_rumusan_salah_laku_keseluruhan():
    total_salah_laku = {m: 0 for m in MURID}
    for date_str, info in st.session_state.data.items():
        if isinstance(info, dict):
            salah_laku_list = info.get("salah_laku_list", info.get("aduan_list", []))
            if isinstance(salah_laku_list, list):
                for kes in salah_laku_list:
                    nama = kes.get("nama")
                    if nama in total_salah_laku:
                        total_salah_laku[nama] += 1
    return total_salah_laku

# LAYOUT SKRIN UTAMA
col1, col2 = st.columns([2.5, 1])

with col1:
    # DIKEMASKINI: Tiada lagi perkataan/sebutan tajuk di sini. Terus paparkan butang tarikh.
    with st.container(height=650):
        # Menyusun tarikh dalam bentuk 5 lajur (5 columns)
        lajur = st.columns(5)
        
        for idx, d in enumerate(all_dates):
            key = d.strftime("%Y-%m-%d")
            
            # Semak status kewujudan data dalam JSON untuk tukar warna
            has_data = key in st.session_state.data and isinstance(st.session_state.data[key], dict)
            color = "🟢" if has_data else "🔴"
            
            # Memasukkan butang ke lajur yang betul secara bergilir (0 hingga 4)
            sasaran_lajur = lajur[idx % 5]
            
            if sasaran_lajur.button(f"{color} {key}", key=f"list_btn_{key}", use_container_width=True):
                st.session_state.active_date = key
                st.rerun()

# ================== POPUP BORANG LAPORAN HARIAN ==================
@st.dialog("Borang Laporan Harian Warden", width="large")
def papar_popup_laporan(date_key):
    st.write(f"### 📑 Mengisi / Mengedit Laporan Tarikh: **{date_key}**")
    if date_key not in st.session_state.data:
        st.session_state.data[date_key] = {}
    existing = dict(st.session_state.data.get(date_key, {}))

    # Laporan Asas Warden
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        nama = st.text_input("Nama Warden", existing.get("nama_warden", ""))
        oncall = st.text_input("Warden Oncall", existing.get("oncall", ""))
    with col_w2:
        jumlah = st.number_input("Jumlah Murid", min_value=0, value=int(existing.get("jumlah_murid", 0)))
        masa = st.text_input("Masa Rondaan", existing.get("masa_rondaan", ""))
        
    tiada = st.text_area("Murid Tiada / Sebab", existing.get("murid_tiada", ""))
    nama_program = st.text_input("Nama Program", existing.get("nama_program", existing.get("catatan_program", "")))

    st.markdown("---")
    
    # Rekod Murid Haid
    st.subheader("🩸 Rekod Murid Haid")
    ex_haid_popup = []
    haid_source = existing.get("haid_hari_ini", existing.get("haid_data", {}))
    if isinstance(haid_source, dict):
        ex_haid_popup = [m for m, v in haid_source.items() if v > 0]
        
    pilihan_haid_popup = st.multiselect(
        "Pilih Nama Murid Haid (Maksimum 15 Orang):", options=MURID, default=ex_haid_popup, max_selections=15, key=f"pop_haid_{date_key}"
    )

    st.markdown("---")
    
    # Rekod Kes Salah Laku
    st.subheader("⚠️ Rekod Kes Salah Laku")
    salah_laku_list = existing.get("salah_laku_list", existing.get("aduan_list", []))
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
            butiran = item.get("kesalahan", item.get("aduan", ""))
            st.write(f" {idx+1}. **{item['nama']}** — {butiran}")

    st.markdown("---")
    
    # Muat Naik Gambar
    st.subheader("📸 Lampiran Laporan (Maksimum 2 Gambar)")
    img_list = existing.get("images_base64", existing.get("program_images", []))
    if not isinstance(img_list, list): img_list = []
    
    uploaded_files = st.file_uploader("Pilih gambar laporan asrama", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="uploader_gambar")
    
    if uploaded_files:
        img_list = []
        for f in uploaded_files[:2]:
            bytes_data = f.read()
            b64_str = base64.b64encode(bytes_data).decode()
            img_list.append(b64_str)

    if img_list:
        st.write("Preview Gambar Sedia Ada:")
        cols_img = st.columns(len(img_list))
        for idx, b64_img in enumerate(img_list):
            if b64_img:
                try:
                    cols_img[idx].image(base64.b64decode(b64_img), use_container_width=True)
                except:
                    pass

    st.markdown("---")
    if st.button("💾 Simpan Semua Rekod Laporan", use_container_width=True):
        existing.update({
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "catatan_program": nama_program,
            "nama_program": nama_program,
            "haid_hari_ini": {m: 1 for m in pilihan_haid_popup},
            "salah_laku_list": salah_laku_list,
            "images_base64": img_list
        })
        st.session_state.data[date_key] = existing
        save_json_global(FILE_PATH, st.session_state.data, f"Simpan laporan lengkap bertarikh {date_key}")
        st.success("Berjaya disimpan!")
        st.session_state.active_date = None
        st.rerun()

if st.session_state.active_date:
    papar_popup_laporan(st.session_state.active_date)

# ================== RUMUSAN DI SEBELAH KANAN ==================
with col2:
    st.markdown("### 📊 Rumusan Keseluruhan Data")
    
    # Rumusan Murid Haid Keseluruhan Tarikh
    st.write("**🩸 Bilangan Hari Haid (Terkumpul):**")
    res_haid = kira_rumusan_haid_keseluruhan()
    ada_haid = False
    for nama, bil in sorted(res_haid.items(), key=lambda x: x[1], reverse=True):
        if bil > 0:
            ada_haid = True
            st.write(f"👩‍🦰 {nama} ({bil} Hari)")
    if not ada_haid:
        st.info("Tiada rekod data murid haid ditemui dalam fail JSON.")

    st.markdown("---")
    
    # Rumusan Kes Salah Laku Keseluruhan Tarikh
    st.write("**⚠️ Rumusan Kes Salah Laku:**")
    res_sl = kira_rumusan_salah_laku_keseluruhan()
    ada_sl = False
    for nama, bil in sorted(res_sl.items(), key=lambda x: x[1], reverse=True):
        if bil > 0:
            ada_sl = True
            st.write(f"❌ {nama} ({bil} Kali)")
    if not ada_sl:
        st.info("Tiada kes salah laku direkodkan dalam fail JSON.")

    st.markdown("---")
    if st.sidebar.button("🔄 Ambil Data Terkini GitHub", use_container_width=True):
        st.session_state.data = load_json(FILE_PATH, {})
        st.rerun()