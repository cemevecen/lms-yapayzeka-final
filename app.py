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
    'page': "Ana Sayfa",
    'quiz_content': "",
    'current_quiz_title': ""
}
for k, v in states.items():
    if k not in st.session_state: st.session_state[k] = v

st.set_page_config(page_title="LMS Yapay Zeka Pro", page_icon=None, layout="wide", initial_sidebar_state="expanded")
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
        backdrop-filter: blur({glass*10}px); padding: 25px; border-radius: 20px; border: 1px solid var(--divider-color); margin-bottom: 20px; 
    }}
    .stat-box {{
        background: var(--secondary-background-color); padding: 20px; border-radius: 15px; border: 1px solid var(--divider-color);
        text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05); min-width: 150px;
    }}
    .stat-val {{ font-size: 32px; font-weight: 850; color: {accent}; }}
    .nav-card {{
        background: var(--secondary-background-color); padding: 25px; border-radius: 20px; border: 1px solid var(--divider-color);
        transition: all 0.3s; cursor: pointer; text-align: center; min-height: 180px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }}
    .nav-card:hover {{ transform: translateY(-10px); border-color: {accent}; box-shadow: 0 12px 24px rgba(0,0,0,0.1); }}
    .stButton>button {{ border-radius: 12px; font-weight: 600; transition: all 0.2s; border: 1px solid {accent}; }}
</style>
""", unsafe_allow_html=True)

def navigate_to(pname): st.session_state.page = pname; st.rerun()

# Navigation
pages = ["Ana Sayfa", "AI Sohbet", "Ders Materyalleri", "Quiz Hazirla", "Veri Analizi", "Ayarlar"]
with st.sidebar:
    st.title("AI-LMS Pro"); st.divider()
    s_page = st.radio("Navigasyon", pages, index=pages.index(st.session_state.page))
    if s_page != st.session_state.page: st.session_state.page = s_page; st.rerun()

# --- PAGES ---
if st.session_state.page == "Ana Sayfa":
    db_gen = get_db(); db = next(db_gen); courses = get_all_courses(db); history = get_chat_history(db)
    if os.path.exists("banner.png"): st.image("banner.png", use_container_width=True)
    st.markdown("### Sistem İstatistikleri")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1: st.markdown(f'<div class="stat-box"><div class="stat-val">{len(courses)}</div><div class="stat-lab">Arşiv</div></div>', unsafe_allow_html=True)
    with sc2: st.markdown(f'<div class="stat-box"><div class="stat-val">{len(history)}</div><div class="stat-lab">AI Yanıtı</div></div>', unsafe_allow_html=True)
    with sc3: st.markdown(f'<div class="stat-box"><div class="stat-val">Online</div><div class="stat-lab">Durum</div></div>', unsafe_allow_html=True)
    
    st.divider(); st.markdown("### Hizmet Paneli")
    nc1, nc2, nc3 = st.columns(3)
    with nc1:
        st.markdown('<div class="nav-card"><h3>💬 Sohbet</h3><p style="opacity:0.7;">AI ile anında bilgi alın.</p></div>', unsafe_allow_html=True)
        if st.button("AI Sohbet Paneli", use_container_width=True, key="nh_chat"): navigate_to("AI Sohbet")
    with nc2:
        st.markdown('<div class="nav-card"><h3>📝 Sınav</h3><p style="opacity:0.7;">Quizler hazırlayın.</p></div>', unsafe_allow_html=True)
        if st.button("Hemen Quiz Hazırla", use_container_width=True, key="nh_quiz"): navigate_to("Quiz Hazirla")
    with nc3:
        st.markdown('<div class="nav-card"><h3>📊 Analiz</h3><p style="opacity:0.7;">Başarı takibi.</p></div>', unsafe_allow_html=True)
        if st.button("Verileri İncele", use_container_width=True, key="nh_ana"): navigate_to("Veri Analizi")

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
    st.title("Sınav Hazırlayıcı")
    c1, c2 = st.columns([0.7, 0.3])
    with c1: topic = st.text_input("Sınav Başlığı")
    with c2: q_count = st.slider("Adet", 3, 20, 5)
    if st.button("AI Sınav Oluştur", use_container_width=True, type="primary"):
        if topic:
            with st.spinner("AI Yanıtlıyor..."):
                st.session_state.quiz_content = ai_service.ask(f"{topic} hakkında {q_count} soruluk test hazırla.", temp=st.session_state.ai_temp, tokens=st.session_state.ai_tokens)
                st.session_state.current_quiz_title = topic
    if st.session_state.quiz_content:
        st.markdown('<div class="settings-card">', unsafe_allow_html=True); st.markdown(st.session_state.quiz_content)
        if st.button("Simülasyon Başlat (15 Öğrenci)", use_container_width=True):
            db_gen = get_db(); db = next(db_gen)
            names = ["Ahmet","Fatma","Can","Selin","Burak","Elif","Mehmet","Ayşe","Deniz","Zeynep","Emir","Melis","Okan","Gizem","Arda"]
            for n in names: add_quiz_result(db, st.session_state.current_quiz_title, n, random.randint(72,100))
            st.success("Sınav simüle edildi!"); st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Ders Materyalleri":
    st.title("Ders Arşivi"); db_gen = get_db(); db = next(db_gen); courses = get_all_courses(db)
    if courses:
        for c in courses: 
            with st.expander(c.title): st.markdown(f"**{c.description}**\n\n{c.content}")
    else:
        if st.button("15 Örnek Branşı Hemen Yükle", type="primary", use_container_width=True):
            demo = [("Matematik", "Kalkülüs", "Limit ve Türev..."), ("Fizik", "Newton", "Kuvvet Kanunları..."), ("Yazılım", "Python", "Giriş..."), ("AI", "Deep Learning", "Yapay Sinir Ağları..."), ("Kimya", "Periyodik Tablo", "Element Analizi...")]
            for t, d, c in demo: add_sample_course(db, t, d, c)
            st.rerun()

elif st.session_state.page == "Veri Analizi":
    st.title("Gelişmiş Analiz Paneli"); db_gen = get_db(); db = next(db_gen); quiz_res = get_quiz_results(db); courses = get_all_courses(db)
    t1, t2 = st.tabs(["Ders Başarı Göstergeleri", "Manuel Not Girişi"])
    with t1:
        if quiz_res:
            res_df = pd.DataFrame([{"Öğrenci": r.student_name, "Puan": r.score, "Ders": r.quiz_title} for r in quiz_res])
            m1, m2, m3 = st.columns(3); m1.metric("Ortalama", round(res_df["Puan"].mean(), 1)); m2.metric("En Yüksek", res_df["Puan"].max())
            last = res_df.iloc[0]; m3.metric("Son Girilen", f"{last['Puan']}", delta=f"{last['Öğrenci']} ({last['Ders']})")
            st.bar_chart(res_df.set_index("Öğrenci")["Puan"], color=accent); st.dataframe(res_df, use_container_width=True)
        else: 
            if st.button("15 Branş Simülasyonu Başlat", use_container_width=True, type="primary"):
                names = ["Ahmet","Fatma","Can","Selin","Burak","Elif","Mehmet","Ayşe","Deniz","Zeynep","Emir","Melis","Okan","Gizem","Arda"]
                subjects = ["Matematik", "AI", "Fizik", "Yazılım", "Kimya", "Tarih", "Müzik", "Sanat"]
                for i, n in enumerate(names): add_quiz_result(db, subjects[i % len(subjects)], n, random.randint(72,100))
                st.rerun()
    with t2:
        with st.form("man_entry"):
            name = st.text_input("Öğrenci"); quiz = st.text_input("Ders"); score = st.number_input("Puan", 0, 100, 85)
            if st.form_submit_button("Sonucu Kaydet"): 
                add_quiz_result(db, quiz, name, score); st.success("Kaydedildi!"); st.rerun()

elif st.session_state.page == "Ayarlar":
    st.title("Sistem Ayarları")
    st.markdown('<div class="settings-card"><h4>Görünüm & AI</h4>', unsafe_allow_html=True)
    st.session_state.ai_system = st.text_area("Yapay Zeka Rolü", value=st.session_state.ai_system)
    if st.button("Değişiklikleri Kaydet"):
        save_settings_to_disk({'ui_accent': st.session_state.ui_accent, 'ai_temp': st.session_state.ai_temp, 'ai_system': st.session_state.ai_system})
        st.success("Kaydedildi!"); st.rerun()
    st.divider()
    if st.button("Veritabanını Sıfırla (Fabrika Ayarları)"):
        db_gen = get_db(); db = next(db_gen); from sqlalchemy import delete; from models import Course, ChatHistory, QuizResult; db.execute(delete(Course)); db.execute(delete(ChatHistory)); db.execute(delete(QuizResult)); db.commit(); st.rerun()
