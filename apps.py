import streamlit as st
from google import genai
from google.genai import types

# --- 0. Setup Klien Gemini & Konfigurasi ---

# Mengambil kunci API dari Streamlit Secrets
try:
    API_KEY = st.secrets["gemini_api_key"]
except KeyError:
    st.error("Kunci API Gemini tidak ditemukan. Harap simpan API key di st.secrets['gemini_api_key'].")
    st.stop()

client = genai.Client(api_key=API_KEY)
MODEL_FLASH = 'gemini-2.5-flash'
TEMPERATURE = 0.8  # Suhu tinggi untuk kreativitas dan gamifikasi

# --- Setup Gamifikasi Session State ---
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'level' not in st.session_state:
    st.session_state.level = 1
# Kunci untuk melacak klaim poin unik per sesi Misi
if 'claimed_daily' not in st.session_state:
    st.session_state.claimed_daily = False
if 'current_quest' not in st.session_state:
    st.session_state.current_quest = None

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Home Hero Academy",
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
    # Tidak menggunakan spinner agar tidak mengganggu st.balloons
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

# --- Fungsi Gamifikasi ---

def check_level_up(points_earned, module_key, mission_type):
    """Mengecek kenaikan level dengan batasan baru dan feedback naratif."""
    
    # Hanya proses jika belum diklaim
    if st.session_state[module_key] == False:
        st.session_state.points += points_earned
        st.session_state[module_key] = True # Tandai sudah diklaim
        
        # Batasan Level Baru: 50, 150, 300
        new_level = st.session_state.level
        if st.session_state.points > 300: new_level = 4
        elif st.session_state.points > 150: new_level = 3
        elif st.session_state.points > 50: new_level = 2
        else: new_level = 1
        
        if new_level > st.session_state.level:
            old_level = st.session_state.level
            st.session_state.level = new_level
            st.success(f"LEVEL UP! Anda naik dari Level {old_level} ke Level {new_level}! 🎉")
            
            # Reward Cerita untuk Level Up
            reward_story = call_gemini_skill_prompt(
                system_instruction="Anda adalah narator Game yang memberikan hadiah cerita singkat (2 paragraf) untuk kenaikan level. Hadiah harus berupa pencapaian pahlawan rumah tangga yang fantastis, berfokus pada kebersihan atau kemandirian.",
                user_prompt=f"Berikan hadiah kepada pahlawan Level {new_level} karena sukses menyelesaikan Misi {mission_type}. Cerita tentang bagaimana mereka mendapatkan lencana baru atau kekuatan super kebersihan."
            )
            if reward_story:
                st.balloons()
                st.markdown("### 🎁 Hadiah Level Baru!")
                st.markdown(reward_story)
        else:
            st.success(f"+{points_earned} Poin ditambahkan ke akun Anda! Lanjutkan petualangan!")

# --- Modul Utama: Misi Harian Pahlawan Rumah ---

def daily_mission_page():
    st.header("🏠 Misi Harian Pahlawan Rumah")
    st.markdown("Pilih misi, baca instruksi *Quest* dari AI, selesaikan tugas, dan klaim poin untuk naik level!")
    
    # Reset klaim untuk sesi baru
    # Ini penting agar setiap kali tombol "Mulai Quest" ditekan, klaim bisa dilakukan lagi
    st.session_state.claimed_daily = True 
    
    # 1. Input Misi
    mission_category = st.selectbox(
        "Pilih Kategori Misi Hari Ini:",
        ["Kebiasaan Diri (Self-Care)", "Perawatan Kamar", "Tugas Rumah Tangga Dasar"]
    )
    
    mission_choice = st.text_input("Tulis Misi Spesifik (e.g., 'Cuci Tangan 7 Langkah', 'Menyapu Ruang Tamu', 'Beresin Tempat Tidur'):")
    
    if st.button("Mulai Quest", type="primary"):
        if not mission_choice:
            st.warning("Mohon tentukan misi spesifik.")
            return

        # Tentukan Poin berdasarkan kategori
        if mission_category == "Kebiasaan Diri (Self-Care)":
            points = 20
        elif mission_category == "Perawatan Kamar":
            points = 30
        else:
            points = 40 # Tugas Rumah Tangga Dasar
            
        system_prompt = f"""
        Anda adalah Game Master (GM) yang memberikan Quest.
        Tugas Anda adalah memecah '{mission_choice}' (kategori: {mission_category}) menjadi 3-5 langkah/quest yang sangat sederhana, jelas, dan berurutan untuk anak usia 4-8 tahun.
        Gunakan bahasa yang menarik dan penuh energi, seperti cerita petualangan. Pastikan instruksi sangat praktis.
        Sebutkan total poin reward ({points} Poin) di akhir deskripsi quest.
        """
        
        prompt = f"Buat Quest 'Pahlawan Rumah' untuk misi: {mission_choice}. Berikan instruksi langkah demi langkah."
        
        quest_description = call_gemini_skill_prompt(system_prompt, prompt)
        
        if quest_description:
            # Simpan Sesi Quest
            st.session_state['current_quest'] = quest_description
            st.session_state['current_points'] = points
            st.session_state['current_mission_type'] = mission_category
            st.session_state.claimed_daily = False # Buka klaim untuk quest baru
            
            st.subheader(f"Misi Baru: {mission_choice} ({points} Poin)!")
            st.markdown(quest_description)
            st.warning("Perhatian, Pahlawan! Selesaikan Quest di dunia nyata dulu sebelum klaim poin!")


    # 2. Tampilan Hasil Quest
    if st.session_state.current_quest:
        st.subheader("Instruksi Quest Aktif:")
        st.markdown(st.session_state.current_quest)
        
        # 3. Tombol Klaim Poin
        if st.button(f"✅ Klaim Poin Selesai Misi ({st.session_state['current_points']} Poin)", type="secondary"):
            if not st.session_state.claimed_daily:
                # Panggil fungsi leveling
                check_level_up(st.session_state['current_points'], 'claimed_daily', st.session_state['current_mission_type'])
                # Hapus Quest agar tidak tampil terus-menerus setelah klaim
                st.session_state.current_quest = None 
            else:
                st.warning("Poin untuk misi ini sudah diklaim. Silakan buat Quest baru!")


# --- 6. Struktur Menu Utama Streamlit (Routing) ---

# Tentukan menu yang hanya berisi Modul Misi Harian
st.sidebar.title("🛠️ Pilih Kegiatan")
main_menu = st.sidebar.selectbox(
    "1. Pilih Modul:",
    ["Tentang Aplikasi", "Misi Pahlawan Rumah Tangga"]
)

# --- Routing Logika Berdasarkan Pilihan Menu ---

if main_menu == "Tentang Aplikasi":
    st.info("Selamat datang di Home Hero Academy! Aplikasi ini menggunakan AI untuk mengubah tugas rumah tangga menjadi petualangan berpoin.")
    st.subheader("Cara Kerja:")
    st.markdown("* **Pilih Misi:** Tulis tugas sehari-hari (merapikan kasur, cuci tangan).")
    st.markdown("* **AI Buat Quest:** Gemini memecah tugas menjadi langkah-langkah permainan.")
    st.markdown("* **Klaim Poin:** Setelah selesai di dunia nyata, klaim poin untuk naik **Level** dan dapat **Hadiah Cerita** (Reward Story).")
    st.markdown(f"Model Dasar: **{MODEL_FLASH}**")

elif main_menu == "Misi Pahlawan Rumah Tangga":
    daily_mission_page()
