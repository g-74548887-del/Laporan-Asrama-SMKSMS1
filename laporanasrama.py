# ================== EXTRACT ==================
def extract(text):
    if not text:
        return []

    res = []

    for line in text.split("\n"):

        # SUPPORT COMMA
        parts = line.replace(",", "\n").split("\n")

        for p in parts:

            p = p.strip()

            if p and p.upper() == p:
                res.append(p)

    return list(set(res))

# ================== TRACKING ==================
from collections import Counter

tiada_counter = Counter()
haid_counter = Counter()

for tarikh, info in st.session_state.data.items():

    # MURID TIADA
    murid_tiada = info.get("murid_tiada", "")

    for nama in extract(murid_tiada):
        tiada_counter[nama] += 1

    # MURID HAID
    murid_haid = info.get("murid_haid", "")

    for nama in extract(murid_haid):
        haid_counter[nama] += 1

# FILTER >10 HARI
murid_tiada_10 = {
    k: v for k, v in tiada_counter.items() if v >= 10
}

murid_haid_10 = {
    k: v for k, v in haid_counter.items() if v >= 10
}

# ================== POPUP ==================
if st.session_state.active_date:

    date_key = st.session_state.active_date

    @st.dialog(f"Laporan {date_key}")
    def form():

        existing = st.session_state.data.get(date_key, {})

        nama = st.text_input(
            "Nama Warden",
            value=existing.get("nama_warden", "")
        )

        oncall = st.text_input(
            "Warden Oncall",
            value=existing.get("oncall", "")
        )

        jumlah = st.number_input(
            "Jumlah Murid",
            min_value=0,
            value=existing.get("jumlah_murid", 0)
        )

        # ================== MURID TIADA ==================
        st.info(
            "⚠️ Tulis nama murid HURUF BESAR supaya sistem boleh detect "
            "murid yang tiada lebih 10 hari.\n\n"
            "Contoh:\n"
            "AUNY HUMAIRAH, NURUL AIDA, DHIYA AMNI,\n"
            "NURIN NAJWA, DANIA, HAJAR BATRISYIA,\n"
            "DAMIA, QASEH ELLYSHA, AIRIS,\n"
            "AINNUR HUMAIRA, SHUHADA, QAISARA,\n"
            "ARISSA QAIREN, KHAIYISAH, NURIN AIREN,\n"
            "FATIHAH DAMIASARA, NURZAHIRAH,\n"
            "AMNI NADHIRAH, NURUL ASYIKIN,\n"
            "SYAHIDATUL, AMNI DAHLIA, RAUDHAH,\n"
            "ALYAA, NUR FATIHAH, NAJA SYIFA,\n"
            "SAFEERA, DAMIA DAYANA, SYUHADA ERINA,\n"
            "NURUL HUSNA, ZULAIFATUL,\n"
            "AINUL SAKINAH, FARZANA,\n"
            "UMMU BARIK, AMANDA, AMANI DAMIA"
        )

        tiada = st.text_area(
            "Murid Tiada / Sebab",
            value=existing.get("murid_tiada", "")
        )

        # ================== MURID HAID ==================
        st.info(
            "⚠️ Tulis nama murid HAID dalam HURUF BESAR supaya "
            "sistem boleh detect murid haid lebih 10 hari.\n\n"
            "Contoh:\n"
            "AUNY HUMAIRAH, NURUL AIDA, DHIYA AMNI,\n"
            "NURIN NAJWA, DANIA, HAJAR BATRISYIA,\n"
            "DAMIA, QASEH ELLYSHA, AIRIS,\n"
            "AINNUR HUMAIRA, SHUHADA, QAISARA,\n"
            "ARISSA QAIREN, KHAIYISAH, NURIN AIREN,\n"
            "FATIHAH DAMIASARA, NURZAHIRAH,\n"
            "AMNI NADHIRAH, NURUL ASYIKIN,\n"
            "SYAHIDATUL, AMNI DAHLIA, RAUDHAH,\n"
            "ALYAA, NUR FATIHAH, NAJA SYIFA,\n"
            "SAFEERA, DAMIA DAYANA, SYUHADA ERINA,\n"
            "NURUL HUSNA, ZULAIFATUL,\n"
            "AINUL SAKINAH, FARZANA,\n"
            "UMMU BARIK, AMANDA, AMANI DAMIA"
        )

        murid_haid = st.text_area(
            "Murid Haid",
            value=existing.get("murid_haid", "")
        )

        masa = st.text_input(
            "Masa Rondaan",
            value=existing.get("masa_rondaan", "")
        )

        st.info(
            "⚠️ Nama murid MESTI HURUF BESAR sahaja.\n"
            "Contoh: SITI NURHALIZA tidak solat subuh berjemaah"
        )

        kes = st.text_area(
            "Laporan Rondaan",
            value=existing.get("kes", "")
        )

        # ================== AKTIVITI ==================
        aktiviti = st.text_area(
            "Nama Aktiviti",
            value=existing.get("nama_aktiviti", "")
        )

        gambar_aktiviti = st.file_uploader(
            "Upload 2 Gambar Aktiviti",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="aktiviti_upload"
        )

        # ================== SISKA ==================
        program_siska = st.text_area(
            "Nama Program SISKA",
            value=existing.get("program_siska", "")
        )

        gambar_siska = st.file_uploader(
            "Upload 2 Gambar SISKA",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="siska_upload"
        )

        # ================== HANTAR ==================
        if st.button("Hantar"):

            st.session_state.data[date_key] = {
                "nama_warden": nama,
                "oncall": oncall,
                "jumlah_murid": jumlah,

                # MURID
                "murid_tiada": tiada,
                "murid_haid": murid_haid,

                # RONDAAN
                "masa_rondaan": masa,
                "kes": kes,

                # AKTIVITI
                "nama_aktiviti": aktiviti,

                # SISKA
                "program_siska": program_siska
            }

            save_json(FILE_PATH, st.session_state.data, "update laporan")

            # AUTO TAMBAH MURID DENDA
            for n in extract(kes):

                if n not in st.session_state.denda:
                    st.session_state.denda.append(n)

            save_json(
                DENDA_FILE,
                st.session_state.denda,
                "update denda"
            )

            st.success("Data berjaya disimpan")

            st.session_state.active_date = None
            st.rerun()

        st.markdown("---")

        # ================== RESET ==================
        if st.button("🧨 Reset Tarikh Ini"):

            if date_key in st.session_state.data:

                del st.session_state.data[date_key]

                save_json(
                    FILE_PATH,
                    st.session_state.data,
                    "delete tarikh"
                )

            st.success("Tarikh telah dikosongkan")

            st.session_state.active_date = None

            st.rerun()

    form()

# ================== DENDA ==================
with col2:

    # ================== MURID DENDA ==================
    st.subheader("Murid Denda")

    st.caption(
        "Tekan ❌ untuk buang nama jika telah ambil tindakan."
    )

    if not st.session_state.denda:

        st.info("Tiada murid")

    else:

        for i, m in enumerate(st.session_state.denda):

            c1, c2 = st.columns([3,1])

            c1.write(m)

            if c2.button("❌", key=f"denda_{i}"):

                st.session_state.denda.pop(i)

                save_json(
                    DENDA_FILE,
                    st.session_state.denda,
                    "delete"
                )

                st.rerun()

    st.markdown("---")

    # ================== MURID TIADA >10 ==================
    st.subheader("Murid Tiada >10 Hari")

    st.caption(
        "Tekan ❌ untuk buang nama jika telah ambil tindakan."
    )

    if not murid_tiada_10:

        st.info("Tiada murid")

    else:

        remove_tiada = []

        for i, (nama, total) in enumerate(murid_tiada_10.items()):

            c1, c2 = st.columns([3,1])

            c1.write(f"{nama} ({total} hari)")

            if c2.button("❌", key=f"tiada_{i}"):

                remove_tiada.append(nama)

        if remove_tiada:

            for tarikh, info in st.session_state.data.items():

                text = info.get("murid_tiada", "")

                for nama in remove_tiada:
                    text = text.replace(nama, "")

                st.session_state.data[tarikh]["murid_tiada"] = text

            save_json(
                FILE_PATH,
                st.session_state.data,
                "remove murid tiada"
            )

            st.rerun()

    st.markdown("---")

    # ================== MURID HAID >10 ==================
    st.subheader("Murid Haid >10 Hari")

    st.caption(
        "Tekan ❌ untuk buang nama jika telah ambil tindakan."
    )

    if not murid_haid_10:

        st.info("Tiada murid")

    else:

        remove_haid = []

        for i, (nama, total) in enumerate(murid_haid_10.items()):

            c1, c2 = st.columns([3,1])

            c1.write(f"{nama} ({total} hari)")

            if c2.button("❌", key=f"haid_{i}"):

                remove_haid.append(nama)

        if remove_haid:

            for tarikh, info in st.session_state.data.items():

                text = info.get("murid_haid", "")

                for nama in remove_haid:
                    text = text.replace(nama, "")

                st.session_state.data[tarikh]["murid_haid"] = text

            save_json(
                FILE_PATH,
                st.session_state.data,
                "remove murid haid"
            )

            st.rerun()