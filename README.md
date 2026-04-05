# LMS Yapay Zeka Final Projesi 🎓

Bu proje, modern bir Öğrenim Yönetim Sistemi (LMS) üzerine entegre edilmiş yapay zeka servislerini içermektedir. Google Gemini ve Groq (Llama 3) modellerini kullanarak öğrencilere ve eğitmenlere akıllı asistanlık sunar.

## 🚀 Özellikler
- **AI Sohbet:** Derslerle ilgili soruları yanıtlayan akıllı eğitmen asistanı.
- **Model Seçimi:** Gemini veya Groq (Llama 8B) modelleri arasında seçim yapabilme.
- **Ders Arşivi:** SQL tabanlı ders materyalleri yönetimi.
- **Modern Arayüz:** Streamlit ile geliştirilmiş kolay kullanımlı dashboard.
- **SQLite Entegrasyonu:** Tüm sohbet geçmişi ve ders verileri yerel veritabanında saklanır.

## 🛠 Proje Yapısı
```
lms-yapayzeka-final/
├── app.py              # Ana Uygulama (Streamlit Arayüzü)
├── ai_service.py       # LLM API Mantığı (Gemini & Groq Entegrasyonu)
├── database.py         # SQLite & Veritabanı İşlemleri
├── models.py           # Veri Modelleri ve Şemalar
├── requirements.txt    # Gerekli Kütüphaneler
├── .env                # API Anahtarları (Yerelde kullanım için)
└── README.md           # Proje Tanımı ve Kurulum Notları
```

## 📦 Kurulum
1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
2. `.env` dosyasını düzenleyerek API anahtarlarınızı ekleyin:
   - `GEMINI_API_KEY`: [Google AI Studio](https://aistudio.google.com/app/apikey)
   - `GROQ_API_KEY`: [Groq Console](https://console.groq.com/keys)

3. Uygulamayı başlatın:
   ```bash
   streamlit run app.py
   ```

## 💻 Kullanım
- Sol menüden **Ana Sayfa**'yı görüntüleyebilir, **AI Sohbet** ile konuşmaya başlayabilir veya **Ders Materyalleri** sekmesinden yeni dersler ekleyebilirsiniz.
- Sohbet geçmişi otomatik olarak kaydedilir.
- Ayarlar sekmesinden API durumlarını kontrol edebilirsiniz.

## 📝 Notlar
- Proje eğitim amaçlıdır ve modüler yapısı sayesinde kolayca geliştirilebilir.
- API anahtarlarınızı asla GitHub'a yüklemeyin (`.env` dosyası .gitignore'da olmalıdır).
