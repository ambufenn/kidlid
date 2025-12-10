import streamlit as st
from google import genai
from google.genai import types

# --- 0. Setup Klien Gemini & Konfigurasi ---

# Mengambil kunci API dari Streamlit Secrets
# Pastikan Anda telah menyimpan kunci API Anda di .streamlit/secrets.toml
try:
    API_KEY = st.secrets["gemini_api_key"]
except KeyError:
    st.error("Kunci API Gemini tidak ditemukan. Harap simpan API key di st.secrets['gemini_api_key'].")
    st.stop()

client = genai.Client(api_key=API_KEY)
MODEL_FLASH = 'gemini-2.5-flash'
TEMPERATURE = 0.8  # Suhu tinggi untuk kreativitas dan skenario yang beragam

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Kids' Life Skills Coach",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fungsi Panggilan AI Inti ---
def call_gemini_skill_prompt(system_instruction, user_prompt):
    """Memanggil Gemini dengan instruksi dan suhu kreatif."""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=TEMPERATURE
    )
    with st.spinner("Menciptakan skenario interaktif..."):
        try:
            response = client.models.generate_content(
                model=MODEL_FLASH,
                contents=user_prompt,
                config=config
            )
            return response.text
        except Exception as e:
            st.error(f"Gagal memproses AI: {e}")
            return None

# --- Judul Utama Aplikasi ---
st.title("🌟 Kids' Life Skills Coach (Didukung Gemini AI)")
st.markdown("Aplikasi interaktif untuk melatih keterampilan hidup praktis anak usia 6-12 tahun.")

# --- Sidebar Menu ---
st.sidebar.title("📚 Modul Pembelajaran")

main_menu = st.sidebar.selectbox(
    "Pilih Keterampilan yang Ingin Dilatih:",
    ["Simulasi Role-Playing", "Perencana Tugas Harian", "Tantangan Keuangan"]
)

# --- 1. Modul: Simulasi Role-Playing (Keterampilan Sosial) ---
if main_menu == "Simulasi Role-Playing":
    st.header("🎭 Role-Playing: Keterampilan Sosial")
    st.markdown("Ciptakan skenario yang menyenangkan agar anak belajar menghadapi situasi sosial.")
    
    # Input Pengguna
    skill_choice = st.selectbox(
        "Pilih Keterampilan Dasar:",
        ["Menyelesaikan Konflik", "Meminta Bantuan", "Berbagi dan Bekerja Sama", "Mengelola Emosi"]
    )
    child_age = st.number_input("Usia Anak:", min_value=6, max_value=12, value=8)
    
    user_input = st.text_input("Tokoh atau Situasi yang disukai Anak (Opsional, e.g., 'bertemu robot baik', 'di sekolah baru'):")
    
    if st.button("Mulai Skenario Baru", type="primary"):
        # System Instruction untuk Role-Playing
        system_prompt = f"""
        Anda adalah seorang Storyteller AI yang ramah dan suportif, khusus untuk anak usia {child_age} tahun. 
        Tugas Anda adalah membuat skenario role-playing singkat (3-4 paragraf) yang berfokus melatih '{skill_choice}'. 
        Skenario harus interaktif, diakhiri dengan pertanyaan yang membutuhkan keputusan anak. 
        Gunakan nada bahasa yang positif, sederhana, dan menarik untuk anak.
        """
        
        prompt = f"Ciptakan skenario interaktif untuk melatih {skill_choice}. Tambahkan elemen: {user_input if user_input else 'cerita sehari-hari'}."
        
        scenario = call_gemini_skill_prompt(system_prompt, prompt)
        
        if scenario:
            st.subheader(f"Petualangan {skill_choice} Dimulai!")
            st.markdown(scenario)
            st.info("Ajak anak Anda menjawab pertanyaan di akhir skenario. Anda bisa melanjutkan diskusi dengan anak Anda.")

# --- 2. Modul: Perencana Tugas Harian (Keterampilan Organisasi) ---
elif main_menu == "Perencana Tugas Harian":
    st.header("📋 Perencana Tugas Harian")
    st.markdown("Buat jadwal yang menyenangkan dan realistis agar anak belajar mengatur waktu dan memprioritaskan tugas.")

    tasks = st.text_area("Daftar Tugas yang Harus Dilakukan Anak (Pisahkan dengan koma, contoh: 'rapikan mainan, kerjakan PR, bantu siram bunga'):")
    
    if st.button("Buat Rencana Prioritas", type="primary"):
        if tasks:
            system_prompt = """
            Anda adalah Time Management Coach yang lucu dan tegas.
            Tugas Anda adalah mengambil daftar tugas anak dan:
            1. Mengelompokkannya menjadi 'Mendesak (Kerjakan Sekarang)', 'Penting (Kerjakan Nanti)', dan 'Bisa Ditunda (Bonus)'.
            2. Memberikan motivasi yang mendorong penyelesaian tugas, bukan hukuman.
            3. Tambahkan ikon emoji yang menarik.
            Tampilkan hasilnya dalam format daftar Markdown dengan heading yang jelas.
            """
            prompt = f"Tolong atur tugas-tugas berikut ke dalam kategori prioritas dan berikan saran urutan yang masuk akal: {tasks}"
            
            plan = call_gemini_skill_prompt(system_prompt, prompt)
            
            if plan:
                st.subheader("Rencana Tugas Harian Siap!")
                st.markdown(plan)

# --- 3. Modul: Tantangan Keuangan (Keterampilan Finansial) ---
elif main_menu == "Tantangan Keuangan":
    st.header("💸 Tantangan Finansial Sederhana")
    st.markdown("Simulasikan keputusan uang untuk mengajarkan konsep menabung, keinginan vs. kebutuhan.")

    # Menggunakan text_input karena nominal bisa berupa Rupiah, Dollar, dll.
    money_amount_str = st.text_input("Jumlah Uang Awal Anak (e.g., Rp 10.000, $5.00):", value="Rp 10.000")
    
    st.subheader("Pilihan Belanja:")
    item1 = st.text_input("Pilihan 1 (e.g., 'Buku Komik'):", value="Buku Komik")
    cost1_str = st.text_input("Harga Pilihan 1:", value="Rp 5.000")
    
    item2 = st.text_input("Pilihan 2 (e.g., 'Mainan Baru'):", value="Mainan Baru")
    cost2_str = st.text_input("Harga Pilihan 2:", value="Rp 15.000")
    
    if st.button("Analisis Keputusan Uang", type="primary"):
        # Cek input dasar
        if not all([money_amount_str, item1, cost1_str, item2, cost2_str]):
            st.warning("Mohon isi semua kolom input.")
            st.stop()
            
        system_prompt = f"""
        Anda adalah Financial Advisor yang sabar untuk anak-anak. Uang saku awal adalah {money_amount_str}.
        Tugas Anda adalah:
        1. Membuat skenario di mana anak harus memilih antara menabung atau membeli salah satu item.
        2. Menjelaskan konsep 'Keinginan vs. Kebutuhan' dalam bahasa yang sederhana dan menarik.
        3. Memberikan 3 saran konkret bagaimana anak bisa mendapatkan uang tambahan atau menabung secara disiplin.
        Gunakan mata uang yang dimasukkan ({money_amount_str}).
        """
        prompt = f"""
        Anak memiliki uang {money_amount_str}. Mereka ingin membeli:
        - {item1} seharga {cost1_str}
        - {item2} seharga {cost2_str}
        Buat skenario keputusan yang mengajarkan tentang uang.
        """
        
        analysis = call_gemini_skill_prompt(system_prompt, prompt)
        
        if analysis:
            st.subheader("Skenario Keuangan dan Nasihat")
            st.markdown(analysis)
