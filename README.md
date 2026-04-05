# LMS Yapay Zeka Final

Eğitim süreçlerini yapay zeka ile optimize eden, modern ve profesyonel bir Öğrenme Yönetim Sistemi (LMS). Bu platform, eğitimcilerin ve öğrencilerin ders içerikleri, sınav hazırlığı ve veri analizi süreçlerini tek bir merkezden yönetmelerini sağlar.

## 🚀 Öne Çıkan Özellikler

- **Akıllı Eğitmen Asistanı:** Gemini ve Groq (Llama 3.3) modelleri ile dersleriniz hakkında anlık etkileşime geçin.
- **Üretken Sınav Hazırlayıcı:** Belirlediğiniz herhangi bir konuda saniyeler içinde çoktan seçmeli sınavlar ve testler oluşturun.
- **Gelişmiş Ders Arşivi:** Ders materyallerini ekleyin, düzenleyin ve kategorize edilmiş bir şekilde listeleyin.
- **Profesyonel Raporlama:** Tüm ders içeriğini ve hazırlanan sınavları tek tıkla **PDF** veya **Excel** formatında dışa aktarın.
- **Eğitim Veri Analizi:** Öğrenci katılımı ve AI yanıt başarısı gibi metrikleri yapay zeka destekli grafiklerle takip edin.
- **Premium UI/UX:** Emojisiz, kurumsal, tema duyarlı (dark/light mode) ve modern bir kullanıcı arayüzü.

## 🛠 Teknik Altyapı

- **Front-end / Framework:** [Streamlit](https://streamlit.io/)
- **Veritabanı:** SQLite & [SQLAlchemy ORM](https://www.sqlalchemy.org/)
- **Yapay Zeka (LLM):** Google Gemini API & Groq API
- **Raporlama:** fpdf2 (PDF) & Pandas/OpenPyXL (Excel)
- **Tasarım:** Custom CSS (Glassmorphism & Modern Typography)

## 📦 Kurulum ve Kullanım

### Yerel Çalıştırma

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/cemevecen/lms-yapayzeka-final.git
   cd lms-yapayzeka-final
   ```

2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. `.env` dosyasını oluşturun ve API anahtarlarınızı ekleyin:
   ```env
   GEMINI_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key
   ```

4. Uygulamayı başlatın:
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. Projeyi GitHub'a yükleyin.
2. [Streamlit Cloud](https://share.streamlit.io/) sitesine gidin ve projenizi bağlayın.
3. **Advanced Settings > Secrets** kısmına API anahtarlarınızı ekleyin.

## 🛡 Veri Yönetimi

Uygulamanın **Ayarlar** sekmesinden tüm veritabanını tek tıkla sıfırlayabilir veya platformu test etmek için **"Temiz Örnek Veri"** yüklemesi yapabilirsiniz.

---
**Versiyon:** v1.0.1  
**Durum:** Kararlı (Stable)  
**Tasarım Dili:** Kurumsal / Emoji-Free
