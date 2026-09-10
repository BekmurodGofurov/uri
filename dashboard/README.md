# Uzum Review Intelligence (URI) — Dashboard UI

O'zbek tili sharhlari uchun sentiment tahlili va jihatlar (aspect extraction) bo'yicha tahliliy dashboard.
FastAPI Gateway API (`gateway/api/app.py`) bilan integratsiya qilingan.

---

## Imkoniyatlar (Features)

1. **Mahsulotlar katalogi (Product List):**
   - Har bir tovarning o'rtacha reytingi (1.0 - 5.0).
   - Sharhlar soni va dinamikasi.
   - Ijobiy, neytral va salbiy kayfiyat nisbati progress bar orqali.
   - Qidiruv (nomi yoki ID bo'yicha), toifalar bo'yicha filtrlash va saralash.

2. **Dinamik grafiklar (Sentiment Over Time):**
   - Vaqt bo'yicha mijozlar kayfiyati dinamikasi (Recharts interactive area chart).
   - Sanalar kesimida ijobiy, neytral va salbiy sharhlar soni.

3. **Jihatlar tahlili (Aspect Breakdown):**
   - **Sifat (Quality)**
   - **Yetkazib berish (Delivery)**
   - **Narx (Price)**
   - **Sotuvchi (Seller)**
   - **Qadoqlash (Packaging)**
   - Har bir jihat bo'yicha foizlar va qoniqish darajasi.

4. **Sharhlar drill-down:**
   - Haqiqiy xaridor sharhlari matni.
   - Yulduzchali baholar va sanalar.
   - AI tomonidan chiqarilgan kayfiyat va ishonchlilik foizi (`sentiment_confidence`).
   - Aniqlangan jihatlar teglari.

5. **Majburiy talab — Model Versiyasi (`model_version`):**
   - Sahifa yuqori panelida faol model versiyasi barchaga ko'rinib turadi.
   - Tanlangan mahsulot sarlavhasida ushbu tovar sharhlarini tahlil qilgan barcha model versiyalari ko'rsatiladi.
   - **Har bir sharh kartochkasida** aynan qaysi model versiyasi ushbu xulosani bergani alohida nishon (badge) bilan aniq ko'rsatiladi.

6. **Jonli AI Tahlil (Live Scorer Modal):**
   - Istalgan yangi o'zbekcha sharhni yozib, Gateway API (`POST /api/score/preview`) orqali test qilish va real vaqtda natija olish imkoniyati.

---

## Ishga tushirish (Getting Started)

### 1. Backend Xizmatlarni ishga tushirish (Docker orqali):
Backend mikroxizmatlari (`postgres`, `sentiment-svc`, `aspect-svc`, `gateway`) Docker orqali ishga tushiriladi:
```bash
# Loyiha ildizida (root directory):
docker compose up -d
```
Backend Gateway `http://localhost:8000` manzilida ishlaydi.

---

### 2. Dashboard Muhit Sozlamasi (.env - Majburiy):
Dashboard barcha API so'rovlarini faqat `.env` faylida ko'rsatilgan `VITE_API_URL` manziliga yuboradi.

`dashboard/.env` faylini yarating yoki mavjudligini tekshiring:
```bash
cd dashboard
cp .env.example .env
```

`dashboard/.env` ichida:
```env
# Backend Gateway API manzili (majburiy)
VITE_API_URL=http://localhost:8000
```
> **Muhim:** Agar `VITE_API_URL` ko'rsatilmasa, ilova xatolik beradi va API ga ulanmaydi.

---

### 3. Qo'lda Build qilish va Ishga tushirish:

Dashboard Docker orqali emas, faqat qo'lda build va run qilinadi:

#### A) Ishchi rejimda (Development - Hot Reload):
```bash
cd dashboard
npm install       # Faqat birinchi marta
npm run dev       # Veb serverni ishga tushirish (port 3000)
```
Brauzerda ochish: [http://localhost:3000](http://localhost:3000)

#### B) Ishlab chiqarish rejimida (Production Build & Run):
```bash
cd dashboard
npm run build     # TypeScript va Vite orqali dist/ papkasiga yig'ish
npm run preview   # Yig'ilgan production versiyani ishga tushirish (port 3000)
```
Brauzerda ochish: [http://localhost:3000](http://localhost:3000)

