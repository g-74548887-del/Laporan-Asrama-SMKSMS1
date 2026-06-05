```python
import streamlit as st
import datetime
import json
from github import Github

# ================== PAGE ==================
st.set_page_config(
    page_title="Laporan Warden",
    layout="wide"
)

st.title("📋 Laporan Warden")

# ================== SENARAI MURID ==================
MURID = [
    "AUNY HUMAIRAH",
    "NURUL AIDA",
    "DHIYA AMNI",
    "NURIN NAJWA",
    "DANIA",
    "HAJAR BATRISYIA",
    "DAMIA",
    "QASEH ELLYSHA",
    "AIRIS",
    "AINNUR HUMAIRA",
    "SHUHADA",
    "QAISARA",
    "ARISSA QAIREN",
    "KHAIYISAH",
    "NURIN AIREN",
    "FATIHAH DAMIASARA",
    "NURZAHIRAH",
    "AMNI NADHIRAH",
    "NURUL ASYIKIN",
    "SYAHIDATUL",
    "AMNI DAHLIA",
    "RAUDHAH",
    "ALYAA",
    "NUR FATIHAH",
    "NAJA SYIFA",
    "SAFEERA",
    "DAMIA DAYANA",
    "SYUHADA ERINA",
    "NURUL HUSNA",
    "ZULAIFATUL",
    "AINUL SAKINAH",
    "FARZANA",
    "UMMU BARIK",
    "AMANDA",
    "AMANI"
]

# ================== GITHUB ==================
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

REPO_NAME = "g-74548887-del/Laporan-Asrama-SMKSMS1"

FILE_PATH = "laporan.json"

g = Github(GITHUB_TOKEN)

repo = g.get_repo(REPO_NAME)

# ================== LOAD ==================
def load_json(path, default):

    try:

        file = repo.get_contents(path)

        return json.loads(
            file.decoded_content.decode()
        )

    except:

        return default

# ================== SAVE ==================
def save_json(path, data, msg):

    try:

        file = repo.get_contents(path)

        repo.update_file(
            path,
            msg,
            json.dumps(data, indent=4),
            file.sha
        )

    except:

        repo.create_file(
            path,
            msg,
            json.dumps(data, indent=4)
        )

# ================== SESSION ==================
if "data" not in st.session_state:

    st.session_state.data = load_json(
        FILE_PATH,
        {}
    )

if "active_date" not in st.session_state:

    st.session_state.active_date = None

if "show_haid_popup" not in st.session_state:

    st.session_state.show_haid_popup = False

# ================== DATE ==================
def gen_dates():

    start = datetime.date(2026, 4, 1)

    end = datetime.date(2026, 11, 30)

    out = []

    while start <= end:

        out.append(start)

        start += datetime.timedelta(days=1)

    return out

all_dates = gen_dates()

# ================== OPEN DATE ==================
def open_date(d):

    st.session_state.active_date = d

# ================== LAYOUT ==================
col1, col2 = st.columns([2,1])

# ================== TARIKH ==================
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

        existing = st.session_state.data.get(
            date_key,
            {}
        )

        # ================== INPUT ==================
        nama = st.text_input(
            "Nama Warden",
            value=existing.get(
                "nama_warden",
                ""
            )
        )

        oncall = st.text_input(
            "Warden Oncall",
            value=existing.get(
                "oncall",
                ""
            )
        )

        jumlah = st.number_input(
            "Jumlah Murid",
            min_value=0,
            value=existing.get(
                "jumlah_murid",
                0
            )
        )

        tiada = st.text_area(
            "Murid Tiada / Sebab",
            value=existing.get(
                "murid_tiada",
                ""
            ),
            height=120
        )

        masa = st.text_input(
            "Masa Rondaan",
            value=existing.get(
                "masa_rondaan",
                ""
            )
        )

        st.markdown("---")

        # ================== ADUAN ==================
        st.subheader("📌 Aduan Murid")

        aduan_list = existing.get(
            "aduan_list",
            []
        )

        selected_murid = st.selectbox(
            "Pilih Nama Murid",
            MURID
        )

        aduan_text = st.text_area(
            "Penjelasan Aduan"
        )

        if st.button("➕ Tambah Aduan"):

            aduan_list.append({

                "nama": selected_murid,

                "aduan": aduan_text

            })

            existing["aduan_list"] = aduan_list

            st.session_state.data[date_key] = existing

            save_json(
                FILE_PATH,
                st.session_state.data,
                "update aduan"
            )

            st.success("Aduan berjaya ditambah")

            st.rerun()

        st.markdown("### 📋 Senarai Aduan")

        kiraan = {}

        for item in aduan_list:

            nama_murid = item["nama"]

            if nama_murid not in kiraan:

                kiraan[nama_murid] = 0

            kiraan[nama_murid] += 1

        if kiraan:

            sorted_kiraan = sorted(
                kiraan.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for nama_murid, jumlah_aduan in sorted_kiraan:

                with st.expander(
                    f"{nama_murid} ({jumlah_aduan})"
                ):

                    for item in aduan_list:

                        if item["nama"] == nama_murid:

                            st.write(
                                "•",
                                item["aduan"]
                            )

        else:

            st.info("Tiada aduan")

        st.markdown("---")

        # ================== HAID ==================
        st.subheader("🩸 Murid Haid")

        haid_data = existing.get(
            "haid_data",
            {}
        )

        # kira jumlah keseluruhan
        total_haid_semua = {}

        for murid in MURID:

            total_haid_semua[murid] = 0

        for tarikh, info in st.session_state.data.items():

            hd = info.get(
                "haid_data",
                {}
            )

            for murid, hari in hd.items():

                total_haid_semua[murid] += hari

        # button popup
        if st.button(
            "🩸 Buka Senarai Murid Haid",
            use_container_width=True
        ):

            st.session_state.show_haid_popup = True

        # popup
        if st.session_state.show_haid_popup:

            @st.dialog("🩸 Senarai Murid Haid")
            def popup_haid():

                st.caption(
                    "Nombor dalam kurungan ialah jumlah terkumpul."
                )

                for murid in MURID:

                    jumlah_lama = total_haid_semua.get(
                        murid,
                        0
                    )

                    default_hari = haid_data.get(
                        murid,
                        jumlah_lama
                    )

                    hari = st.number_input(
                        f"{murid} ({jumlah_lama})",
                        min_value=0,
                        max_value=100,
                        value=default_hari,
                        step=1,
                        key=f"haid_{date_key}_{murid}"
                    )

                    haid_data[murid] = hari

                st.markdown("---")

                if st.button(
                    "💾 Simpan Data Haid",
                    use_container_width=True
                ):

                    existing["haid_data"] = haid_data

                    st.session_state.data[
                        date_key
                    ] = existing

                    save_json(
                        FILE_PATH,
                        st.session_state.data,
                        "update haid"
                    )

                    st.success(
                        "Data haid berjaya disimpan"
                    )

                    st.session_state.show_haid_popup = False

                    st.rerun()

                if st.button(
                    "❌ Tutup",
                    use_container_width=True
                ):

                    st.session_state.show_haid_popup = False

                    st.rerun()

            popup_haid()

        st.markdown("---")

        # ================== PROGRAM ==================
        program = st.text_area(
            "Nama Program",
            value=existing.get(
                "catatan_program",
                ""
            ),
            height=100
        )

        # ================== HANTAR ==================
        if st.button("✅ Hantar"):

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

            save_json(
                FILE_PATH,
                st.session_state.data,
                "update laporan"
            )

            st.success(
                "Laporan berjaya dihantar"
            )

            st.session_state.active_date = None

            st.rerun()

        st.markdown("---")

        # ================== RESET ==================
        if st.button("🧨 Reset Tarikh Ini"):

            if date_key in st.session_state.data:

                del st.session_state.data[
                    date_key
                ]

                save_json(
                    FILE_PATH,
                    st.session_state.data,
                    "delete tarikh"
                )

            st.success(
                "Tarikh telah dikosongkan"
            )

            st.session_state.active_date = None

            st.rerun()

    form()

# ================== RUMUSAN ==================
with col2:

    st.subheader("📊 Rumusan Haid")

    total_haid = {}

    for murid in MURID:

        total_haid[murid] = 0

    for tarikh, info in st.session_state.data.items():

        haid_data = info.get(
            "haid_data",
            {}
        )

        for murid, hari in haid_data.items():

            total_haid[murid] += hari

    sorted_total = sorted(
        total_haid.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for murid, jumlah in sorted_total:

        st.write(f"{murid} ({jumlah})")

    st.markdown("---")

    st.subheader("📌 Rumusan Aduan")

    kiraan_aduan = {}

    for tarikh, info in st.session_state.data.items():

        aduan_list = info.get(
            "aduan_list",
            []
        )

        for item in aduan_list:

            nama = item["nama"]

            if nama not in kiraan_aduan:

                kiraan_aduan[nama] = 0

            kiraan_aduan[nama] += 1

    sorted_aduan = sorted(
        kiraan_aduan.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for nama, jumlah in sorted_aduan:

        st.write(f"{nama} ({jumlah})")

# ================== SIDEBAR ==================
st.sidebar.header("⚙️ Control Panel")

if st.sidebar.button("🔄 Sync Data"):

    st.session_state.data = load_json(
        FILE_PATH,
        {}
    )

    st.rerun()

if st.sidebar.button("🧨 Reset Semua Data"):

    st.session_state.data = {}

    save_json(
        FILE_PATH,
        {},
        "RESET semua"
    )

    st.rerun()
```
