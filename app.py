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

# --- INITIALIZE SETTINGS ---
if 'ui_accent' not in st.session_state: st.session_state.ui_accent = "#1f77b4" # Default Blue
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
    .status-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight:600; margin-left: 10px; }}
    .status-active {{ background: #2ecc71; color: white; }}
    .status-passive {{ background: #e74c3c; color: white; }}
    .stButton>button {{ border-radius: 10px; font-weight: 600; transition: all 0.2s ease; border: 1px solid {accent}; }}
    .stButton>button:hover {{ background: {accent}; color: white; }}
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
    # Page Numbers logic
    if st.session_state.pdf_pagenums:
        pdf.set_y(-15); pdf.set_font("helvetica", size=8); pdf.cell(0, 10, f'Sayfa {pdf.page_no()}', 0, 0, 'C'); pdf.set_y(30)
    pdf.set_font("helvetica", size=11)
    pdf.multi_cell(0, 10, txt=tr_fix(content))
    return pdf.output()

# --- PAGE: HOME ---
if st.session_state.page == "Ana Sayfa":
    st.markdown(f'<div style="text-align:center; padding:20px 0;"><h1 style="font-size:3rem; margin-bottom:0; color:{accent};">LMS Yapay Zeka Final</h1><p style="font-size:1.2rem; opacity:0.8;">Premium AI Destekli Eğitim Deneyimi</p></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('<div class="stat-card"><div class="stat-value">12</div><div class="stat-label">Ders Sayısı</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="stat-card"><div class="stat-value">156</div><div class="stat-label">Öğrenci</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="stat-card"><div class="stat-value">4.8</div><div class="stat-label">Puan</div></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="stat-card"><div class="stat-value">850+</div><div class="stat-label">AI Yanıtı</div></div>', unsafe_allow_html=True)
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
    st.caption(f"Aktif Parametreler: Yaratıcılık: {st.session_state.ai_temp} | Max Tokens: {st.session_state.ai_tokens}")
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
            with st.spinner("Özelleştirilmiş sorular hazırlanıyor..."):
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
            c1, c2 = st.columns(2)
            with c1: 
                excel_df = pd.DataFrame([{"Baslik": c.title, "Aciklama": c.description, "Icerik": c.content} for c in courses])
                output = io.BytesIO(); 
                with pd.ExcelWriter(output, engine='openpyxl') as writer: excel_df.to_excel(writer, index=False)
                st.download_button("Excel İndir", output.getvalue(), "dersler.xlsx", use_container_width=True)
            with c2: 
                raw = "\n\n".join([f"**{c.title}**\n{c.description}\n{c.content}" for c in courses])
                st.download_button("PDF İndir", bytes(export_pdf(raw, title="Ders Arşivi")), "dersler.pdf", use_container_width=True, key="c_pdf")
            st.markdown('</div>', unsafe_allow_html=True)
            for c in courses:
                col1, col2 = st.columns([0.92, 0.08])
                with col1: 
                    with st.expander(c.title, expanded=st.session_state.course_expanded): st.write(c.content)
                with col2:
                    if st.button("Sil", key=f"del_{c.id}", type="primary"): delete_course(db, c.id); st.rerun()

# --- PAGE: VERI ANALIZI ---
elif st.session_state.page == "Veri Analizi":
    st.title("Performans Takibi"); st.bar_chart(pd.DataFrame({'Ders': ['Mat', 'Cog', 'Res', 'Edb'], 'Puan': [85, 72, 95, 68]}))

# --- PAGE: SETTINGS ---
elif st.session_state.page == "Ayarlar":
    st.title("Gelişmiş Ayarlar Panel")
    
    # Category 1: AI Rules
    st.markdown('<div class="settings-card"><h4>AI Model Parametreleri</h4>', unsafe_allow_html=True)
    st.session_state.ai_temp = st.slider("Temperature (Yaratıcılık): Düşük değerler daha gerçekçi, yüksek değerler daha yaratıcı yanıtlar üretir.", 0.0, 1.0, st.session_state.ai_temp, 0.1)
    st.session_state.ai_tokens = st.select_slider("Maksimum Yanıt Uzunluğu (Tokens)", options=[256, 512, 1024, 2048, 4096], value=st.session_state.ai_tokens)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Category 2: UI Appearance
    st.markdown('<div class="settings-card"><h4>Arayüz ve Görünüm Ayarları</h4>', unsafe_allow_html=True)
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        color_map = {"Kurumsal Mavi": "#1f77b4", "Doğa Yeşil": "#2ecc71", "Modern Mor": "#9b59b6", "Canlı Turuncu": "#e67e22"}
        selected_color_name = st.selectbox("Vurgu Rengi Seçin", list(color_map.keys()), index=list(color_map.values()).index(st.session_state.ui_accent))
        if color_map[selected_color_name] != st.session_state.ui_accent:
            st.session_state.ui_accent = color_map[selected_color_name]; st.rerun()
    with c_col2:
        st.info("Karanlık/Aydınlık mod tarayıcı ayarlarınıza göre otomatik optimize edilir.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Category 3: Usage Preferences
    st.markdown('<div class="settings-card"><h4>Kullanım Tercihleri</h4>', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.session_state.default_model = st.selectbox("Varsayılan AI Modeli", ["Groq", "Gemini"], index=0 if st.session_state.default_model=="Groq" else 1)
    with p_col2:
        st.session_state.course_expanded = st.toggle("Dersleri Listede Genişletilmiş Göster", value=st.session_state.course_expanded)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Category 4: Report Settings
    st.markdown('<div class="settings-card"><h4>Raporlama Tercihleri</h4>', unsafe_allow_html=True)
    st.session_state.pdf_pagenums = st.toggle("PDF Dışa Aktarımlarında Sayfa Numarası Göster", value=st.session_state.pdf_pagenums)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Category 5: Data Management
    st.markdown('<div class="settings-card"><h4>Veri ve Sistem Yönetimi</h4>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        if st.button("Tüm Verileri Temizle", type="primary", use_container_width=True):
            db_gen = get_db(); db = next(db_gen); from sqlalchemy import delete; from models import Course, ChatHistory; db.execute(delete(Course)); db.execute(delete(ChatHistory)); db.commit(); st.rerun()
    with d2:
        if st.button("Örnek Veri Yükle", use_container_width=True):
            db_gen = get_db(); db = next(db_gen); sc = [{"title": "Cografya: Iklim", "desc": "...", "content": "Dünya iklimleri..."}, {"title": "Matematik: Turev", "desc": "...", "content": "Turev kurallari..."}]
            for c in sc: add_sample_course(db, c["title"], c["desc"], c["content"]); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
