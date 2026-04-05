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

# Custom CSS for Premium & Theme-Aware Look
st.markdown("""
<style>
    /* Main Background - Adaptive */
    .stApp {
        background: var(--background-content-color);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
        border-right: 1px solid var(--divider-color);
    }
    
    /* Stat Cards - Glassmorphism */
    .stat-card {
        background: var(--secondary-background-color);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid var(--divider-color);
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        border-color: #1f77b4;
    }
    .stat-value {
        font-size: 28px;
        font-weight: 800;
        color: #1f77b4;
        margin-bottom: 4px;
    }
    .stat-label {
        font-size: 14px;
        color: var(--text-color);
        opacity: 0.8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    
    /* Title styling */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
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
    # Hero Section with Banner
    st.image("assets/banner.png", use_container_width=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 3rem; margin-bottom: 0;">LMS Yapay Zeka Final</h1>
        <p style="font-size: 1.2rem; opacity: 0.8;">Eğitimde Yeni Nesil Yapay Zeka Deneyimi</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Advanced Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 40px;">📚</div>
            <div class="stat-value">12</div>
            <div class="stat-label">Toplam Ders</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 40px;">👨‍🎓</div>
            <div class="stat-value">156</div>
            <div class="stat-label">Öğrenci Sayısı</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 40px;">⭐</div>
            <div class="stat-value">4.8</div>
            <div class="stat-label">Ortalama Puan</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div style="font-size: 40px;">⚡</div>
            <div class="stat-value">850+</div>
            <div class="stat-label">AI Yanıtı</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    st.markdown("### 🚀 Platform Özellikleri")
    
    # Feature Cards
    fcol1, fcol2, fcol3 = st.columns(3)
    
    with fcol1:
        st.markdown("""
        <div style="background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color); height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;">
            <div style="background: rgba(31, 119, 180, 0.1); width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px;">
                <span style="font-size: 30px;">💬</span>
            </div>
            <h4>Akıllı Sohbet</h4>
            <p style="font-size: 0.9rem; opacity: 0.8;">Gemini ve Groq modelleri ile dersleriniz hakkında anlık soru-cevap asistanlığı.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with fcol2:
        st.markdown("""
        <div style="background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color); height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;">
            <div style="background: rgba(46, 204, 113, 0.1); width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px;">
                <span style="font-size: 30px;">✍️</span>
            </div>
            <h4>İçerik Üretimi</h4>
            <p style="font-size: 0.9rem; opacity: 0.8;">Tek tıkla ders özetleri, sınav soruları ve çalışma notları oluşturma.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with fcol3:
        st.markdown("""
        <div style="background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color); height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;">
            <div style="background: rgba(155, 89, 182, 0.1); width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px;">
                <span style="font-size: 30px;">📊</span>
            </div>
            <h4>Veri Analizi</h4>
            <p style="font-size: 0.9rem; opacity: 0.8;">Eğitim performansınızı yapay zeka destekli grafiklerle takip edin.</p>
        </div>
        """, unsafe_allow_html=True)

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
