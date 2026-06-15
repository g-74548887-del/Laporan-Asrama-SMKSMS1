```python
import streamlit as st
import datetime
import json
from github import Github

st.set_page_config(page_title="Laporan Warden", layout="wide")
st.title("📋 Laporan Warden")

# ================== SENARAI MURID ==================
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

    # START BULAN 6
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

    for d in all_dates:

        key = d.strftime("%Y-%m-%d")

        color = "🟢" if key in st.session_state.data else "🔴"

        if st.button(
            f"{color} {key}",
            key=key,
            use_container_width=True
        ):
            open_date(key)
            st.rerun()

# ================== FORM ==================
if st.session_state.active_date:

    date_key = st.session_state.active_date

    @st.dialog(f"Laporan {date_key}")
    def form():

        existing = st.session_state.data.get(date_key, {})

        # ================== MAKLUMAT ==================
        nama = st.text_input(
            "Nama Warden",
            existing.get("nama_warden", "")
        )

        oncall = st.text_input(
            "Warden Oncall",
            existing.get("oncall", "")
        )

        jumlah = st.number_input(
            "Jumlah Murid",
            min_value=0,
            value=existing.get("jumlah_murid", 0)
        )

        tiada = st.text_area(
            "Murid Tiada / Sebab",
            existing.get("murid_tiada", "")
        )

        masa = st.text_input(
            "Masa Rondaan",
            existing.get("masa_rondaan", "")
        )

        st.markdown("---")

        # ================== ADUAN ==================
        st.subheader("📌 Aduan Murid")

        aduan_list = existing.get("aduan_list", [])

        murid_pilih = st.selectbox(
            "Nama Murid",
            MURID
        )

        aduan_text = st.text_area("Aduan")

        if st.button("➕ Tambah Aduan"):

            aduan_list.append({
                "nama": murid_pilih,
                "aduan": aduan_text
            })

            existing["aduan_list"] = aduan_list

            st.session_state.data[date_key] = existing

            save_json(
                FILE_PATH,
                st.session_state.data,
                "update aduan"
            )

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

                    if st.button(
                        "❌",
                        key=f"del_{nama_murid}"
                    ):

                        aduan_list = [
                            a for a in aduan_list
                            if a["nama"] != nama_murid
                        ]

                        existing["aduan_list"] = aduan_list

                        st.session_state.data[date_key] = existing

                        save_json(
                            FILE_PATH,
                            st.session_state.data,
                            "delete aduan"
                        )

                        st.rerun()

        else:
            st.info("Tiada aduan")

        st.markdown("---")

        # ================== HAID ==================
        st.subheader("🩸 Murid Haid")

        haid_data = existing.get("haid_data", {})

        if st.button(
            "🩸 Buka Senarai Haid",
            use_container_width=True
        ):
            st.session_state.show_haid_popup = True

        if st.session_state.show_haid_popup:

            st.info("Tick murid yang haid")

            selected_haid = {}

            for m in MURID:

                selected_haid[m] = st.checkbox(
                    m,
                    value=haid_data.get(m, False),
                    key=f"haid_{date_key}_{m}"
                )

            colA, colB = st.columns(2)

            with colA:

                if st.button("💾 Simpan Haid"):

                    existing["haid_data"] = selected_haid

                    st.session_state.data[date_key] = existing

                    save_json(
                        FILE_PATH,
                        st.session_state.data,
                        "update haid"
                    )

                    st.session_state.show_haid_popup = False

                    st.success("Data haid disimpan")

                    st.rerun()

            with colB:

                if st.button("❌ Tutup"):

                    st.session_state.show_haid_popup = False
                    st.rerun()

        st.markdown("---")

        # ================== PROGRAM ==================
        program = st.text_area(
            "Program",
            existing.get("catatan_program", "")
        )

        # ================== BUTTON ==================
        colH1, colH2 = st.columns(2)

        with colH1:

            if st.button("Hantar"):

                st.session_state.data[date_key] = {
                    "nama_warden": nama,
                    "oncall": oncall,
                    "jumlah_murid": jumlah,
                    "murid_tiada": tiada,
                    "masa_rondaan": masa,
                    "catatan_program": program,
                    "aduan_list": aduan_list,
                    "haid_data": existing.get("haid_data", {})
                }

                save_json(
                    FILE_PATH,
                    st.session_state.data,
                    "update laporan"
                )

                st.success("Berjaya simpan")

                st.session_state.active_date = None

                st.rerun()

        with colH2:

            if st.button("🧨 Reset Laporan (Padam)"):

                if date_key in st.session_state.data:

                    del st.session_state.data[date_key]

                    save_json(
                        FILE_PATH,
                        st.session_state.data,
                        "delete laporan"
                    )

                    st.success("Laporan dipadam")

                    st.session_state.active_date = None

                    st.rerun()

    form()

# ================== RUMUSAN HAID ==================
with col2:

    st.subheader("📊 Rumusan Haid")

    total_haid = {m: 0 for m in MURID}

    for tarikh, info in st.session_state.data.items():

        haid = info.get("haid_data", {})

        for nama, status in haid.items():

            if status:
                total_haid[nama] += 1

    for m, jumlah in sorted(
        total_haid.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        if jumlah > 0:

            colA, colB = st.columns([6,1])

            with colA:

                if jumlah >= 9:

                    st.markdown(
                        f"""
                        <div style="
                            color:red;
                            font-weight:bold;
                        ">
                            {m} ({jumlah} kali)
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:
                    st.write(f"{m} ({jumlah} kali)")

            with colB:

                if st.button(
                    "❌",
                    key=f"reset_haid_{m}"
                ):

                    for t in st.session_state.data:

                        if "haid_data" in st.session_state.data[t]:

                            st.session_state.data[t]["haid_data"][m] = False

                    save_json(
                        FILE_PATH,
                        st.session_state.data,
                        "reset haid murid"
                    )

                    st.rerun()

    st.markdown("---")

    if st.button(
        "🔄 Reset Haid Bulan Baru",
        use_container_width=True
    ):

        for t in st.session_state.data:

            if "haid_data" in st.session_state.data[t]:

                st.session_state.data[t]["haid_data"] = {}

        save_json(
            FILE_PATH,
            st.session_state.data,
            "reset haid bulan baru"
        )

        st.success("Semua rekod haid telah direset")

        st.rerun()

# ================== RUMUSAN ADUAN ==================
with col2:

    st.subheader("📌 Rumusan Aduan")

    total_aduan = {}

    for t, info in st.session_state.data.items():

        for a in info.get("aduan_list", []):

            total_aduan[a["nama"]] = (
                total_aduan.get(a["nama"], 0) + 1
            )

    for n, v in sorted(
        total_aduan.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        colA, colB = st.columns([6, 1])

        with colA:
            st.write(f"{n} ({v})")

        with colB:

            if st.button(
                "❌",
                key=f"clear_{n}"
            ):

                for t in st.session_state.data:

                    st.session_state.data[t]["aduan_list"] = [
                        a for a in st.session_state.data[t].get("aduan_list", [])
                        if a["nama"] != n
                    ]

                save_json(
                    FILE_PATH,
                    st.session_state.data,
                    "clear aduan"
                )

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
```
