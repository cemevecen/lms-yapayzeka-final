import streamlit as st
import pandas as pd
from database import init_db, get_db, add_chat_message, get_chat_history, add_sample_course, get_all_courses, delete_course
from ai_service import ai_service
import os
import io
from datetime import datetime
try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None

# Page Configuration
st.set_page_config(page_title="LMS Yapay Zeka Final", page_icon=None, layout="wide", initial_sidebar_state="expanded")

# Initialize Session State
if 'page' not in st.session_state: st.session_state.page = "Ana Sayfa"
if 'quiz_content' not in st.session_state: st.session_state.quiz_content = ""

def navigate_to(page_name): st.session_state.page = page_name; st.rerun()

init_db()

# Custom CSS
st.markdown("""
<style>
    .stApp { background: var(--background-content-color); }
    [data-testid="stSidebar"] { background-color: var(--secondary-background-color); border-right: 1px solid var(--divider-color); }
    .stat-card {
        background: var(--secondary-background-color);
        padding: 24px; border-radius: 16px; border: 1px solid var(--divider-color); text-align: center;
        transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .stat-card:hover { transform: translateY(-5px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); border-color: #1f77b4; }
    .stat-value { font-size: 28px; font-weight: 800; color: #1f77b4; margin-bottom: 4px; }
    .stat-label { font-size: 14px; color: var(--text-color); opacity: 0.8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .feature-card {
        background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color);
        height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 10px;
    }
    .settings-card {
        background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color);
        margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight:600; margin-left: 10px; }
    .status-active { background: #2ecc71; color: white; }
    .status-passive { background: #e74c3c; color: white; }
    .stButton>button { border-radius: 10px; font-weight: 600; padding: 0.5rem 1rem; transition: all 0.2s ease; }
</style>
""", unsafe_allow_html=True)

# Sidebar
pages = ["Ana Sayfa", "AI Sohbet", "Ders Materyalleri", "Quiz Hazirla", "Veri Analizi", "Ayarlar"]
with st.sidebar:
    st.title("AI-LMS Dashboard"); st.divider()
    current_index = pages.index(st.session_state.page)
    selected_page = st.radio("Navigasyon", pages, index=current_index)
    if selected_page != st.session_state.page: st.session_state.page = selected_page; st.rerun()
    st.divider()

# --- HELPERS ---
def export_excel(courses):
    df = pd.DataFrame([{"Baslik": c.title, "Aciklama": c.description, "Icerik": c.content} for c in courses])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False)
    return output.getvalue()

def export_pdf(content, title="Rapor"):
    if pisa is None: raise ImportError("PDF motoru yukleniyor, bekleyin.")
    html = f"<html><head><meta charset='UTF-8'><style>body {{ font-family: Helvetica, Arial, sans-serif; padding: 30px; }} h1 {{ color: #1f77b4; text-align: center; }} .content {{ line-height: 1.6; font-size: 12px; white-space: pre-wrap; }}</style></head><body><h1>{title}</h1><hr><div class='content'>{content}</div></body></html>"
    result = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=result, encoding='UTF-8')
    return result.getvalue()

# --- PAGE: HOME ---
if st.session_state.page == "Ana Sayfa":
    st.markdown('<div style="text-align: center; padding: 20px 0;"><h1 style="font-size: 3rem; margin-bottom:0;">LMS Yapay Zeka Final</h1><p style="font-size: 1.2rem; opacity: 0.8;">Eğitimde Yeni Nesil Yapay Zeka Deneyimi</p></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('<div class="stat-card"><div class="stat-value">12</div><div class="stat-label">Ders Sayısı</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="stat-card"><div class="stat-value">156</div><div class="stat-label">Öğrenci</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="stat-card"><div class="stat-value">4.8</div><div class="stat-label">Puan</div></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="stat-card"><div class="stat-value">850+</div><div class="stat-label">AI Yanıtı</div></div>', unsafe_allow_html=True)
    st.divider(); st.markdown("### Platform Özellikleri")
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        st.markdown('<div class="feature-card"><h4>Akıllı Sohbet</h4><p style="font-size:0.8rem; opacity:0.8;">AI ile anlık soru-cevap.</p></div>', unsafe_allow_html=True)
        if st.button("Sohbete Başla", use_container_width=True, key="h_go_chat"): navigate_to("AI Sohbet")
    with fcol2:
        st.markdown('<div class="feature-card"><h4>Quiz Hazırlayıcı</h4><p style="font-size:0.8rem; opacity:0.8;">Saniyeler içinde sınav hazırlayın.</p></div>', unsafe_allow_html=True)
        if st.button("Sınav Hazırla", use_container_width=True, key="h_go_quiz"): navigate_to("Quiz Hazirla")
    with fcol3:
        st.markdown('<div class="feature-card"><h4>Ders Arşivi</h4><p style="font-size:0.8rem; opacity:0.8;">Tüm içerikleri yönetin.</p></div>', unsafe_allow_html=True)
        if st.button("Dersleri Gör", use_container_width=True, key="h_go_courses"): navigate_to("Ders Materyalleri")

# --- PAGE: AI CHAT ---
elif st.session_state.page == "AI Sohbet":
    st.title("AI Egitmen Asistani")
    c1, c2 = st.columns([0.8, 0.2])
    with c2: 
        if st.button("Temizle", use_container_width=True):
            db_gen = get_db(); db = next(db_gen); from sqlalchemy import delete; from models import ChatHistory; db.execute(delete(ChatHistory)); db.commit(); st.rerun()
    use_groq = st.toggle("Groq Modu", value=True)
    ai_provider = "Groq" if use_groq else "Gemini"
    db_gen = get_db(); db = next(db_gen); history = get_chat_history(db)
    for chat in history[-15:]:
        with st.chat_message(chat.role): st.markdown(chat.message)
    if pr := st.chat_input("Dersinle ilgili sor..."):
        with st.chat_message("user"): st.markdown(pr)
        add_chat_message(db, "user", pr, ai_provider)
        with st.chat_message("assistant"):
            with st.spinner(f"{ai_provider}..."):
                res = ai_service.ask(pr, provider=ai_provider.lower()); st.markdown(res); add_chat_message(db, "assistant", res, ai_provider)

# --- PAGE: QUIZ ---
elif st.session_state.page == "Quiz Hazirla":
    st.title("AI Sinav Hazirlayici")
    st.caption("Yapay zeka ile diledigin konuda aninda sınav veya test hazırlayın.")
    
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        topic = st.text_input("Sinav Konusu veya Ders Basligi", placeholder="Ornegin: Osmanli Yukselme Donemi veya Fotosentez")
    with col2:
        q_count = st.slider("Soru Sayisi", 3, 15, 5)
    
    provider = st.selectbox("AI Modeli Secin", ["Groq", "Gemini"])
    
    if st.button("Sinavi Olustur", use_container_width=True, type="primary"):
        if topic:
            with st.spinner("Sorular hazirlaniyor..."):
                prompt = f"{topic} konusu hakkinda {q_count} adet coktan secmeli soru iceren bir sinav hazirla. Her sorunun A,B,C,D secenekleri ve sonunda cevap anahtari olsun. Dil: Turkce."
                st.session_state.quiz_content = ai_service.ask(prompt, provider=provider.lower())
        else:
            st.error("Lutfen bir konu girin.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.quiz_content:
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.subheader("Hazirlanan Sinav")
        st.markdown(st.session_state.quiz_content)
        
        # Download as PDF
        pdf_ready = export_pdf(st.session_state.quiz_content, title=f"SINAV: {topic.upper()}")
        st.download_button("Sinavi PDF Olarak Indir", pdf_ready, file_name=f"sinav_{datetime.now().strftime('%d%m%y')}.pdf", mime="application/pdf", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: COURSES ---
elif st.session_state.page == "Ders Materyalleri":
    st.title("Ders Arşivi"); db_gen = get_db(); db = next(db_gen); tab1, tab2 = st.tabs(["Listele", "Ekle"])
    with tab1:
        courses = get_all_courses(db)
        if courses:
            for c in courses:
                exp_col, del_col = st.columns([0.9, 0.1])
                with exp_col: 
                    with st.expander(c.title): st.write(c.content)
                with del_col:
                    if st.button("Sil", key=f"d_{c.id}", type="primary"): delete_course(db, c.id); st.rerun()

# --- PAGE: VERI ANALIZI ---
elif st.session_state.page == "Veri Analizi":
    st.title("Veri Analizi"); st.bar_chart(pd.DataFrame({'Ders': ['Mat', 'Cog', 'Res', 'Edb'], 'Puan': [85, 72, 95, 68]}))

# --- PAGE: SETTINGS ---
elif st.session_state.page == "Ayarlar":
    st.title("Sistem Yonetimi")
    if st.button("Veritabanini Sifirla", type="primary"):
        db_gen = get_db(); db = next(db_gen); from sqlalchemy import delete; from models import Course, ChatHistory; db.execute(delete(Course)); db.execute(delete(ChatHistory)); db.commit(); st.rerun()
