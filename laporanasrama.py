import streamlit as st
import datetime
import json
import base64
from github import Github

st.set_page_config(page_title="Laporan Asrama SMKSMS1", layout="wide")
st.title("📋 Laporan Asrama SMKSMS1")

# ================== SENARAI MURID (NAMA PANJANG) ==================
MURID = [
    "DHIYA AMNI QAISARA BINTI ADDIE FAIZAL", "NURIN NAJWASHADRINA BINTI MUHAMAD",
    "NUR AIRIS HERYNA BINTI HAJRI HAIRI", "NUR ZULLAIFATUL IZZATI",
    "QAISARA SAFIYYAH BINTI HASBULLAH", "NUR AINUL SAKINAH BINTI MUHD NASIR",
    "QASEH NUR ELLYSHA BINTI SHAIREL ANUAR", "AMANDA UQAISHA BINTI ABDUL FATTAH",
    "UMMU BAARIK JALILAH BINTI MOHD NAZIF", "AMNI DAHLIA BINTI MUHAMMAD SAFUAN",
    "NURUL SHUHADA BINTI FADZDIL", "DAMIA NUR UMAIRAH BINTI MUHAMADSHAH AZLAN",
    "NURUL HAJAR BATRISYIA BINTI ABDULLAH", "SITI NUR ZAHIRAH BINTI MUHAMAD FITRI",
    "NUR FATIHAH DAMIASARA BINTI MOHD YUSRI", "SYAHIDATUL MUNAWWARAH BINTI SALLEH",
    "NUR ARRISA QAIREN BINTI MOHD AZROLAMIN", "NURIN AIREN AQILAH BINTI MOHD ZAIDI",
    "NUR ALYAA SAFFIYA BINTI MOHAMED FAUZI", "RAUDHAH MUNAWWARAH MUTAMMIMAH BINTI MOHAMMAD IN'AAMULLAH",
    "NUR AMNI NADHIRAH BINTI NASRUL", "NURUL ASYIKIN BINTI MOHD FADZLI",
    "KHAIYISAH LIYANA BINTI SABRI", "NUR AMANI DAMIA BINTI HALIL",
    "NUR DAMIA DAYANA BINTI AIDRUS", "NUR DANIA ALEESHA BINTI SAMSURI",
    "AUNY HUMAIRAH BINTI MOHD ZAIN", "NURUL HUSNA BINTI ZAIRUL AMIN",
    "SAIDATUL SAFEERA BT NORMAN SHAH", "AINNUR HUMAIRA BINTI HAMDAN",
    "NURUL SYUHADA ERINA BINTI HISHAMUDIN", "NUR FATIHAH BINTI SHAFIZUDEN",
    "NURUL HANIM UMAIRAH BINTI ROSLI", "NUR AMANINA BINTI AZMAN",
    "NUR NAJA SYIFA BINTI MAHADAY", "NURUL AIDA BINTI LAILI"
]

# Mapping: Nama lama (pendek) -> Nama baru (panjang)
NAME_MAP = {
    "AUNY HUMAIRAH": "AUNY HUMAIRAH BINTI MOHD ZAIN", "NURUL AIDA": "NURUL AIDA BINTI LAILI",
    "DHIYA AMNI": "DHIYA AMNI QAISARA BINTI ADDIE FAIZAL", "NURIN NAJWA": "NURIN NAJWASHADRINA BINTI MUHAMAD",
    "DANIA": "NUR DANIA ALEESHA BINTI SAMSURI", "HAJAR BATRISYIA": "NURUL HAJAR BATRISYIA BINTI ABDULLAH",
    "DAMIA": "DAMIA NUR UMAIRAH BINTI MUHAMADSHAH AZLAN", "QASEH ELLYSHA": "QASEH NUR ELLYSHA BINTI SHAIREL ANUAR",
    "AIRIS": "NUR AIRIS HERYNA BINTI HAJRI HAIRI", "AINNUR HUMAIRA": "AINNUR HUMAIRA BINTI HAMDAN",
    "SHUHADA": "NURUL SHUHADA BINTI FADZDIL", "QAISARA": "QAISARA SAFIYYAH BINTI HASBULLAH",
    "ARISSA QAIREN": "NUR ARRISA QAIREN BINTI MOHD AZROLAMIN", "KHAIYISAH": "KHAIYISAH LIYANA BINTI SABRI",
    "NURIN AIREN": "NURIN AIREN AQILAH BINTI MOHD ZAIDI", "FATIHAH DAMIASARA": "NUR FATIHAH DAMIASARA BINTI MOHD YUSRI",
    "NURZAHIRAH": "SITI NUR ZAHIRAH BINTI MUHAMAD FITRI", "AMNI NADHIRAH": "NUR AMNI NADHIRAH BINTI NASRUL",
    "NURUL ASYIKIN": "NURUL ASYIKIN BINTI MOHD FADZLI", "SYAHIDATUL": "SYAHIDATUL MUNAWWARAH BINTI SALLEH",
    "AMNI DAHLIA": "AMNI DAHLIA BINTI MUHAMMAD SAFUAN", "RAUDHAH": "RAUDHAH MUNAWWARAH MUTAMMIMAH BINTI MOHAMMAD IN'AAMULLAH",
    "ALYAA": "NUR ALYAA SAFFIYA BINTI MOHAMED FAUZI", "NUR FATIHAH": "NUR FATIHAH BINTI SHAFIZUDEN",
    "NAJA SYIFA": "NUR NAJA SYIFA BINTI MAHADAY", "SAFEERA": "SAIDATUL SAFEERA BT NORMAN SHAH",
    "DAMIA DAYANA": "NUR DAMIA DAYANA BINTI AIDRUS", "SYUHADA ERINA": "NURUL SYUHADA ERINA BINTI HISHAMUDIN",
    "AMANINA": "NUR AMANINA BINTI AZMAN", "HANIM": "NURUL HANIM UMAIRAH BINTI ROSLI",
    "NURUL HUSNA": "NURUL HUSNA BINTI ZAIRUL AMIN", "ZULAIFATUL": "NUR ZULLAIFATUL IZZATI",
    "AINUL SAKINAH": "NUR AINUL SAKINAH BINTI MUHD NASIR", "UMMU BARIK": "UMMU BAARIK JALILAH BINTI MOHD NAZIF",
    "AMANDA": "AMANDA UQAISHA BINTI ABDUL FATTAH", "AMANI": "NUR AMANI DAMIA BINTI HALIL"
}

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def ambil_data_dari_github():
    try:
        file_content = repo.get_contents(FILE_PATH)
        if file_content.size <= 2: return {}
        blob = repo.get_git_blob(file_content.sha)
        return json.loads(base64.b64decode(blob.content).decode("utf-8"))
    except Exception as e: return {}

def hantar_data_ke_github(data_baru, msg):
    file = repo.get_contents(FILE_PATH)
    json_bytes = json.dumps(data_baru, indent=4).encode("utf-8")
    repo.update_file(path=FILE_PATH, message=msg, content=json_bytes, sha=file.sha)
    st.session_state.data = data_baru

if "data" not in st.session_state or not st.session_state.data: st.session_state.data = ambil_data_dari_github()
if "active_date" not in st.session_state: st.session_state.active_date = None

def gen_dates():
    start = datetime.date(2026, 6, 1)
    end = datetime.date(2026, 12, 5)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out

all_dates = gen_dates()

# LOGIK RUMUSAN BULANAN
def kira_rumusan_haid_bulanan():
    haid_jun, haid_julai = {}, {}
    if st.session_state.data:
        for date_str, info in st.session_state.data.items():
            try: d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except: continue
            haid_list = info.get("haid_hari_ini", info.get("haid_data", {}))
            if isinstance(haid_list, dict):
                for m, v in haid_list.items():
                    nama = NAME_MAP.get(m, m)
                    if v > 0:
                        if d.month == 6: haid_jun[nama] = haid_jun.get(nama, 0) + 1
                        elif d.month == 7: haid_julai[nama] = haid_julai.get(nama, 0) + 1
    return haid_jun, haid_julai

def kira_rumusan_salah_laku_keseluruhan():
    total = {}
    if st.session_state.data:
        for info in st.session_state.data.values():
            for kes in info.get("salah_laku_list", info.get("aduan_list", [])):
                nama = NAME_MAP.get(kes.get("nama"), kes.get("nama"))
                if nama: total[nama] = total.get(nama, 0) + 1
    return total

# LAYOUT
col1, col2 = st.columns([2.5, 1])
with col1:
    with st.container(height=650):
        lajur = st.columns(5)
        for idx, d in enumerate(all_dates):
            key = d.strftime("%Y-%m-%d")
            color = "🟢" if (st.session_state.data and key in st.session_state.data) else "🔴"
            if lajur[idx % 5].button(f"{color} {key}", key=f"btn_{key}", use_container_width=True):
                st.session_state.active_date = key
                st.rerun()

@st.dialog("Borang Laporan Harian Warden", width="large")
def papar_popup_laporan(date_key):
    existing = dict(st.session_state.data.get(date_key, {}))
    nama = st.text_input("Nama Warden", existing.get("nama_warden", ""))
    oncall = st.text_input("Warden Oncall", existing.get("oncall", ""))
    pilihan_haid = st.multiselect("Pilih Murid Haid:", options=MURID, default=[m for m in existing.get("haid_hari_ini", {}).keys() if m in MURID])
    if st.button("Simpan"):
        existing.update({"nama_warden": nama, "oncall": oncall, "haid_hari_ini": {m: 1 for m in pilihan_haid}})
        data = ambil_data_dari_github()
        data[date_key] = existing
        hantar_data_ke_github(data, f"Update {date_key}")
        st.rerun()

if st.session_state.active_date: papar_popup_laporan(st.session_state.active_date)

with col2:
    st.markdown("### 📊 Rumusan")
    res_jun, res_jul = kira_rumusan_haid_bulanan()
    st.write("**🩸 Haid Bulan 6 (> 8 Hari):**")
    for n, b in res_jun.items():
        if b > 8: st.write(f"{n} ({b} Hari)")
    st.write("**🩸 Haid Bulan 7 (Terkumpul):**")
    for n, b in res_jul.items():
        if b > 0: st.write(f"{n} ({b} Hari)")