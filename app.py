import streamlit as st
import pandas as pd
import random
from database import init_db, get_db, add_chat_message, get_chat_history, add_sample_course, get_all_courses, delete_course, add_quiz_result, get_quiz_results
from ai_service import ai_service
import os
import io
import json
from datetime import datetime
from fpdf import FPDF

# --- PERSISTENT SETTINGS ---
SETTINGS_FILE = "persistent_settings.json"
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f: return json.load(f)
    return {}
def save_settings_to_disk(data):
    with open(SETTINGS_FILE, "w") as f: json.dump(data, f)

p_settings = load_settings()
if 'ui_accent' not in st.session_state: st.session_state.ui_accent = p_settings.get('ui_accent', "#1f77b4")
if 'ai_temp' not in st.session_state: st.session_state.ai_temp = p_settings.get('ai_temp', 0.7)
if 'ai_tokens' not in st.session_state: st.session_state.ai_tokens = 2048
if 'default_model' not in st.session_state: st.session_state.default_model = p_settings.get('default_model', "Groq")
if 'course_expanded' not in st.session_state: st.session_state.course_expanded = p_settings.get('course_expanded', False)
if 'pdf_pagenums' not in st.session_state: st.session_state.pdf_pagenums = p_settings.get('pdf_pagenums', True)
if 'page' not in st.session_state: st.session_state.page = "Ana Sayfa"
if 'quiz_content' not in st.session_state: st.session_state.quiz_content = ""
if 'current_quiz_title' not in st.session_state: st.session_state.current_quiz_title = ""

# Page Configuration
st.set_page_config(page_title="LMS Yapay Zeka Final", page_icon=None, layout="wide", initial_sidebar_state="expanded")
def navigate_to(page_name): st.session_state.page = page_name; st.rerun()

init_db()

# Custom Dynamic CSS
accent = st.session_state.ui_accent
st.markdown(f"""
<style>
    :root {{ --primary-color: {accent}; }}
    .stApp {{ background: var(--background-content-color); }}
    [data-testid="stSidebar"] {{ background-color: var(--secondary-background-color); border-right: 1px solid var(--divider-color); }}
    .settings-card {{ background: var(--secondary-background-color); padding: 25px; border-radius: 20px; border: 1px solid var(--divider-color); margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
    .stButton>button {{ border-radius: 10px; font-weight: 600; transition: all 0.2s ease; border: 1px solid {accent}; }}
    .stButton>button:hover {{ background: {accent}; color: white; }}
    .stat-card {{ background: var(--secondary-background-color); padding: 24px; border-radius: 16px; border: 1px solid var(--divider-color); text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
</style>
""", unsafe_allow_html=True)

# Sidebar
pages = ["Ana Sayfa", "AI Sohbet", "Ders Materyalleri", "Quiz Hazirla", "Veri Analizi", "Ayarlar"]
with st.sidebar:
    st.title("AI-LMS Panel"); st.divider()
    curr_idx = pages.index(st.session_state.page)
    sel_page = st.radio("Navigasyon", pages, index=curr_idx)
    if sel_page != st.session_state.page: st.session_state.page = sel_page; st.rerun()
    st.divider()

# --- HELPERS ---
def tr_fix(text):
    c = {"ğ": "g", "Ğ": "G", "ı": "i", "İ": "I", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in c.items(): text = text.replace(k, v)
    return text

def export_pdf(content, title="Rapor"):
    pdf = FPDF()
    pdf.add_page(); pdf.set_font("helvetica", style='B', size=16); pdf.cell(200, 10, txt=tr_fix(title), ln=True, align='C'); pdf.ln(10)
    pdf.set_font("helvetica", size=11); pdf.multi_cell(0, 10, txt=tr_fix(content))
    return pdf.output()

# --- PAGES ---
if st.session_state.page == "Ana Sayfa":
    db_gen = get_db(); db = next(db_gen); courses = get_all_courses(db); history = get_chat_history(db)
    st.markdown(f'<div style="text-align:center; padding:20px 0;"><h1 style="font-size:3rem; margin-bottom:0; color:{accent};">LMS Yapay Zeka Final</h1><p style="font-size:1.2rem; opacity:0.8;">Eğitimde Yeni Nesil Analitik Deneyim</p></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'<div class="stat-card"><div class="stat-value">{len(courses)}</div><div class="stat-label">Dersler</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="stat-card"><div class="stat-value">{len(history)}</div><div class="stat-label">AI Mesajları</div></div>', unsafe_allow_html=True)
    st.divider(); st.markdown("### Hızlı Kısayollar")
    c1, c2, c3 = st.columns(3);
    with c1: 
        if st.button("Sohbete Git", use_container_width=True): navigate_to("AI Sohbet")
    with c2: 
        if st.button("Sınav Hazırla", use_container_width=True): navigate_to("Quiz Hazirla")
    with c3: 
        if st.button("Analiz Göster", use_container_width=True): navigate_to("Veri Analizi")

elif st.session_state.page == "AI Sohbet":
    st.title("AI Eğitmen Asistanı")
    use_groq = st.toggle("Groq Modu", value=(st.session_state.default_model == "Groq"))
    ai_p = "Groq" if use_groq else "Gemini"
    db_gen = get_db(); db = next(db_gen); history = get_chat_history(db)
    for chat in history[-10:]:
        with st.chat_message(chat.role): st.markdown(chat.message)
    if pr := st.chat_input("Mesajınızı yazın..."):
        with st.chat_message("user"): st.markdown(pr)
        add_chat_message(db, "user", pr, ai_p)
        with st.chat_message("assistant"):
            res = ai_service.ask(pr, provider=ai_p.lower(), temp=st.session_state.ai_temp, tokens=st.session_state.ai_tokens)
            st.markdown(res); add_chat_message(db, "assistant", res, ai_p)

elif st.session_state.page == "Quiz Hazirla":
    st.title("Sınav Hazırlayıcı"); st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.7, 0.3])
    with c1: topic = st.text_input("Konu", placeholder="Ör: Fotosentez")
    with c2: q_count = st.slider("Adet", 3, 20, 5)
    model = st.selectbox("Model", ["Groq", "Gemini"], index=0 if st.session_state.default_model=="Groq" else 1)
    if st.button("Sınavı Oluştur", use_container_width=True, type="primary"):
        if topic:
            with st.spinner("Hazırlanıyor..."):
                st.session_state.quiz_content = ai_service.ask(f"{topic} hakkında {q_count} soruluk bir test hazırla.", provider=model.lower(), temp=st.session_state.ai_temp, tokens=st.session_state.ai_tokens)
                st.session_state.current_quiz_title = topic
        else: st.error("Bir konu girin.")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.quiz_content:
        st.markdown('<div class="settings-card">', unsafe_allow_html=True); st.markdown(st.session_state.quiz_content)
        st.download_button("PDF İndir", bytes(export_pdf(st.session_state.quiz_content, title=f"SINAV: {st.session_state.current_quiz_title}")), file_name="sinav.pdf", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Ders Materyalleri":
    st.title("Ders Arşivi"); db_gen = get_db(); db = next(db_gen); tab1, tab2 = st.tabs(["Listele", "Ekle"])
    with tab1:
        courses = get_all_courses(db)
        if courses:
            for c in courses:
                col1, col2 = st.columns([0.9, 0.1])
                with col1: 
                    with st.expander(c.title, expanded=st.session_state.course_expanded): st.write(c.content)
                with col2:
                    if st.button("Sil", key=f"del_{c.id}", type="primary"): delete_course(db, c.id); st.rerun()

elif st.session_state.page == "Veri Analizi":
    st.title("Veri Analizi Paneli"); db_gen = get_db(); db = next(db_gen)
    courses = get_all_courses(db); quiz_res = get_quiz_results(db)
    
    t1, t2, t3 = st.tabs(["Sistem Analizi", "Ders Başarı Göstergeleri", "Manuel Puan Girişi"])
    with t1:
        if courses:
            c_df = pd.DataFrame({'Ders': [c.title for c in courses], 'Uzunluk': [len(c.content) for c in courses]})
            st.bar_chart(data=c_df, x='Ders', y='Uzunluk', color=accent)
    with t2:
        if quiz_res:
            res_df = pd.DataFrame([{"Öğrenci": r.student_name, "Puan": r.score, "Sınav": r.quiz_title} for r in quiz_res])
            m1, m2 = st.columns(2); m1.metric("Sınıf Ortalaması", round(res_df["Puan"].mean(), 1)); m2.metric("Toplam Kayıt", len(res_df))
            st.line_chart(res_df.set_index("Öğrenci")["Puan"], color=accent)
            st.dataframe(res_df, use_container_width=True)
        else:
            st.info("Henüz sınav sonucu yok.")
            if st.button("Simülasyon Verisi Yükle (15 Kişi)", use_container_width=True):
                names = ["Ahmet", "Fatma", "Can", "Selin", "Burak", "Elif", "Mehmet", "Ayşe", "Deniz", "Zeynep", "Emir", "Melis", "Okan", "Gizem", "Arda"]
                for n in names: add_quiz_result(db, "Genel Değerlendirme", n, random.randint(70,100))
                st.rerun()
    with t3:
        st.subheader("Yeni Öğrenci Puanı Kaydet")
        with st.form("manual_entry"):
            m_student = st.text_input("Öğrenci Adı Soyadı")
            m_quiz = st.text_input("Sınav Başlığı / Konusu", placeholder="Ör: Vize 1")
            m_score = st.number_input("Aldığı Puan", 0, 100, 85)
            if st.form_submit_button("Sisteme Kaydet", use_container_width=True):
                if m_student and m_quiz:
                    add_quiz_result(db, m_quiz, m_student, m_score)
                    st.success(f"{m_student} için {m_score} puanı başarıyla kaydedildi!")
                    st.rerun()
                else: st.error("Lütfen tüm alanları doldurun.")

elif st.session_state.page == "Ayarlar":
    st.title("Sistem Ayarları"); st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.session_state.ai_temp = st.slider("Temperature", 0.0, 1.0, st.session_state.ai_temp, 0.1)
    color_map = {"Mavi": "#1f77b4", "Yeşil": "#2ecc71", "Mor": "#9b59b6", "Turuncu": "#e67e22"}
    sel_c = st.selectbox("Tema Rengi", list(color_map.keys()), index=list(color_map.values()).index(st.session_state.ui_accent))
    if color_map[sel_c] != st.session_state.ui_accent: st.session_state.ui_accent = color_map[sel_c]; st.rerun()
    if st.button("Ayarları Kaydet", type="primary", use_container_width=True):
        save_settings_to_disk({'ui_accent': st.session_state.ui_accent, 'ai_temp': st.session_state.ai_temp, 'ai_tokens': st.session_state.ai_tokens, 'default_model': st.session_state.default_model, 'course_expanded': st.session_state.course_expanded, 'pdf_pagenums': st.session_state.pdf_pagenums})
        st.success("Kaydedildi!"); st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Veritabanını Sıfırla (Tehlikeli)"):
        db_gen = get_db(); db = next(db_gen); from sqlalchemy import delete; from models import Course, ChatHistory, QuizResult; db.execute(delete(Course)); db.execute(delete(ChatHistory)); db.execute(delete(QuizResult)); db.commit(); st.rerun()
