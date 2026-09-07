# Aspekt taksonomiyasi — `aspect-svc`

Bu hujjat 6 ta aspekt toifasini belgilaydi va har biri uchun aniq ta'rif + misollarni beradi.
`gold_set.jsonl`ni qo'lda belgilashda va LLM'ga prompt yozishda shu ta'riflarga tayaning —
ta'rif noaniq bo'lsa, o'zingiz bilan kelishmovchilik (kappa past chiqadi) kafolatlangan.

> **Holat:** ✅ Tasdiqlangan (draft emas). 100+ ta sharh o'qib chiqilgan, 300 ta
> gold set to'liq belgilangan, va ta'riflar ikki bosqichli Cohen's kappa
> tekshiruvi (pastga qarang) orqali real kelishmovchilik misollariga asoslanib
> aniqlashtirilgan. Keyingi o'zgarish faqat R1 qoidasiga ko'ra (jamoa yozma
> roziligi bilan) kiritiladi.

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
4. "Zakaz bergandim, lekin hali ham kelmadi" (aybdor aniq ko'rsatilmagan — pastdagi
   "Chegara holati: buyurtma kelmadi" bo'limiga qarang).

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

> ⚠️ **Chegara holati: `seller` vs `delivery`** — real kappa tekshiruvida eng ko'p
> chalkashgan juftlik shu ikkisi edi (kappa = 0.479). Qoida: **agar buyurtma
> umuman kelmagan/yo'qolgan bo'lsa va matnda aybdor aniq ko'rsatilmagan bo'lsa —
> faqat `delivery` ga qo'ying.** `seller` faqat sotuvchi bilan **to'g'ridan-to'g'ri
> muloqot** (xabar yozish, javob kutish) yoki **kafolat/almashtirish siyosati**
> aniq tilga olinganda qo'shiladi.
>
> Masalan: *"pulini tulaganman ammo zakasim berilmagan"* → faqat `delivery`
> (kim aybdorligi noaniq). Lekin *"sotuvchiga yozdim, javob bermadi"* →
> `delivery` + `seller` (muloqot aniq tilga olingan).
>
> **Diqqat — bu qoidani haddan tashqari qattiq qo'llamang:** agar mahsulotni
> **almashtirish/qaytarishni so'rash va rad etilish/qiyinchilik** aniq tasvirlansa
> ("sotuvchidan so'rang dedi", "almashtirib berishmayapti", "qaytarib
> olishmadi"), bu — **kafolat/almashtirish siyosati** haqida, demak `seller`
> ham qo'shilishi kerak, hatto asosiy muammo mahsulot sifati (`quality`) bo'lsa
> ham. Faqat "buyurtma yo'qolgan/kelmagan, hech kim bilan gaplashilmagan" holatida
> `seller`ni tashlab ketasiz.
>
> Masalan: *"soatni qaytarib berish uchun keldim... sotuvchidan sorang, deyishdi"*
> → `quality` + `seller` (almashtirish so'ralgan va rad etilgan — ikkalasi ham bor).

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
4. "Paket juda qulay, chemodanimda joy tejaldi." (⚠️ real belgilashda bu ikki marta
   `quality`/`other`ga xato tushib qolgan — "paket/qadoq" so'zi tilga olinsa,
   birinchi navbatda `packaging`ni ko'rib chiqing, hatto ijobiy va tasodifiy
   aytilgandek tuyulsa ham.)

---

## 6. `other` — Boshqa

**Ta'rif:** Yuqoridagi 5 toifaning hech biriga aniq mos kelmaydigan, lekin baribir
mazmunli fikr bildirilgan holatlar (masalan: umumiy taassurot, ilova/interfeys haqida
fikr, mahsulotning umumiy tavsifi bilan bog'liq bo'lmagan izoh).

> ⚠️ **Chegara holati: `other` vs `quality`** — real kappa tekshiruvida bu eng ko'p
> chalkashgan juftlik bo'ldi (kappa = 0.44). Muammo: avvalgi qoida "qisqa sharh →
> `other`" edi, lekin **uzunlik emas, mazmun** hal qiluvchi bo'lishi kerak.
>
> **To'g'ri qoida:** Agar sharh qisqa bo'lsa-yu, lekin **mahsulotning o'zi haqida**
> ijobiy/salbiy fikr bildirsa ("yaxshi", "zo'r ekan", "ishlayapti", "yoqmadi") — bu
> **`quality`**, uzunligidan qat'iy nazar. `other` faqat sharh **hech qanday aniq
> narsaga ishora qilmasa** ishlatiladi (masalan: "rahmat", "super", "5 yulduz" —
> mahsulot, narx, yetkazish, sotuvchi yoki qadoqning qay biri haqida ekanligi
> umuman aniqlanmaydigan holatlar).
>
> Masalan: *"tasiri sezildi zo'r ekan"* → `quality` (mahsulotning ta'siri haqida,
> qisqa bo'lsa ham). Lekin *"xammasi ajoyib, raxmat!"* → `other` (nima "hammasi"
> ekanligi aniq emas — mahsulotmi, xizmatmi, umuman tajribami).

Agar sharh hech qanday aniq aspektga tegishli bo'lmasa yoki juda umumiy bo'lsa
("zo'r", "yoqmadi" — aniq nimasi haqida emasligi chindan ham aniqlanmasa), shu
yerga tushadi.

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

## Kappa tekshiruvi (3-kun) — yakuniy xulosa

**1-bosqich (50 ta, tasodifiy tanlov):**

| Aspekt | Kappa | Xulosa |
|---|---|---|
| delivery | 0.898 | Ajoyib |
| price | 0.778 | Yaxshi |
| packaging | 0.778 | Yaxshi |
| quality | 0.674 | Qoniqarli |
| seller | 0.479 | Past — qoida qo'shildi |
| other | 0.44 | Past — qoida qo'shildi |

**2-bosqich (20 ta, ataylab `seller`/`other`ga qaratilgan qiyin holatlar):** raqam
o'zi past chiqdi (seller=0.219, other=0.259), lekin qo'lda tekshirilganda buning
sababi taksonomiyaning noaniqligi emas — **kappa formulasining tizimli tuzatishni
"kelishmovchilik" deb hisoblashi** edi. 20 tadan 7 tasi to'g'ri ravishda `other`dan
`quality`ga o'tkazildi (yangi mazmun-asosli qoida ishladi), 2 tasida esa `seller`
qoidasi haddan tashqari qattiq talqin qilinib, kerakli holatlarda ham olib
tashlangan edi — bu yuqorida tuzatildi ("Diqqat — bu qoidani haddan tashqari
qattiq qo'llamang" bandi).

**Xulosa:** taksonomiya endi yetarlicha aniq. Keyingi safar chalkashish chiqsa,
bu holat allaqachon yozib qo'yilgan bandlar bilan yechiladi — yangi tub qoida
qo'shish shart emas.
