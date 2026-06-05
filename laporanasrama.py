import streamlit as st
import datetime
import json
from github import Github

st.set_page_config(page_title="Laporan Warden", layout="wide")
st.title("📋 Laporan Warden")

MURID = [
    "AUNY HUMAIRAH","NURUL AIDA","DHIYA AMNI","NURIN NAJWA","DANIA",
    "HAJAR BATRISYIA","DAMIA","QASEH ELLYSHA","AIRIS","AINNUR HUMAIRA",
    "SHUHADA","QAISARA","ARISSA QAIREN","KHAIYISAH","NURIN AIREN",
    "FATIHAH DAMIASARA","NURZAHIRAH","AMNI NADHIRAH","NURUL ASYIKIN",
    "SYAHIDATUL","AMNI DAHLIA","RAUDHAH","ALYAA","NUR FATIHAH",
    "NAJA SYIFA","SAFEERA","DAMIA DAYANA","SYUHADA ERINA","NURUL HUSNA",
    "ZULAIFATUL","AINUL SAKINAH","FARZANA","UMMU BARIK","AMANDA","AMANI"
]

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"
FILE_PATH = "laporan.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def load_json(path, default):
    try:
        return json.loads(repo.get_contents(path).decoded_content.decode())
    except:
        return default

def save_json(path, data, msg):
    try:
        file = repo.get_contents(path)
        repo.update_file(path, msg, json.dumps(data, indent=4), file.sha)
    except:
        repo.create_file(path, msg, json.dumps(data, indent=4))

if "data" not in st.session_state:
    st.session_state.data = load_json(FILE_PATH, {})

if "active_date" not in st.session_state:
    st.session_state.active_date = None

if "show_haid_popup" not in st.session_state:
    st.session_state.show_haid_popup = False


def gen_dates():
    start = datetime.date(2026, 4, 1)
    end = datetime.date(2026, 11, 30)
    out = []
    while start <= end:
        out.append(start)
        start += datetime.timedelta(days=1)
    return out


all_dates = gen_dates()


def open_date(d):
    st.session_state.active_date = d


col1, col2 = st.columns([2, 1])

# ================== TARIKH ==================
with col1:
    st.subheader("📅 Senarai Tarikh")

    for d in all_dates:
        key = d.strftime("%Y-%m-%d")
        color = "🟢" if key in st.session_state.data else "🔴"

        if st.button(f"{color} {key}", key=key, use_container_width=True):
            open_date(key)
            st.rerun()


# ================== FORM ==================
if st.session_state.active_date:

    date_key = st.session_state.active_date

    @st.dialog(f"Laporan {date_key}")
    def form():

        existing = st.session_state.data.get(date_key, {})

        nama = st.text_input("Nama Warden", existing.get("nama_warden", ""))
        oncall = st.text_input("Warden Oncall", existing.get("oncall", ""))
        jumlah = st.number_input("Jumlah Murid", 0, value=existing.get("jumlah_murid", 0))
        tiada = st.text_area("Murid Tiada / Sebab", existing.get("murid_tiada", ""))
        masa = st.text_input("Masa Rondaan", existing.get("masa_rondaan", ""))

        # ================== ADUAN ==================
        st.subheader("📌 Aduan Murid")

        aduan_list = existing.get("aduan_list", [])

        murid_pilih = st.selectbox("Nama Murid", MURID)
        aduan_text = st.text_area("Aduan")

        if st.button("➕ Tambah Aduan"):
            aduan_list.append({"nama": murid_pilih, "aduan": aduan_text})
            existing["aduan_list"] = aduan_list
            st.session_state.data[date_key] = existing
            save_json(FILE_PATH, st.session_state.data, "update aduan")
            st.rerun()

        st.markdown("### 📌 Rumusan Aduan")

        kiraan = {}
        for a in aduan_list:
            kiraan[a["nama"]] = kiraan.get(a["nama"], 0) + 1

        if kiraan:
            for nama_murid, jumlah_aduan in kiraan.items():

                colA, colB = st.columns([6, 1])

                with colA:
                    st.write(f"{nama_murid} ({jumlah_aduan})")

                with colB:
                    if st.button("❌", key=f"del_{nama_murid}"):
                        aduan_list = [a for a in aduan_list if a["nama"] != nama_murid]
                        existing["aduan_list"] = aduan_list
                        st.session_state.data[date_key] = existing
                        save_json(FILE_PATH, st.session_state.data, "delete aduan")
                        st.rerun()

        else:
            st.info("Tiada aduan")

        st.markdown("---")

        # ================== HAID ==================
        st.subheader("🩸 Murid Haid")

        haid_data = existing.get("haid_data", {})

        total = {m: 0 for m in MURID}

        for t, info in st.session_state.data.items():
            for m, v in info.get("haid_data", {}).items():
                total[m] += v

        if st.button("🩸 Buka Haid", use_container_width=True):
            st.session_state.show_haid_popup = True

        if st.session_state.show_haid_popup:

            st.info("Edit haid murid")

            for m in MURID:
                haid_data[m] = st.number_input(
                    f"{m} ({total[m]})",
                    min_value=0,
                    max_value=100,
                    value=haid_data.get(m, total[m]),
                    key=f"{date_key}_{m}"
                )

            colA, colB = st.columns(2)

            with colA:
                if st.button("💾 Simpan Haid"):
                    existing["haid_data"] = haid_data
                    st.session_state.data[date_key] = existing
                    save_json(FILE_PATH, st.session_state.data, "update haid")
                    st.session_state.show_haid_popup = False
                    st.success("Disimpan")
                    st.rerun()

            with colB:
                if st.button("❌ Tutup"):
                    st.session_state.show_haid_popup = False
                    st.rerun()

        # ================== PROGRAM ==================
        program = st.text_area("Program", existing.get("catatan_program", ""))

        if st.button("Hantar"):
            st.session_state.data[date_key] = {
                "nama_warden": nama,
                "oncall": oncall,
                "jumlah_murid": jumlah,
                "murid_tiada": tiada,
                "masa_rondaan": masa,
                "catatan_program": program,
                "aduan_list": aduan_list,
                "haid_data": haid_data
            }

            save_json(FILE_PATH, st.session_state.data, "update laporan")
            st.success("Berjaya simpan")
            st.session_state.active_date = None
            st.rerun()

    form()


# ================== RUMUSAN HAID ==================
with col2:

    st.subheader("📊 Rumusan Haid")

    total = {m: 0 for m in MURID}

    for t, info in st.session_state.data.items():
        for m, v in info.get("haid_data", {}).items():
            total[m] += v

    for m, v in sorted(total.items(), key=lambda x: x[1], reverse=True):
        st.write(f"{m} ({v})")

    st.markdown("---")

    if st.button("🧹 Reset Semua Haid (Bulan Baru)", use_container_width=True):

        for t in st.session_state.data:
            if "haid_data" in st.session_state.data[t]:
                for m in MURID:
                    st.session_state.data[t]["haid_data"][m] = 0

        save_json(FILE_PATH, st.session_state.data, "reset semua haid")
        st.success("Semua haid dikosongkan")
        st.rerun()


# ================== RUMUSAN ADUAN ==================
with col2:

    st.subheader("📌 Rumusan Aduan")

    total_aduan = {}

    for t, info in st.session_state.data.items():
        for a in info.get("aduan_list", []):
            total_aduan[a["nama"]] = total_aduan.get(a["nama"], 0) + 1

    for n, v in sorted(total_aduan.items(), key=lambda x: x[1], reverse=True):
        colA, colB = st.columns([6, 1])

        with colA:
            st.write(f"{n} ({v})")

        with colB:
            if st.button("❌", key=f"clear_{n}"):
                for t in st.session_state.data:
                    st.session_state.data[t]["aduan_list"] = [
                        a for a in st.session_state.data[t].get("aduan_list", [])
                        if a["nama"] != n
                    ]
                save_json(FILE_PATH, st.session_state.data, "clear aduan")
                st.rerun()


# ================== SIDEBAR ==================
st.sidebar.header("⚙️ Control Panel")

if st.sidebar.button("🔄 Sync Data"):
    st.session_state.data = load_json(FILE_PATH, {})
    st.rerun()

if st.sidebar.button("🧨 Reset Semua Data"):
    st.session_state.data = {}
    save_json(FILE_PATH, {}, "RESET semua")
    st.rerun()