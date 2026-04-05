import streamlit as st
import pandas as pd
from database import init_db, get_db, add_chat_message, get_chat_history, add_sample_course, get_all_courses
from ai_service import ai_service
import os

# Page Configuration
st.set_page_config(
    page_title="LMS Yapay Zeka Final",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database
init_db()

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7f9 0%, #eef2f3 100%);
    }
    .stSidebar {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        text-align: center;
    }
    .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 14px;
        color: #666;
    }
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=60)
    st.title("AI-LMS Dashboard")
    st.divider()
    
    selected_page = st.radio(
        "Navigasyon",
        ["🏠 Ana Sayfa", "💬 AI Sohbet", "📚 Ders Materyalleri", "⚙ Ayarlar"]
    )
    
    st.divider()
    st.info("Bu platform Gemini & Groq LLM API'leri ile güçlendirilmiştir.")

# --- PAGE: HOME ---
if selected_page == "🏠 Ana Sayfa":
    st.title("Hoş Geldiniz! 👋")
    st.subheader("Eğitimde Yapay Zeka Entegrasyonu")
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-card"><div class="stat-value">12</div><div class="stat-label">Toplam Ders</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div class="stat-value">156</div><div class="stat-label">Öğrenci Sayısı</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><div class="stat-value">4.8</div><div class="stat-label">Ortalama Puan</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-card"><div class="stat-value">850+</div><div class="stat-label">AI Yanıtı</div></div>', unsafe_allow_html=True)
        
    st.divider()
    
    st.markdown("""
    ### 🚀 Neler Yapabilirsiniz?
    - **Akıllı Sohbet:** Gemini veya Groq modelleri ile dersleriniz hakkında soru sorun.
    - **İçerik Üretimi:** Yapay zeka ile otomatik ders özetleri ve sınav soruları oluşturun.
    - **Veri Analizi:** Eğitim performansınızı yapay zeka destekli grafiklerle takip edin.
    """)

# --- PAGE: AI CHAT ---
elif selected_page == "💬 AI Sohbet":
    st.title("AI Eğitmen Asistanı")
    st.caption("Farklı yapay zeka modelleri ile etkileşime geçin.")
    
    # Model Selection
    ai_provider = st.radio("Provider Seçin:", ["Gemini", "Groq"], horizontal=True)
    
    db_gen = get_db()
    db = next(db_gen)
    
    # Chat History
    chat_history = get_chat_history(db)
    for chat in chat_history:
        with st.chat_message(chat.role):
            st.write(chat.message)
            st.caption(f"Model: {chat.model_name} | {chat.timestamp.strftime('%H:%M')}")
            
    # User Input
    if prompt := st.chat_input("Dersinle ilgili ne öğrenmek istersin?"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Save to DB
        add_chat_message(db, "user", prompt, ai_provider)
        
        # Get AI Response
        with st.chat_message("assistant"):
            with st.spinner(f"{ai_provider} düşünüyot..."):
                response = ai_service.ask(prompt, provider=ai_provider.lower())
                st.markdown(response)
        
        # Save response to DB
        add_chat_message(db, "assistant", response, ai_provider)

# --- PAGE: COURSES ---
elif selected_page == "📚 Ders Materyalleri":
    st.title("Ders Arşivi")
    st.caption("Yüklü dersleri görüntüleyin veya yenilerini ekleyin.")
    
    db_gen = get_db()
    db = next(db_gen)
    
    tab1, tab2 = st.tabs(["Mevcut Dersler", "Yeni Ders Ekle"])
    
    with tab1:
        courses = get_all_courses(db)
        if not courses:
            st.warning("Henüz kayıtlı ders bulunmamaktadır.")
        else:
            for course in courses:
                with st.expander(f"📙 {course.title}"):
                    st.write(f"**Açıklama:** {course.description}")
                    st.divider()
                    st.write(course.content)
                    
    with tab2:
        with st.form("new_course"):
            title = st.text_input("Ders Başlığı")
            desc = st.text_area("Kısa Açıklama")
            content = st.text_area("Ders İçeriği")
            submit = st.form_submit_button("Dersi Kaydet")
            
            if submit:
                if title and content:
                    add_sample_course(db, title, desc, content)
                    st.success("Ders başarıyla eklendi!")
                    st.rerun()
                else:
                    st.error("Lütfen başlık ve içerik alanlarını doldurun.")

# --- PAGE: SETTINGS ---
elif selected_page == "⚙ Ayarlar":
    st.title("Platform Ayarları")
    
    st.subheader("API Yapılandırması")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    st.toggle("Gemini Aktif", value=bool(gemini_key), disabled=True)
    st.toggle("Groq Aktif", value=bool(groq_key), disabled=True)
    
    st.info("API anahtarları `.env` dosyası üzerinden yönetilmektedir.")
    
    if st.button("Örnek Veri Yükle"):
        db_gen = get_db()
        db = next(db_gen)
        add_sample_course(db, "Yapay Zekaya Giriş", "Temel kavramlar", "Yapay zeka, makinelerin insan zekasını taklit etmesidir...")
        st.success("Örnek veriler yüklendi.")
