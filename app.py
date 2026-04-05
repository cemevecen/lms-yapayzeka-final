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

p = load_settings()
states = {
    'ui_accent': p.get('ui_accent', "#1f77b4"),
    'ai_temp': p.get('ai_temp', 0.7),
    'ai_tokens': p.get('ai_tokens', 2048),
    'ai_system': p.get('ai_system', "Sen profesyonel bir Eğitim Asistanısın."),
    'ui_glass': p.get('ui_glass', 0.8),
    'chart_type': p.get('chart_type', "Bar"),
    'default_model': p.get('default_model', "Groq"),
    'course_expanded': p.get('course_expanded', False),
    'pdf_pagenums': p.get('pdf_pagenums', True),
    'page': "Ana Sayfa",
    'quiz_content': "",
    'current_quiz_title': ""
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

st.set_page_config(page_title="LMS Yapay Zeka Final", page_icon=None, layout="wide", initial_sidebar_state="expanded")
def navigate_to(pname): st.session_state.page = pname; st.rerun()
init_db()

accent = st.session_state.ui_accent
glass = st.session_state.ui_glass
st.markdown(f"""
<style>
    :root {{ --primary-color: {accent}; }}
    .stApp {{ background: var(--background-content-color); }}
    [data-testid="stSidebar"] {{ background-color: var(--secondary-background-color); border-right: 1px solid var(--divider-color); }}
    .settings-card {{ 
        background: rgba(255, 255, 255, {glass*0.05 if glass < 1 else 0.1}); 
        backdrop-filter: blur({glass*10}px);
        padding: 25px; border-radius: 20px; border: 1px solid var(--divider-color); margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    }}
    .stat-card {{ background: var(--secondary-background-color); padding: 24px; border-radius: 16px; border: 1px solid var(--divider-color); text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
    .stat-card:hover {{ transform: translateY(-5px); border-color: {accent}; }}
    .stat-value {{ font-size: 28px; font-weight: 800; color: {accent}; }}
    .stButton>button {{ border-radius: 10px; font-weight: 600; transition: all 0.2s ease; border: 1px solid {accent}; }}
    .stButton>button:hover {{ background: {accent}; color: white; }}
</style>
""", unsafe_allow_html=True)

pages = ["Ana Sayfa", "AI Sohbet", "Ders Materyalleri", "Quiz Hazirla", "Veri Analizi", "Ayarlar"]
with st.sidebar:
    st.title("AI-LMS Pro"); st.divider()
    s_page = st.radio("Navigasyon", pages, index=pages.index(st.session_state.page))
    if s_page != st.session_state.page: st.session_state.page = s_page; st.rerun()

# --- HELPERS ---
def tr_fix(text):
    c = {"ğ":"g","Ğ":"G","ı":"i","İ":"I","ş":"s","Ş":"S","ü":"u","Ü":"U","ö":"o","Ö":"O","ç":"c","Ç":"C"}
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
    st.divider(); st.markdown("### Navigasyon Kısayolları")
    c1, c2, c3 = st.columns(3);
    with c1: 
        if st.button("Sohbete Başla", use_container_width=True): navigate_to("AI Sohbet")
    with c2: 
        if st.button("Hemen Quiz Hazırla", use_container_width=True): navigate_to("Quiz Hazirla")
    with c3: 
        if st.button("Analizlere Git", use_container_width=True): navigate_to("Veri Analizi")

elif st.session_state.page == "AI Sohbet":
    st.title("AI Eğitmen Asistanı")
    st.info(f"Yapay Zeka Karakteri: {st.session_state.ai_system}")
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
    with c1: topic = st.text_input("Konu")
    with c2: q_count = st.slider("Soru Adedi", 3, 20, 5)
    if st.button("AI Sınav Oluştur", use_container_width=True, type="primary"):
        if topic:
            with st.spinner("AI Yanıtlıyor..."):
                st.session_state.quiz_content = ai_service.ask(f"{topic} hakkında {q_count} soruluk test hazırla.", temp=st.session_state.ai_temp, tokens=st.session_state.ai_tokens)
                st.session_state.current_quiz_title = topic
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.quiz_content:
        st.markdown('<div class="settings-card">', unsafe_allow_html=True); st.markdown(st.session_state.quiz_content)
        st.download_button("PDF Olarak İndir", bytes(export_pdf(st.session_state.quiz_content, title="SINAV")), file_name="sinav.pdf", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Ders Materyalleri":
    st.title("Ders Arşivi"); db_gen = get_db(); db = next(db_gen); courses = get_all_courses(db)
    if courses:
        for c in courses:
            with st.expander(c.title, expanded=st.session_state.course_expanded): st.write(c.content)

elif st.session_state.page == "Veri Analizi":
    st.title("Gelişmiş Veri Analizi"); db_gen = get_db(); db = next(db_gen); courses = get_all_courses(db); quiz_res = get_quiz_results(db)
    t1, t2, t3 = st.tabs(["Ders Başarı Göstergeleri", "Sistem Analizi", "Manuel Puan Girişi"])
    with t1:
        st.subheader("Öğrenci Başarı Analizi")
        if quiz_res:
            res_df = pd.DataFrame([{"Öğrenci": r.student_name, "Puan": r.score, "Sınav": r.quiz_title} for r in quiz_res])
            
            # KPI Metrics with "Last Entered Grade"
            m1, m2, m3 = st.columns(3)
            m1.metric("Sınıf Ortalaması", round(res_df["Puan"].mean(), 1))
            m2.metric("En Yüksek Puan", res_df["Puan"].max())
            
            # The "Last Entered" metric
            last_entry = res_df.iloc[0] # Results sorted by creation date desc
            m3.metric("Son Girilen Not", f"{last_entry['Puan']}", delta=f"{last_entry['Öğrenci']}")
            
            if st.session_state.chart_type == "Bar": st.bar_chart(res_df.set_index("Öğrenci")["Puan"], color=accent)
            elif st.session_state.chart_type == "Line": st.line_chart(res_df.set_index("Öğrenci")["Puan"], color=accent)
            else: st.area_chart(res_df.set_index("Öğrenci")["Puan"], color=accent)
            st.dataframe(res_df, use_container_width=True)
        else:
            st.info("Henüz sınav sonucu bulunmuyor.")
            if st.button("Hemen Simüle Et (15 Öğrenci)", key="ana_sim"):
                for n in ["Ahmet","Fatma","Can","Selin","Burak","Elif","Mehmet","Ayşe","Deniz","Zeynep","Emir","Melis","Okan","Gizem","Arda"]: add_quiz_result(db, "Genel Değerlendirme", n, random.randint(72,100))
                st.rerun()
    with t2:
        st.subheader("Sistem Kullanım Verileri")
        if courses:
            df = pd.DataFrame({'Ders': [c.title for c in courses], 'Uzunluk': [len(c.content) for c in courses]})
            st.bar_chart(df, x='Ders', y='Uzunluk', color=accent)
    with t3:
        st.subheader("Yeni Puan Girişi")
        with st.form("man_entry"):
            name = st.text_input("Öğrenci Adı"); quiz = st.text_input("Sınav Konusu"); score = st.number_input("Puan", 0, 100, 85)
            if st.form_submit_button("Sisteme İşle"):
                if name and quiz: add_quiz_result(db, quiz, name, score); st.success(f"{name} için not başarıyla işlendi!"); st.rerun()
                else: st.error("Lütfen alanları doldurun.")

elif st.session_state.page == "Ayarlar":
    st.title("Denetleme Masası")
    st.markdown('<div class="settings-card"><h4>AI Derin Yapılandırma</h4>', unsafe_allow_html=True)
    st.session_state.ai_system = st.text_area("Sistem Rolü", value=st.session_state.ai_system)
    c1, c2 = st.columns(2)
    with c1: st.session_state.ai_temp = st.slider("Temperature", 0.0, 1.0, st.session_state.ai_temp, 0.1)
    with c2: st.session_state.ai_tokens = st.select_slider("Maksimum Tokens", options=[256, 512, 1024, 2048, 4096, 8192], value=st.session_state.ai_tokens)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="settings-card"><h4>Görünüm</h4>', unsafe_allow_html=True)
    cu1, cu2 = st.columns(2)
    with cu1:
        c_map = {"Mavi": "#1f77b4", "Yeşil": "#2ecc71", "Mor": "#9b59b6", "Turuncu": "#e67e22", "Kırmızı": "#e74c3c"}
        sel = st.selectbox("Renk", list(c_map.keys()), index=list(c_map.values()).index(st.session_state.ui_accent))
        if c_map[sel] != st.session_state.ui_accent: st.session_state.ui_accent = c_map[sel]; st.rerun()
    with cu2: st.session_state.ui_glass = st.slider("Cam Yoğunluğu", 0.0, 1.0, st.session_state.ui_glass, 0.1)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Ayarları Kalıcı Kaydet", type="primary", use_container_width=True):
        save_settings_to_disk({'ui_accent': st.session_state.ui_accent, 'ai_temp': st.session_state.ai_temp, 'ai_tokens': st.session_state.ai_tokens, 'ai_system': st.session_state.ai_system, 'ui_glass': st.session_state.ui_glass, 'chart_type': st.session_state.chart_type, 'default_model': st.session_state.default_model, 'course_expanded': st.session_state.course_expanded, 'pdf_pagenums': st.session_state.pdf_pagenums})
        st.success("Kaydedildi!"); st.balloons()
    st.divider()
    if st.button("Fabrika Ayarlarina Dön", use_container_width=True):
        db_gen = get_db(); db = next(db_gen); from sqlalchemy import delete; from models import Course, ChatHistory, QuizResult; db.execute(delete(Course)); db.execute(delete(ChatHistory)); db.execute(delete(QuizResult)); db.commit(); st.rerun()
