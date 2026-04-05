import streamlit as st
import pandas as pd
from database import init_db, get_db, add_chat_message, get_chat_history, add_sample_course, get_all_courses, delete_course
from ai_service import ai_service
import os
import io
from datetime import datetime
from fpdf import FPDF

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
    curr_idx = pages.index(st.session_state.page)
    sel_page = st.radio("Navigasyon", pages, index=curr_idx)
    if sel_page != st.session_state.page: st.session_state.page = sel_page; st.rerun()
    st.divider()

# --- HELPERS ---
def tr_fix(text):
    """Fallback: Replaces Turkish characters if PDF font doesn't support them."""
    chars = {"ğ": "g", "Ğ": "G", "ı": "i", "İ": "I", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in chars.items(): text = text.replace(k, v)
    return text

def export_excel(courses):
    df = pd.DataFrame([{"Baslik": c.title, "Aciklama": c.description, "Icerik": c.content} for c in courses])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False)
    return output.getvalue()

def export_pdf(content, title="Rapor"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", style='B', size=16)
    # Clean text to avoid encoding errors on standard PDF fonts
    pdf.cell(200, 10, txt=tr_fix(title), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("helvetica", size=12)
    pdf.multi_cell(0, 10, txt=tr_fix(content))
    return pdf.output()

# --- PAGE: HOME ---
if st.session_state.page == "Ana Sayfa":
    st.markdown('<div style="text-align: center; padding: 20px 0;"><h1 style="font-size: 3rem; margin-bottom:0;">LMS Yapay Zeka Final</h1><p style="font-size: 1.2rem; opacity: 0.8;">Yapay Zeka Destekli Yeni Nesil Eğitim</p></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('<div class="stat-card"><div class="stat-value">12</div><div class="stat-label">Ders Sayısı</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="stat-card"><div class="stat-value">156</div><div class="stat-label">Öğrenci</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="stat-card"><div class="stat-value">4.8</div><div class="stat-label">Puan</div></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="stat-card"><div class="stat-value">850+</div><div class="stat-label">AI Yanıtı</div></div>', unsafe_allow_html=True)
    st.divider(); st.markdown("### Platform Özellikleri")
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        st.markdown('<div class="feature-card"><h4>Akıllı Sohbet</h4><p style="font-size:0.8rem; opacity:0.8;">Anlık AI asistanlığı.</p></div>', unsafe_allow_html=True)
        if st.button("Sohbete Başla", use_container_width=True, key="h_chat"): navigate_to("AI Sohbet")
    with fcol2:
        st.markdown('<div class="feature-card"><h4>Quiz Hazırlayıcı</h4><p style="font-size:0.8rem; opacity:0.8;">Hızlı sınavlar oluşturun.</p></div>', unsafe_allow_html=True)
        if st.button("Hemen Hazırla", use_container_width=True, key="h_quiz"): navigate_to("Quiz Hazirla")
    with fcol3:
        st.markdown('<div class="feature-card"><h4>Ders Arşivi</h4><p style="font-size:0.8rem; opacity:0.8;">İçerikleri yönetin.</p></div>', unsafe_allow_html=True)
        if st.button("Derslere Git", use_container_width=True, key="h_course"): navigate_to("Ders Materyalleri")

# --- PAGE: AI CHAT ---
elif st.session_state.page == "AI Sohbet":
    st.title("AI Egitmen Asistani")
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
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([0.7, 0.3])
    with col1: topic = st.text_input("Konu Girin", placeholder="Ör: Fotosentez")
    with col2: q_count = st.slider("Adet", 3, 15, 5)
    model = st.selectbox("Model", ["Groq", "Gemini"])
    if st.button("Sinavi Olustur", use_container_width=True, type="primary"):
        if topic:
            with st.spinner("Sorular hazirlaniyor..."):
                st.session_state.quiz_content = ai_service.ask(f"{topic} konusu hakkinda {q_count} adet coktan secmeli soru iceren bir sinav hazirla. Secenekler ve cevap anahtari en sonda olsun. Turkce.", provider=model.lower())
        else: st.error("Bir konu girin.")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.quiz_content:
        st.markdown('<div class="settings-card">', unsafe_allow_html=True); st.markdown(st.session_state.quiz_content)
        pdf = bytes(export_pdf(st.session_state.quiz_content, title=f"SINAV: {topic.upper()}"))
        st.download_button("PDF İndir", pdf, file_name=f"sinav.pdf", mime="application/pdf", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: COURSES ---
elif st.session_state.page == "Ders Materyalleri":
    st.title("Ders Arşivi"); db_gen = get_db(); db = next(db_gen); tab1, tab2 = st.tabs(["Listele", "Ekle"])
    with tab1:
        courses = get_all_courses(db)
        if courses:
            st.markdown('<div class="settings-card" style="padding:15px; margin-bottom:20px;">', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.download_button("Excel İndir", export_excel(courses), "dersler.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with c2: 
                pdf_raw = "\n\n".join([f"**{c.title}**\n{c.description}\n{c.content}" for c in courses])
                st.download_button("PDF İndir", bytes(export_pdf(pdf_raw, title="Ders Arşivi")), "dersler.pdf", "application/pdf", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            for c in courses:
                col1, col2 = st.columns([0.9, 0.1])
                with col1: 
                    with st.expander(c.title): st.write(c.content)
                with col2:
                    if st.button("Sil", key=f"del_{c.id}", type="primary"): delete_course(db, c.id); st.rerun()

# --- PAGE: VERI ANALIZI ---
elif st.session_state.page == "Veri Analizi":
    st.title("Veri Analizi"); st.bar_chart(pd.DataFrame({'Ders': ['Mat', 'Cog', 'Res', 'Edb'], 'Puan': [85, 72, 95, 68]}))

# --- PAGE: SETTINGS ---
elif st.session_state.page == "Ayarlar":
    st.title("Ayarlar")
    if st.button("Verileri Sıfırla", type="primary"):
        db_gen = get_db(); db = next(db_gen); from sqlalchemy import delete; from models import Course, ChatHistory; db.execute(delete(Course)); db.execute(delete(ChatHistory)); db.commit(); st.rerun()
