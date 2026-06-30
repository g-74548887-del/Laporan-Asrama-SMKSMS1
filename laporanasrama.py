import streamlit as st
import datetime
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Asrama SMKSMS1", layout="wide")
st.title("📋 Laporan Asrama SMKSMS1")

# ================== SENARAI MURID ==================
MURID = [
    "AUNY HUMAIRAH", "NURUL AIDA", "DHIYA AMNI", "NURIN NAJWA", "DANIA",
    "HAJAR BATRISYIA", "DAMIA", "QASEH ELLYSHA", "AIRIS", "AINNUR HUMAIRA",
    "SHUHADA", "QAISARA", "ARISSA QAIREN", "KHAIYISAH", "NURIN AIREN",
    "FATIHAH DAMIASARA", "NURZAHIRAH", "AMNI NADHIRAH", "NURUL ASYIKIN",
    "SYAHIDATUL", "AMNI DAHLIA", "RAUDHAH", "ALYAA", "NUR FATIHAH",
    "NAJA SYIFA", "SAFEERA", "DAMIA DAYANA", "SYUHADA ERINA", "AMANINA", "HANIM", "NURUL HUSNA",
    "ZULAIFATUL", "AINUL SAKINAH", "FARZANA", "UMMU BARIK", "AMANDA", "AMANI"
]

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ================== FUNGSI BACA GITHUB ==================
def ambil_data_dari_github():
    try:
        file_content = repo.get_contents(FILE_PATH)
        
        if file_content.size <= 2:
            return {}
            
        blob = repo.get_git_blob(file_content.sha)
        raw_content = blob.content
        
        decoded_bytes = base64.b64decode(raw_content)
        content_str = decoded_bytes.decode("utf-8")
        
        data_json = json.loads(content_str)
        
        if isinstance(data_json, dict):
            return data_json
        return {}
    except Exception as e:
        st.error(f"⚠️ Ralat Membaca GitHub: {e}")
        return {}

# PENGUNCI MEMORI SESI STREAMLIT
if "data" not in st.session_state or not st.session_state.data:
    st.session_state.data = ambil_data_dari_github()

if "active_date" not in st.session_state:
    st.session_state.active_date = None

# ================== FUNGSI SIMPAN GITHUB ==================
def hantar_data_ke_github(data_baru, msg):
    try:
        file = repo.get_contents(FILE_PATH)
        
        json_string = json.dumps(data_baru, indent=4)
        json_bytes = json_string.encode("utf-8")
        
        repo.update_file(
            path=FILE_PATH,
            message=msg,
            content=json_bytes,
            sha=file.sha
        )
        
        st.session_state.data = data_baru
        st.toast("💾 Data berjaya dikunci dan disimpan ke GitHub!", icon="✅")
    except Exception as e:
        st.error(f"❌ Ralat Sistem Simpanan GitHub: {e}")

# ================== JANA SEMUA TARIKH ==================
def gen_dates():
    start = datetime.date(2026, 6, 1)
    end = datetime.date(2026, 12, 5)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out

all_dates = gen_dates()

# ================== LOGIK RUMUSAN ==================
def kira_rumusan_haid_keseluruhan():
    total_haid = {}
    if st.session_state.data:
        for date_str, info in st.session_state.data.items():
            if isinstance(info, dict):
                haid_list = info.get("haid_hari_ini", info.get("haid_data", {}))
                if isinstance(haid_list, dict):
                    for m, v in haid_list.items():
                        if v > 0:
                            total_haid[m] = total_haid.get(m, 0) + 1
    return total_haid

def kira_rumusan_salah_laku_keseluruhan():
    total_salah_laku = {}
    if st.session_state.data:
        for date_str, info in st.session_state.data.items():
            if isinstance(info, dict):
                salah_laku_list = info.get("salah_laku_list", info.get("aduan_list", []))
                if isinstance(salah_laku_list, list):
                    for kes in salah_laku_list:
                        nama = kes.get("nama")
                        if nama:
                            total_salah_laku[nama] = total_salah_laku.get(nama, 0) + 1
    return total_salah_laku

# LAYOUT SKRIN UTAMA
col1, col2 = st.columns([2.5, 1])

with col1:
    with st.container(height=650):
        lajur = st.columns(5)
        total_items = len(all_dates)
        per_col = (total_items + 4) // 5
        
        for col_idx in range(5):
            with lajur[col_idx]:
                start_idx = col_idx * per_col
                end_idx = min(start_idx + per_col, total_items)
                
                for idx in range(start_idx, end_idx):
                    d = all_dates[idx]
                    key = d.strftime("%Y-%m-%d")
                    
                    has_data = False
                    if st.session_state.data and key in st.session_state.data:
                        isi_data = st.session_state.data[key]
                        if isinstance(isi_data, dict) and len(isi_data) > 0:
                            has_data = True
                    
                    color = "🟢" if has_data else "🔴"
                    
                    if st.button(f"{color} {key}", key=f"list_btn_{key}", use_container_width=True):
                        st.session_state.active_date = key
                        st.rerun()

# ================== POPUP BORANG LAPORAN HARIAN (BAIKI) ==================
@st.dialog("Borang Laporan Harian Warden", width="large")
def papar_popup_laporan(date_key):
    st.write(f"### 📑 Mengisi / Mengedit Laporan Tarikh: **{date_key}**")
    
    if date_key not in st.session_state.data:
        st.session_state.data[date_key] = {}
        
    existing = dict(st.session_state.data.get(date_key, {}))

    # Sediakan pemegang memori gambar sementara khusus untuk sesi popup ini
    if "temp_images" not in st.session_state:
        st.session_state.temp_images = existing.get("images_base64", [])

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
    st.subheader("🩸 Rekod Murid Haid")
    
    ex_haid_popup = []
    haid_source = existing.get("haid_hari_ini", existing.get("haid_data", {}))
    if isinstance(haid_source, dict):
        ex_haid_popup = [m for m, v in haid_source.items() if v > 0]
        
    pilihan_haid_popup = st.multiselect(
        "Pilih Nama Murid Haid:", options=MURID, default=[m for m in ex_haid_popup if m in MURID], key=f"pop_haid_{date_key}"
    )

    st.markdown("---")
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
    st.subheader("📸 Lampiran Laporan (Maksimum 2 Gambar)")
    
    uploaded_files = st.file_uploader("Pilih gambar laporan asrama", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="uploader_gambar")
    
    # Jika ada muat naik fail baru, kemas kini st.session_state.temp_images
    if uploaded_files:
        st.session_state.temp_images = []
        for f in uploaded_files[:2]:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
            st.session_state.temp_images.append(b64_str)

    # Papar gambar sedia ada dari temp_images (tidak akan hilang jika berlaku rerun dialog)
    if st.session_state.temp_images:
        cols_img = st.columns(len(st.session_state.temp_images))
        for idx, b64_img in enumerate(st.session_state.temp_images):
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
            "images_base64": st.session_state.temp_images  # Ikat terus ke data induk
        })
        
        # Tarik data terkini daripada GitHub terlebih dahulu (mengelakkan overwrite data warden lain)
        pangkalan_induk = ambil_data_dari_github()
        pangkalan_induk[date_key] = existing
        
        # Hantar semula fail kemaskini lengkap ke GitHub
        hantar_data_ke_github(pangkalan_induk, f"Kemaskini laporan tarikh {date_key}")
        
        # Buang cache imej sementara dan tutup modal
        if "temp_images" in st.session_state:
            del st.session_state.temp_images
            
        st.session_state.active_date = None
        st.rerun()

# PAPAR DIALOG JIKA AKTIF
if st.session_state.active_date:
    papar_popup_laporan(st.session_state.active_date)

# ================== RUMUSAN DI SEBELAH KANAN ==================
with col2:
    st.markdown("### 📊 Rumusan Keseluruhan Data")
    
    st.write("**🩸 Bilangan Hari Haid (Terkumpul):**")
    res_haid = kira_rumusan_haid_keseluruhan()
    ada_haid = False
    for nama, bil in sorted(res_haid.items(), key=lambda x: x[1], reverse=True):
        if bil > 0:
            ada_haid = True
            st.write(f"👩‍🦰 {nama} ({bil} Hari)")
    if not ada_haid:
        st.info("Tiada rekod data murid haid.")

    st.markdown("---")
    st.write("**⚠️ Rumusan Kes Salah Laku:**")
    res_sl = kira_rumusan_salah_laku_keseluruhan()
    ada_sl = False
    for nama, bil in sorted(res_sl.items(), key=lambda x: x[1], reverse=True):
        if bil > 0:
            ada_sl = True
            st.write(f"❌ {nama} ({bil} Kali)")
    if not ada_sl:
        st.info("Tiada kes salah laku.")

    st.markdown("---")
    if st.button("🔄 Tarik Paksa Data GitHub", use_container_width=True):
        st.session_state.data = ambil_data_dari_github()
        st.rerun()