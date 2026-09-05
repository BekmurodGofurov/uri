# Aspekt taksonomiyasi — `aspect-svc`

Bu hujjat 6 ta aspekt toifasini belgilaydi va har biri uchun aniq ta'rif + misollarni beradi.
`gold_set.jsonl`ni qo'lda belgilashda va LLM'ga prompt yozishda shu ta'riflarga tayaning —
ta'rif noaniq bo'lsa, o'zingiz bilan kelishmovchilik (kappa past chiqadi) kafolatlangan.

> **Eslatma:** bu qoralama (draft). 100 ta tasodifiy sharhni o'qib chiqqach (talabnoma, 1-vazifa),
> ta'riflarni real ma'lumotga moslab tahrirlang — bu 1-kun ichida qilinishi shart.

---

## 1. `delivery` — Yetkazib berish

**Ta'rif:** Buyurtmaning jismoniy yetkazib berilishi bilan bog'liq har qanday fikr:
tezlik, kechikish, kuryer xatti-harakati, yetkazib berish narxi (agar alohida aytilsa),
manzilga yetkazish aniqligi. Mahsulotning o'zi haqida emas — **jarayon** haqida.

**Ijobiy misollar:**
1. "Yetkazib berish juda tez bo'ldi, ertasi kuni keldi."
2. "Kuryer o'z vaqtida, xushmuomala yetkazib berdi."
3. "Buyurtma aynan belgilangan vaqtda yetib keldi."

**Salbiy misollar:**
1. "Yetkazib berish 2 hafta kechikdi."
2. "Kuryer manzilni topa olmay, mahsulot orqaga qaytarildi."
3. "Buyurtma boshqa shahar filialiga noto'g'ri yuborilgan."

---

## 2. `quality` — Sifat

**Ta'rif:** Mahsulotning o'zi haqida — ishlab chiqarilish sifati, mustahkamligi,
tavsiflangan xususiyatlarga mosligi, muddatidan oldin buzilishi.

**Ijobiy misollar:**
1. "Mahsulot juda mustahkam, hech qanday nuqson yo'q."
2. "Sifat rasmda ko'rsatilgandek, hatto yaxshiroq."
3. "Bir oydan beri ishlatyapman, hali ham a'lo holatda."

**Salbiy misollar:**
1. "Ikkinchi kunidayoq ishlamay qoldi."
2. "Material juda past sifatli, tez yirtilib ketdi."
3. "Rasmda ko'rsatilgan mahsulotdan butunlay farq qiladi."

---

## 3. `price` — Narx

**Ta'rif:** Narx/qiymat nisbati haqidagi har qanday fikr — qimmat, arzon, chegirma,
"pul-ga-yarasha" degan baholash. Yetkazib berish narxi emas (u — `delivery`).

**Ijobiy misollar:**
1. "Bu narxda juda yaxshi tanlov, tavsiya qilaman."
2. "Chegirma bilan olganim uchun juda mamnunman."
3. "Shu sifatga nisbatan narxi arzon."

**Salbiy misollar:**
1. "Narxi sifatiga mos emas, juda qimmat."
2. "Boshqa do'konlarda ancha arzonroq ekan."
3. "Chegirma tugagach narx ikki barobar oshib ketdi."

---

## 4. `seller` — Sotuvchi

**Ta'rif:** Sotuvchi/do'kon bilan bog'liq muloqot, xizmat ko'rsatish, kafolat/qaytarish
siyosati, javobgarlik. Platformaning o'zi (Uzum) emas — **muayyan sotuvchi**.

**Ijobiy misollar:**
1. "Sotuvchi savollarimga tezda javob berdi."
2. "Muammo bo'lganda sotuvchi darhol almashtirib berdi."
3. "Sotuvchi juda muloyim va yordamchi bo'ldi."

**Salbiy misollar:**
1. "Sotuvchi xabarlarga umuman javob bermayapti."
2. "Kafolat haqida gap bo'lganda sotuvchi javobgarlikdan qochdi."
3. "Shikoyat yozganimga bir hafta bo'ldi, hali ham javob yo'q."

---

## 5. `packaging` — Qadoqlash

**Ta'rif:** Jismoniy qadoq/quti holati — yetib kelgan paytdagi tashqi ko'rinishi,
qadoqning mahsulotni himoya qilgani yoki qilmagani. Kamdan-kam uchraydigan, lekin
muhim toifa — biznes buni ko'pincha alohida nazorat qilishni xohlaydi.

**Ijobiy misollar:**
1. "Qadoq juda mustahkam, hech narsa shikastlanmagan."
2. "Qutida qo'shimcha himoya materiali bor edi, yaxshi o'ylangan."
3. "Chiroyli qadoqlangan, sovg'a qilish uchun ham mos."

**Salbiy misollar:**
1. "Quti yorilib, mahsulot ezilib kelgan."
2. "Qadoqsiz, faqat paket ichida jo'natilgan."
3. "Quti namlangan, ichidagi mahsulotga ham ta'sir qilgan."

---

## 6. `other` — Boshqa

**Ta'rif:** Yuqoridagi 5 toifaning hech biriga aniq mos kelmaydigan, lekin baribir
mazmunli fikr bildirilgan holatlar (masalan: umumiy taassurot, ilova/interfeys haqida
fikr, mahsulotning umumiy tavsifi bilan bog'liq bo'lmagan izoh). Agar sharh hech qanday
aniq aspektga tegishli bo'lmasa yoki juda umumiy bo'lsa ("zo'r", "yoqmadi" — aniq nimasi
haqida emas), shu yerga tushadi.

**Ijobiy misollar:**
1. "Umuman olganda mamnunman."
2. "Ilova orqali buyurtma berish juda qulay."
3. "Zo'r, albatta yana buyurtma beraman."

**Salbiy misollar:**
1. "Umuman yoqmadi."
2. "Ilovada xatolik bo'lib, buyurtma ikki marta tushib ketdi."
3. "Umidsizlantirdi."

---

## Ko'p-yorliqlilik (multi-label) haqida eslatma

Bitta sharh bir nechta aspektga tegishli bo'lishi mumkin va **shart emas hammasi bir
xil polaritetda bo'lishi** — masalan: *"Yetkazib berish tez edi, lekin mahsulot sifati
pastroq chiqdi"* → `delivery: positive`, `quality: negative`.

## Kappa tekshiruvi (3-kun)

Agar `aspect_labeling_app.py`dagi "Qayta tekshirish rejimi"da o'z-o'zingizga nisbatan
kappa < 0.6 chiqsa, muammo odatda shu yerda: `other` bilan `quality`/`delivery` orasidagi
chegara noaniq bo'lib qoladi. Shunday holatda yuqoridagi ta'riflarni yanada aniqroq
qilib qayta yozing — bu modelning aybi emas, taksonomiyaning aybi.
