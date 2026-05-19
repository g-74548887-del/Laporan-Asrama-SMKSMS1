# ================== POPUP ==================
if st.session_state.active_date:

    date_key = st.session_state.active_date

    @st.dialog(f"Laporan {date_key}")
    def form():

        existing = st.session_state.data.get(date_key, {})

        nama = st.text_input("Nama Warden", value=existing.get("nama_warden", ""))
        oncall = st.text_input("Warden Oncall", value=existing.get("oncall", ""))

        jumlah = st.number_input(
            "Jumlah Murid",
            min_value=0,
            value=existing.get("jumlah_murid", 0)
        )

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

        if st.button("Hantar"):

            st.session_state.data[date_key] = {
                "nama_warden": nama,
                "oncall": oncall,
                "jumlah_murid": jumlah,
                "murid_tiada": tiada,
                "masa_rondaan": masa,
                "kes": kes,

                # AKTIVITI
                "nama_aktiviti": aktiviti,

                # SISKA
                "program_siska": program_siska
            }

            save_json(FILE_PATH, st.session_state.data, "update laporan")

            for n in extract(kes):
                if n not in st.session_state.denda:
                    st.session_state.denda.append(n)

            save_json(DENDA_FILE, st.session_state.denda, "update denda")

            st.success("Data berjaya disimpan")

            st.session_state.active_date = None
            st.rerun()

        st.markdown("---")

        if st.button("🧨 Reset Tarikh Ini"):

            if date_key in st.session_state.data:
                del st.session_state.data[date_key]
                save_json(FILE_PATH, st.session_state.data, "delete tarikh")

            st.success("Tarikh telah dikosongkan")
            st.session_state.active_date = None
            st.rerun()

    form()