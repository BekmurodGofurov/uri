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

### 1. Gateway API va Ma'lumotlar bazasini ishga tushirish:
```bash
# Loyiha ildizida (root directory):
source .venv/bin/activate

# Baza jadvallarini yaratish (agar kerak bo'lsa):
python3 -c "from gateway.database.connection import init_db; init_db()"

# Gateway API serverini ishga tushirish:
DATABASE_URL=sqlite:///./uzum_reviews.db uvicorn gateway.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Dashboard UI ni ishga tushirish:
```bash
cd dashboard

# Bog'liqliklarni o'rnatish (agar o'rnatilmagan bo'lsa):
npm install

# Ishchi rejimda ishga tushirish:
npm run dev
```

Brauzerda ochish: `http://localhost:5173`

### 3. Production Build:
```bash
cd dashboard
npm run build
npm run preview
```
