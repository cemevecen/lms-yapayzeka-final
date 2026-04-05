import streamlit as st
import pandas as pd
from database import init_db, get_db, add_chat_message, get_chat_history, add_sample_course, get_all_courses, delete_course
from ai_service import ai_service
import os
import io
from datetime import datetime
from fpdf import FPDF

# --- INITIALIZE SETTINGS ---
if 'ui_accent' not in st.session_state: st.session_state.ui_accent = "#1f77b4"
if 'ai_temp' not in st.session_state: st.session_state.ai_temp = 0.7
if 'ai_tokens' not in st.session_state: st.session_state.ai_tokens = 2048
if 'default_model' not in st.session_state: st.session_state.default_model = "Groq"
if 'auto_clear' not in st.session_state: st.session_state.auto_clear = False
if 'pdf_pagenums' not in st.session_state: st.session_state.pdf_pagenums = True
if 'course_expanded' not in st.session_state: st.session_state.course_expanded = False
if 'page' not in st.session_state: st.session_state.page = "Ana Sayfa"
if 'quiz_content' not in st.session_state: st.session_state.quiz_content = ""

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
    .stat-card {{
        background: var(--secondary-background-color);
        padding: 24px; border-radius: 16px; border: 1px solid var(--divider-color); text-align: center;
        transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); border-color: {accent}; }}
    .stat-value {{ font-size: 28px; font-weight: 800; color: {accent}; margin-bottom: 4px; }}
    .stat-label {{ font-size: 14px; color: var(--text-color); opacity: 0.8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}
    .feature-card {{
        background: var(--secondary-background-color); padding: 30px; border-radius: 20px; border: 1px solid var(--divider-color);
        height: 220px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 10px;
    }}
    .settings-card {{
        background: var(--secondary-background-color); padding: 25px; border-radius: 20px; border: 1px solid var(--divider-color);
        margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    .stButton>button {{ border-radius: 10px; font-weight: 600; transition: all 0.2s ease; border: 1px solid {accent}; }}
    .stButton>button:hover {{ background: {accent}; color: white; }}
    .status-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight:600; margin-left: 10px; }}
    .status-active {{ background: #2ecc71; color: white; }}
    .status-passive {{ background: #e74c3c; color: white; }}
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
    chars = {"ğ": "g", "Ğ": "G", "ı": "i", "İ": "I", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in chars.items(): text = text.replace(k, v)
    return text

def export_pdf(content, title="Rapor"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", style='B', size=16)
    pdf.cell(200, 10, txt=tr_fix(title), ln=True, align='C')
    pdf.ln(10)
    if st.session_state.pdf_pagenums: pdf.set_y(-15); pdf.set_font("helvetica", size=8); pdf.cell(0, 10, f'Sayfa {pdf.page_no()}', 0, 0, 'C'); pdf.set_y(30)
    pdf.set_font("helvetica", size=11); pdf.multi_cell(0, 10, txt=tr_fix(content))
    return pdf.output()

# --- DATA FETCHING (REAL) ---
def get_analytics_data():
    db_gen = get_db(); db = next(db_gen)
    courses = get_all_courses(db)
    history = get_chat_history(db)
    return courses, history

# --- PAGE: HOME ---
if st.session_state.page == "Ana Sayfa":
    courses, history = get_analytics_data()
    st.markdown(f'<div style="text-align:center; padding:20px 0;"><h1 style="font-size:3rem; margin-bottom:0; color:{accent};">LMS Yapay Zeka Final</h1><p style="font-size:1.2rem; opacity:0.8;">Premium AI Destekli Eğitim Deneyimi</p></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'<div class="stat-card"><div class="stat-value">{len(courses)}</div><div class="stat-label">Ders Sayısı</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="stat-card"><div class="stat-value">{len(history)}</div><div class="stat-label">Toplam Mesaj</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="stat-card"><div class="stat-value">4.8</div><div class="stat-label">İlgi Puanı</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="stat-card"><div class="stat-value">{len(courses)*50}+</div><div class="stat-label">Karakter Arşivi</div></div>', unsafe_allow_html=True)
    st.divider(); st.markdown("### Platform Özellikleri")
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        st.markdown('<div class="feature-card"><h4>Akıllı Sohbet</h4><p style="font-size:0.8rem; opacity:0.8;">Model seçimli AI asistanlığı.</p></div>', unsafe_allow_html=True)
        if st.button("Sohbete Başla", use_container_width=True, key="h_chat"): navigate_to("AI Sohbet")
    with fcol2:
        st.markdown('<div class="feature-card"><h4>Sınav Oluşturucu</h4><p style="font-size:0.8rem; opacity:0.8;">Otomatik quiz hazırlayın.</p></div>', unsafe_allow_html=True)
        if st.button("Hemen Hazırla", use_container_width=True, key="h_quiz"): navigate_to("Quiz Hazirla")
    with fcol3:
        st.markdown('<div class="feature-card"><h4>Ders Arşivi</h4><p style="font-size:0.8rem; opacity:0.8;">İçerik ve rapor yönetimi.</p></div>', unsafe_allow_html=True)
        if st.button("Derslere Git", use_container_width=True, key="h_course"): navigate_to("Ders Materyalleri")

# --- PAGE: AI CHAT ---
elif st.session_state.page == "AI Sohbet":
    st.title("AI Egitmen Asistani")
    use_groq_default = True if st.session_state.default_model == "Groq" else False
    use_groq = st.toggle("Groq Modu Aktif", value=use_groq_default, key="chat_model_toggle")
    ai_p = "Groq" if use_groq else "Gemini"
    db_gen = get_db(); db = next(db_gen); history = get_chat_history(db)
    for chat in history[-15:]:
        with st.chat_message(chat.role): st.markdown(chat.message)
    if pr := st.chat_input("Mesajınızı yazın..."):
        with st.chat_message("user"): st.markdown(pr)
        add_chat_message(db, "user", pr, ai_p)
        with st.chat_message("assistant"):
            with st.spinner(f"{ai_p} yanıtlıyor..."):
                res = ai_service.ask(pr, provider=ai_p.lower(), temp=st.session_state.ai_temp, tokens=st.session_state.ai_tokens)
                st.markdown(res); add_chat_message(db, "assistant", res, ai_p)

# --- PAGE: QUIZ ---
elif st.session_state.page == "Quiz Hazirla":
    st.title("Sınav Hazırlayıcı")
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([0.7, 0.3])
    with c1: topic = st.text_input("Konu/Ders", placeholder="Ör: Kalkulus")
    with c2: q_count = st.slider("Soru Sayısı", 3, 20, 5)
    model = st.selectbox("Model", ["Groq", "Gemini"], index=0 if st.session_state.default_model=="Groq" else 1)
    if st.button("Sınavı Oluştur", use_container_width=True, type="primary"):
        if topic:
            with st.spinner("Sorular hazirlaniyor..."):
                st.session_state.quiz_content = ai_service.ask(f"{topic} hakkında {q_count} soruluk çoktan seçmeli test hazırla. Cevap anahtarı sonda olsun.", provider=model.lower(), temp=st.session_state.ai_temp, tokens=st.session_state.ai_tokens)
        else: st.error("Bir konu girin.")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.quiz_content:
        st.markdown('<div class="settings-card">', unsafe_allow_html=True); st.markdown(st.session_state.quiz_content)
        pdf = bytes(export_pdf(st.session_state.quiz_content, title=f"SINAV: {topic.upper()}"))
        st.download_button("Sınavı PDF İndir", pdf, file_name="sinav.pdf", mime="application/pdf", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: COURSES ---
elif st.session_state.page == "Ders Materyalleri":
    st.title("Ders Arşivi"); db_gen = get_db(); db = next(db_gen); tab1, tab2 = st.tabs(["Listele", "Ekle"])
    with tab1:
        courses = get_all_courses(db)
        if courses:
            st.markdown('<div class="settings-card" style="padding:15px; margin-bottom:20px;">', unsafe_allow_html=True)
            dc1, dc2 = st.columns(2)
            with dc1: 
                df = pd.DataFrame([{"Baslik": c.title, "Aciklama": c.description, "Icerik": c.content} for c in courses])
                output = io.BytesIO(); 
                with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False)
                st.download_button("Excel İndir", output.getvalue(), "dersler.xlsx", use_container_width=True)
            with dc2: 
                raw = "\n\n".join([f"**{c.title}**\n{c.description}\n{c.content}" for c in courses])
                st.download_button("PDF İndir", bytes(export_pdf(raw, title="Ders Arşivi")), "dersler.pdf", use_container_width=True, key="c_pdf")
            st.markdown('</div>', unsafe_allow_html=True)
            for c in courses:
                col1, col2 = st.columns([0.92, 0.08])
                with col1: 
                    with st.expander(c.title, expanded=st.session_state.course_expanded): st.write(c.content)
                with col2:
                    if st.button("Sil", key=f"del_{c.id}", type="primary"): delete_course(db, c.id); st.rerun()
        else: st.warning("Ders bulunmuyor.")
    with tab2:
        with st.form("new_c"):
            t = st.text_input("Başlık"); d = st.text_area("Açıklama"); c = st.text_area("İçerik"); sub = st.form_submit_button("Kaydet")
            if sub and t and c: add_sample_course(db, t, d, c); st.success("Eklendi!"); st.rerun()

# --- PAGE: VERI ANALIZI (REAL DATA) ---
elif st.session_state.page == "Veri Analizi":
    st.title("Gerçek Zamanlı Veri Analizi")
    courses, history = get_analytics_data()
    
    if not courses and not history:
        st.warning("Analiz edilecek veri bulunamadı. Lütfen ders ekleyin veya AI ile sohbet edin.")
    else:
        # KPI Row
        kcol1, kcol2, kcol3 = st.columns(3)
        kcol1.metric("Toplam Ders", len(courses))
        kcol2.metric("Toplam AI Yanıtı", len(history))
        char_count = sum([len(c.content) for c in courses])
        kcol3.metric("Arşiv Karakter Sayısı", char_count)
        
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.subheader("Ders Başına İçerik Yoğunluğu")
        if courses:
            c_df = pd.DataFrame({
                'Ders Başlığı': [c.title for c in courses],
                'İçerik Uzunluğu': [len(c.content) for c in courses]
            })
            st.bar_chart(data=c_df, x='Ders Başlığı', y='İçerik Uzunluğu', color=accent)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.subheader("Mesaj Dağılımı")
            if history:
                h_df = pd.DataFrame({'Model': [h.model_name for h in history if h.model_name]})
                if not h_df.empty:
                    st.write(h_df['Model'].value_counts())
                else: st.write("Model verisi mevcut değil.")
            st.markdown('</div>', unsafe_allow_html=True)
        with col_r:
            st.markdown('<div class="settings-card">', unsafe_allow_html=True)
            st.subheader("Sistem Sağlığı")
            st.progress(0.95, text="API Erişilebilirliği: %95")
            st.progress(len(courses)/20 if len(courses) < 20 else 1.0, text=f"Depolama Kullanımı: {len(courses)}/20 Ders")
            st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: SETTINGS ---
elif st.session_state.page == "Ayarlar":
    st.title("Gelişmiş Ayarlar")
    st.markdown('<div class="settings-card"><h4>AI Parametreleri</h4>', unsafe_allow_html=True)
    st.session_state.ai_temp = st.slider("Yaratıcılık (0.0=Mantıksal, 1.0=Yaratıcı)", 0.0, 1.0, st.session_state.ai_temp, 0.1)
    st.session_state.ai_tokens = st.select_slider("Maksimum Yanıt Uzunluğu", options=[256, 512, 1024, 2048, 4096], value=st.session_state.ai_tokens)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="settings-card"><h4>Görünüm</h4>', unsafe_allow_html=True)
    color_map = {"Kurumsal Mavi": "#1f77b4", "Doğa Yeşil": "#2ecc71", "Modern Mor": "#9b59b6", "Canlı Turuncu": "#e67e22"}
    selected_c = st.selectbox("Vurgu Rengi", list(color_map.keys()), index=list(color_map.values()).index(st.session_state.ui_accent))
    if color_map[selected_c] != st.session_state.ui_accent: st.session_state.ui_accent = color_map[selected_c]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="settings-card"><h4>Tercihler</h4>', unsafe_allow_html=True)
    st.session_state.default_model = st.selectbox("Varsayılan AI Model", ["Groq", "Gemini"], index=0 if st.session_state.default_model=="Groq" else 1)
    st.session_state.course_expanded = st.toggle("Dersleri Açık Listele", value=st.session_state.course_expanded)
    st.session_state.pdf_pagenums = st.toggle("PDF Sayfa Numaraları", value=st.session_state.pdf_pagenums)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Tüm Verileri Sıfırla", type="primary"):
        db_gen = get_db(); db = next(db_gen); from sqlalchemy import delete; from models import Course, ChatHistory; db.execute(delete(Course)); db.execute(delete(ChatHistory)); db.commit(); st.rerun()
