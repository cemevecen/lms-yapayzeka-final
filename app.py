import streamlit as st
import pandas as pd
from database import init_db, get_db, add_chat_message, get_chat_history, add_sample_course, get_all_courses, delete_course
from ai_service import ai_service
import os
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="LMS Yapay Zeka Final",
    page_icon=None,
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
    
    /* Settings Cards */
    .settings-card {
        background: var(--secondary-background-color);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid var(--divider-color);
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight:600;
        margin-left: 10px;
    }
    .status-active { background: #2ecc71; color: white; }
    .status-passive { background: #e74c3c; color: white; }
    
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
    st.title("AI-LMS Dashboard")
    st.divider()
    
    selected_page = st.radio(
        "Navigasyon",
        ["Ana Sayfa", "AI Sohbet", "Ders Materyalleri", "Ayarlar"]
    )
    
    st.divider()
    st.info("Bu platform Gemini ve Groq LLM API'leri ile güçlendirilmiştir.")

# --- PAGE: HOME ---
if selected_page == "Ana Sayfa":
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
            <div class="stat-value">12</div>
            <div class="stat-label">Toplam Ders</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">156</div>
            <div class="stat-label">Öğrenci Sayısı</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">4.8</div>
            <div class="stat-label">Ortalama Puan</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">850+</div>
            <div class="stat-label">AI Yanıtı</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    st.markdown("### Platform Özellikleri")
    
    # Feature Cards
    fcol1, fcol2, fcol3 = st.columns(3)
    
    with fcol1:
        st.markdown("""
        <div style="background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color); height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;">
            <h4>Akıllı Sohbet</h4>
            <p style="font-size: 0.9rem; opacity: 0.8;">Gemini ve Groq modelleri ile dersleriniz hakkında anlık soru-cevap asistanlığı.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with fcol2:
        st.markdown("""
        <div style="background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color); height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;">
            <h4>İçerik Üretimi</h4>
            <p style="font-size: 0.9rem; opacity: 0.8;">Tek tıkla ders özetleri, sınav soruları ve çalışma notları oluşturma.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with fcol3:
        st.markdown("""
        <div style="background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color); height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center;">
            <h4>Veri Analizi</h4>
            <p style="font-size: 0.9rem; opacity: 0.8;">Eğitim performansınızı yapay zeka destekli grafiklerle takip edin.</p>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE: AI CHAT ---
elif selected_page == "AI Sohbet":
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("AI Egitmen Asistani")
        st.caption("Yapay zeka modelleri ile dersleriniz hakkinda etkilesime gecin.")
    with col2:
        if st.button("Gecmisi Temizle", use_container_width=True):
            db_gen = get_db()
            db = next(db_gen)
            from sqlalchemy import delete
            from models import ChatHistory
            db.execute(delete(ChatHistory))
            db.commit()
            st.rerun()

    # Model Selection Switch
    st.markdown('<div style="background: var(--secondary-background-color); padding: 15px; border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">', unsafe_allow_html=True)
    use_groq = st.toggle("Groq Modelini Kullan (Kapaliyken Gemini)", value=True)
    ai_provider = "Groq" if use_groq else "Gemini"
    st.markdown(f'<span style="font-weight: 600; color: #1f77b4;">Aktif Model: {ai_provider}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    db_gen = get_db()
    db = next(db_gen)
    
    # Chat History Container (Limit to last 20 for focus)
    history = get_chat_history(db)
    chat_history = history[-20:] if len(history) > 20 else history
    
    for chat in chat_history:
        with st.chat_message(chat.role):
            st.markdown(chat.message)
            st.markdown(f'<p style="font-size: 0.7rem; opacity: 0.5; margin: 0;">{chat.model_name} | {chat.timestamp.strftime("%H:%M")}</p>', unsafe_allow_html=True)
            
    # User Input Area
    if prompt := st.chat_input("Dersinle ilgili ne ogrenmek istersin?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        add_chat_message(db, "user", prompt, ai_provider)
        
        with st.chat_message("assistant"):
            with st.spinner(f"{ai_provider} yanitliyor..."):
                try:
                    response = ai_service.ask(prompt, provider=ai_provider.lower())
                    st.markdown(response)
                    add_chat_message(db, "assistant", response, ai_provider)
                except Exception as e:
                    st.error(f"Hata olustu: {str(e)}")

# --- PAGE: COURSES ---
elif selected_page == "Ders Materyalleri":
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
                col_exp, col_del = st.columns([0.85, 0.15])
                with col_exp:
                    with st.expander(f"{course.title}"):
                        st.write(f"**Açıklama:** {course.description}")
                        st.divider()
                        st.write(course.content)
                with col_del:
                    if st.button("Sil", key=f"del_{course.id}", type="primary", use_container_width=True):
                        delete_course(db, course.id)
                        st.rerun()
                    
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
elif selected_page == "Ayarlar":
    st.title("Sistem Yonetimi")
    st.caption("Platform ayarlarini ve veri akisini buradan kontrol edin.")
    
    # Section 1: API Configuration
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("API Yapilandirmasi")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    acol1, acol2 = st.columns(2)
    with acol1:
        status_css = "status-active" if gemini_key else "status-passive"
        status_text = "AKTIF" if gemini_key else "PASIF"
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; background: rgba(0,0,0,0.05); border-radius: 10px;">
                <span>Google Gemini API</span>
                <span class="status-badge {status_css}">{status_text}</span>
            </div>
        """, unsafe_allow_html=True)
        
    with acol2:
        status_css = "status-active" if groq_key else "status-passive"
        status_text = "AKTIF" if groq_key else "PASIF"
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; background: rgba(0,0,0,0.05); border-radius: 10px;">
                <span>Groq Llama 3 API</span>
                <span class="status-badge {status_css}">{status_text}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("API anahtarlari .env dosyasi üzerinden guvenli bir sekilde yonetilmektedir.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 2: Data Management
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("Veri Yonetimi")
    st.write("Veritabanindaki tum kayitlari temizleyebilir veya ornek ders iceriklerini yukleyebilirsin.")
    
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        if st.button("Veritabanini Sifirla (Tumunu Sil)", type="primary", use_container_width=True):
            db_gen = get_db()
            db = next(db_gen)
            from sqlalchemy import delete
            from models import Course, ChatHistory
            db.execute(delete(Course))
            db.execute(delete(ChatHistory))
            db.commit()
            st.warning("Veritabani tamamen bosaltildi.")
            st.rerun()
            
    with dcol2:
        if st.button("Temiz Ornek Veri Yukle", use_container_width=True):
            db_gen = get_db()
            db = next(db_gen)
            sample_courses = [
                {"title": "Cografya: Ekosistemler ve Iklim", "desc": "Kuresel iklim dengesi ve biyomlar.", "content": "Dunya'nin iklim sistemleri..."},
                {"title": "Edebiyat: Turk Siiri", "desc": "Tanzimattan gunumuze.", "content": "Siir gelenekleri..."},
                {"title": "Matematik: Kalkulus", "desc": "Turev ve integral.", "content": "Analiz temelleri..."},
                {"title": "Resim: Sanat Tarihi", "desc": "Rönesanstan modern sanata.", "content": "Sanat akimlari..."},
                {"title": "Müzik: Klasik Muzik", "desc": "Bati muzigi donemleri.", "content": "Muzik teorisi..."},
                {"title": "Kimya: Organik Kimya", "desc": "Karbon bilesikleri.", "content": "Molekuler yapi..."}
            ]
            for c in sample_courses:
                add_sample_course(db, c["title"], c["desc"], c["content"])
            st.success("Ornek veriler yuklendi!")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 3: System Info
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("Sistem Bilgisi")
    scol1, scol2, scol3 = st.columns(3)
    scol1.metric("Versiyon", "v1.0.0")
    scol2.metric("Durum", "Kararli")
    scol3.metric("Son Guncelleme", datetime.now().strftime("%d/%m/%Y"))
    st.markdown('</div>', unsafe_allow_html=True)
