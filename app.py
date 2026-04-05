import streamlit as st
import pandas as pd
from database import init_db, get_db, add_chat_message, get_chat_history, add_sample_course, get_all_courses, delete_course
from ai_service import ai_service
import os
import io
from datetime import datetime
from fpdf import FPDF

# Page Configuration
st.set_page_config(
    page_title="LMS Yapay Zeka Final",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State for Navigation
if 'page' not in st.session_state:
    st.session_state.page = "Ana Sayfa"

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# Initialize Database
init_db()

# Custom CSS for Premium & Theme-Aware Look
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

# Sidebar Navigation
pages = ["Ana Sayfa", "AI Sohbet", "Ders Materyalleri", "Veri Analizi", "Ayarlar"]
with st.sidebar:
    st.title("AI-LMS Dashboard")
    st.divider()
    
    # Calculate index based on session state
    current_index = pages.index(st.session_state.page)
    selected_page = st.radio(
        "Navigasyon", 
        pages, 
        index=current_index
    )
    
    # Update session state if radio is clicked
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()
    
    st.divider()

# --- HELPERS ---
def export_excel(courses):
    df = pd.DataFrame([{"Baslik": c.title, "Aciklama": c.description, "Icerik": c.content} for c in courses])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def export_pdf(courses):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=16)
    header_text = "Ders Katalogu Raporu".encode('cp1254', 'ignore').decode('latin-1')
    pdf.cell(200, 10, txt=header_text, ln=True, align='C')
    pdf.ln(10)
    for c in courses:
        pdf.set_font("helvetica", style='B', size=12)
        title_text = f"Ders: {c.title}".encode('cp1254', 'ignore').decode('latin-1')
        pdf.cell(200, 10, txt=title_text, ln=True)
        pdf.set_font("helvetica", size=10)
        content_text = f"Icerik:\n{c.content}".encode('cp1254', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, txt=content_text)
        pdf.ln(10)
        pdf.cell(200, 0, ln=True, border='T')
        pdf.ln(5)
    return pdf.output()

# --- PAGE: HOME ---
if st.session_state.page == "Ana Sayfa":
    st.markdown('<div style="text-align: center; padding: 20px 0;"><h1 style="font-size: 3rem; margin-bottom: 0;">LMS Yapay Zeka Final</h1><p style="font-size: 1.2rem; opacity: 0.8;">Eğitimde Yeni Nesil Yapay Zeka Deneyimi</p></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown('<div class="stat-card"><div class="stat-value">12</div><div class="stat-label">Toplam Ders</div></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="stat-card"><div class="stat-value">156</div><div class="stat-label">Öğrenci Sayısı</div></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="stat-card"><div class="stat-value">4.8</div><div class="stat-label">Ortalama Puan</div></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="stat-card"><div class="stat-value">850+</div><div class="stat-label">AI Yanıtı</div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### Platform Özellikleri")
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        st.markdown('<div class="feature-card"><h4>Akıllı Sohbet</h4><p style="font-size:0.9rem; opacity:0.8;">Gemini ve Groq ile anlık soru-cevap asistanlığı.</p></div>', unsafe_allow_html=True)
        if st.button("Sohbete Basla", use_container_width=True, key="btn_chat"): navigate_to("AI Sohbet")
    with fcol2:
        st.markdown('<div class="feature-card"><h4>İçerik Üretimi</h4><p style="font-size:0.9rem; opacity:0.8;">Ders materyallerini yönetin ve AI ile içerik oluşturun.</p></div>', unsafe_allow_html=True)
        if st.button("Derslere Git", use_container_width=True, key="btn_courses"): navigate_to("Ders Materyalleri")
    with fcol3:
        st.markdown('<div class="feature-card"><h4>Veri Analizi</h4><p style="font-size:0.9rem; opacity:0.8;">Eğitim performansınızı grafiklerle takip edin.</p></div>', unsafe_allow_html=True)
        if st.button("Analizi Gor", use_container_width=True, key="btn_analysis"): navigate_to("Veri Analizi")

# --- PAGE: AI CHAT ---
elif st.session_state.page == "AI Sohbet":
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("AI Egitmen Asistani")
        st.caption("Yapay zeka modelleri ile dersleriniz hakkinda etkilesime gecin.")
    with col2:
        if st.button("Gecmisi Temizle", use_container_width=True):
            db_gen = get_db(); db = next(db_gen)
            from sqlalchemy import delete; from models import ChatHistory
            db.execute(delete(ChatHistory)); db.commit(); st.rerun()
    st.markdown('<div style="background:var(--secondary-background-color); padding:15px; border-radius:12px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between;">', unsafe_allow_html=True)
    use_groq = st.toggle("Groq Modelini Kullan (Kapaliyken Gemini)", value=True)
    ai_provider = "Groq" if use_groq else "Gemini"
    st.markdown(f'<span style="font-weight:600; color:#1f77b4;">Aktif Model: {ai_provider}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    db_gen = get_db(); db = next(db_gen)
    history = get_chat_history(db)
    chat_history = history[-20:] if len(history) > 20 else history
    for chat in chat_history:
        with st.chat_message(chat.role):
            st.markdown(chat.message)
            st.markdown(f'<p style="font-size:0.7rem; opacity:0.5; margin:0;">{chat.model_name} | {chat.timestamp.strftime("%H:%M")}</p>', unsafe_allow_html=True)
    if prompt := st.chat_input("Dersinle ilgili ne ogrenmek istersin?"):
        with st.chat_message("user"): st.markdown(prompt)
        add_chat_message(db, "user", prompt, ai_provider)
        with st.chat_message("assistant"):
            with st.spinner(f"{ai_provider} yanitliyor..."):
                try:
                    response = ai_service.ask(prompt, provider=ai_provider.lower())
                    st.markdown(response); add_chat_message(db, "assistant", response, ai_provider)
                except Exception as e: st.error(f"Hata olustu: {str(e)}")

# --- PAGE: COURSES ---
elif st.session_state.page == "Ders Materyalleri":
    st.title("Ders Arşivi")
    st.caption("Yüklü dersleri görüntüleyin, yeni dersler ekleyin veya dışa aktarın.")
    db_gen = get_db(); db = next(db_gen)
    tab1, tab2 = st.tabs(["Mevcut Dersler", "Yeni Ders Ekle"])
    with tab1:
        courses = get_all_courses(db)
        if not courses:
            st.warning("Henüz kayıtlı ders bulunmamaktadır.")
        else:
            st.markdown('<div class="settings-card" style="padding:15px; margin-bottom:20px;">', unsafe_allow_html=True)
            st.write("**Dersleri Disa Aktar (Export)**")
            ecol1, ecol2 = st.columns(2)
            with ecol1:
                excel_data = export_excel(courses)
                st.download_button(label="Excel Olarak Indir", data=excel_data, file_name=f"dersler_{datetime.now().strftime('%d%m%y')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with ecol2:
                try:
                    pdf_data = bytes(export_pdf(courses))
                    st.download_button(label="PDF Olarak Indir", data=pdf_data, file_name=f"dersler_{datetime.now().strftime('%d%m%y')}.pdf", mime="application/pdf", key="pdf_dl", use_container_width=True)
                except Exception as e:
                    st.error(f"PDF Olusturma Hatasi: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            for course in courses:
                col_exp, col_del = st.columns([0.85, 0.15])
                with col_exp:
                    with st.expander(f"{course.title}"):
                        st.write(f"**Açıklama:** {course.description}"); st.divider(); st.write(course.content)
                with col_del:
                    if st.button("Sil", key=f"del_{course.id}", type="primary", use_container_width=True):
                        delete_course(db, course.id); st.rerun()

# --- PAGE: VERI ANALIZI ---
elif st.session_state.page == "Veri Analizi":
    st.title("Egitim Veri Analizi"); st.caption("Performans grafikleri ve istatistikler.")
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("Ogrenci Katilim Oranlari")
    chart_data = pd.DataFrame({'Ders': ['Matematik', 'Cografya', 'Resim', 'Edebiyat', 'Kimya', 'Muzik'], 'Katilim': [85, 72, 95, 68, 80, 92]})
    st.bar_chart(data=chart_data, x='Ders', y='Katilim')
    st.markdown('</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.subheader("AI Yanit Basarisi"); st.progress(0.92, text="92% Memnuniyet")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.subheader("İcerik Cukitisi"); st.progress(0.75, text="75% Materyal Uyumlulugu")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: SETTINGS ---
elif st.session_state.page == "Ayarlar":
    st.title("Sistem Yonetimi")
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("API Yapilandirmasi")
    gk = os.getenv("GEMINI_API_KEY"); grk = os.getenv("GROQ_API_KEY")
    ac1, ac2 = st.columns(2)
    with ac1:
        css = "status-active" if gk else "status-passive"; txt = "AKTIF" if gk else "PASIF"
        st.markdown(f'<div style="display:flex; align-items:center; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.05); border-radius:10px;"><span>Gemini API</span><span class="status-badge {css}">{txt}</span></div>', unsafe_allow_html=True)
    with ac2:
        css = "status-active" if grk else "status-passive"; txt = "AKTIF" if grk else "PASIF"
        st.markdown(f'<div style="display:flex; align-items:center; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.05); border-radius:10px;"><span>Groq API</span><span class="status-badge {css}">{txt}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("Veri Yonetimi"); dcol1, dcol2 = st.columns(2)
    with dcol1:
        if st.button("Veritabanini Sifirla", type="primary", use_container_width=True, key="reset_btn"):
            db_gen = get_db(); db = next(db_gen)
            from sqlalchemy import delete; from models import Course, ChatHistory
            db.execute(delete(Course)); db.execute(delete(ChatHistory)); db.commit(); st.rerun()
    with dcol2:
        if st.button("Ornek Veri Yukle", use_container_width=True, key="sample_btn"):
            db_gen = get_db(); db = next(db_gen)
            sc = [{"title": "Cografya", "desc": "Dogal kaynaklar.", "content": "Iklim ve eko-sistemler."}, {"title": "Matematik", "desc": "Kalkulus.", "content": "Turev ve integral."}]
            for c in sc: add_sample_course(db, c["title"], c["desc"], c["content"])
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("Sistem Bilgisi")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Versiyon", "v1.0.0"); sc2.metric("Durum", "Kararli"); sc3.metric("Guncelleme", datetime.now().strftime("%d/%m/%Y"))
    st.markdown('</div>', unsafe_allow_html=True)
