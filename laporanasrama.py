# ================== DIALOG FORM ==================
@st.dialog("Borang Laporan")
def papar_borang(date_key):
    st.write(f"### Laporan Tarikh: {date_key}")
    
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
            aduan_list.append({"nama": murid_pilih, "aduan": aduan_text})
            existing["aduan_list"] = aduan_list
            st.session_state.data[date_key] = existing
            save_json(FILE_PATH, st.session_state.data, f"Tambah aduan {murid_pilih} pada {date_key}")
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
                    save_json(FILE_PATH, st.session_state.data, f"Padam aduan {nama_murid} pada {date_key}")
                    st.rerun()
    else:
        st.info("Tiada aduan untuk tarikh ini.")

    st.markdown("---")

    # ================== HAID (SISTEM OPTIMASI BARIS MOBILE) ==================
    st.subheader("🩸 Rekod Haid Tarikh Ini")
    st.info("Tekan + jika murid haid. Tolak jika tersilap.")
    
    st.markdown(
        """
        <style>
        div[data-testid="column"] {
            display: flex;
            align-items: center;
            justify-content: flex-start;
        }
        div.stButton > button {
            padding: 2px 10px !important;
            height: auto !important;
            min-width: 40px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    haid_hari_ini = existing.get("haid_hari_ini", {})
    rumusan_semasa = kira_rumusan_haid_keseluruhan()

    with st.container(height=350):
        for m in MURID:
            hari_tarikh_ini = haid_hari_ini.get(m, 0)
            total_terkini = rumusan_semasa.get(m, 0)
            
            col_nama, col_butang = st.columns([2.5, 1.5])
            
            with col_nama:
                if hari_tarikh_ini > 0:
                    st.markdown(f"🔴 **{m} ({total_terkini})**")
                else:
                    st.write(f"⚪ {m} ({total_terkini})")
            
            with col_butang:
                sub_c1, sub_c2 = st.columns(2)
                with sub_c1:
                    if st.button("➕", key=f"add_{m}_{date_key}"):
                        haid_hari_ini[m] = hari_tarikh_ini + 1
                        existing["haid_hari_ini"] = haid_hari_ini
                        st.session_state.data[date_key] = existing
                        save_json(FILE_PATH, st.session_state.data, f"Tambah haid {m} pada {date_key}")
                        st.rerun()
                with sub_c2:
                    if st.button("➖", key=f"sub_{m}_{date_key}"):
                        if hari_tarikh_ini > 0:
                            haid_hari_ini[m] = hari_tarikh_ini - 1
                            if haid_hari_ini[m] == 0:
                                haid_hari_ini.pop(m, None)
                            existing["haid_hari_ini"] = haid_hari_ini
                            st.session_state.data[date_key] = existing
                            save_json(FILE_PATH, st.session_state.data, f"Kurangkan haid {m} pada {date_key}")
                            st.rerun()

    st.markdown("---")

    # ================== PROGRAM ==================
    st.subheader("🎪 Program Asrama")
    nama_program = st.text_input("Nama Program", existing.get("nama_program", ""))
    
    st.write("📷 Sila muat naik gambar aktiviti (Maksimum 2 Gambar sahaja):")
    
    img_data_list = existing.get("program_images", ["", ""])
    while len(img_data_list) < 2:
        img_data_list.append("")
        
    uploaded_img1 = st.file_uploader("Gambar 1", type=["png", "jpg", "jpeg"], key=f"img1_{date_key}")
    uploaded_img2 = st.file_uploader("Gambar 2", type=["png", "jpg", "jpeg"], key=f"img2_{date_key}")
    
    if uploaded_img1 is not None:
        bytes_data1 = uploaded_img1.getvalue()
        img_data_list[0] = base64.b64encode(bytes_data1).decode("utf-8")
    
    if uploaded_img2 is not None:
        bytes_data2 = uploaded_img2.getvalue()
        img_data_list[1] = base64.b64encode(bytes_data2).decode("utf-8")

    col_preview1, col_preview2 = st.columns(2)
    with col_preview1:
        if img_data_list[0] != "":
            st.image(base64.b64decode(img_data_list[0]), caption="Gambar 1 Sedia Ada", width=150)
    with col_preview2:
        if img_data_list[1] != "":
            st.image(base64.b64decode(img_data_list[1]), caption="Gambar 2 Sedia Ada", width=150)

    st.markdown("---")

    # ================== SIMPAN GLOBAL (DIBAIKI) ==================
    if st.button("💾 Simpan Semua Laporan", use_container_width=True, key="btn_save_laporan"):
        haid_semasa = existing.get("haid_hari_ini", {})
        aduan_semasa = existing.get("aduan_list", [])
        
        st.session_state.data[date_key] = {
            "nama_warden": nama,
            "oncall": oncall,
            "jumlah_murid": jumlah,
            "murid_tiada": tiada,
            "masa_rondaan": masa,
            "aduan_list": aduan_semasa,
            "haid_hari_ini": haid_semasa,
            "nama_program": nama_program,
            "program_images": img_data_list
        }
        save_json(FILE_PATH, st.session_state.data, f"Kemas kini penuh laporan bagi tarikh {date_key}")
        st.success("Laporan berjaya disimpan!")
        st.session_state.active_date = None 
        st.rerun()