# Meta Lead Ads → Google Sheets bot

Bu bot Meta (Facebook/Instagram) Lead Ads formasidan kelgan leadlarni avtomatik
ravishda Google Sheets jadvaliga yozib boradi.

## Qanday ishlaydi

1. Mijoz reklamadagi lead formani to'ldiradi.
2. Meta sizning serveringizga (`/webhook`) xabar yuboradi.
3. Server Meta Graph API orqali lead'ning to'liq ma'lumotini (ism, telefon, email) so'rab oladi.
4. Ma'lumot Google Sheets'ga yangi qator sifatida qo'shiladi.

---

## 1-QADAM: Google Sheets tayyorlash

1. [Google Cloud Console](https://console.cloud.google.com/) da yangi loyiha yarating.
2. **APIs & Services → Library** bo'limidan **Google Sheets API**'ni yoqing.
3. **APIs & Services → Credentials → Create Credentials → Service Account** orqali
   xizmat hisobi (service account) yarating.
4. Yaratilgan service account uchun **JSON kalit** yuklab oling — bu faylni
   `service_account.json` nomi bilan loyiha papkasiga qo'ying.
5. Google Sheets'da yangi jadval yarating, uni oching va **Share** tugmasi orqali
   service account'ning email manzilini (masalan `xxx@xxx.iam.gserviceaccount.com`)
   **Editor** huquqi bilan qo'shing.
6. Jadval URL'idagi ID'ni nusxalab oling:
   `https://docs.google.com/spreadsheets/d/BU_YERDA_ID/edit` → `.env` fayldagi
   `GOOGLE_SPREADSHEET_ID` ga shuni yozing.

## 2-QADAM: Meta (Facebook) tomonini sozlash

1. [Meta for Developers](https://developers.facebook.com/) saytida yangi **App** yarating
   (turi: Business).
2. Ilovangizga **Webhooks** va **Lead Ads** mahsulotlarini qo'shing.
3. **Webhooks** bo'limida:
   - Callback URL: `https://SIZNING_SERVERINGIZ/webhook`
   - Verify Token: `.env` faylidagi `META_VERIFY_TOKEN` bilan bir xil bo'lishi kerak
   - Subscription fields: `leadgen` ni tanlang
4. Sizning Facebook Page'ingizni ilova bilan bog'lang va `leadgen` obunasini yoqing
   (bu odatda Graph API Explorer yoki App Dashboard'dagi "Page Subscriptions" orqali qilinadi).
5. **Page Access Token** oling (uzoq muddatli/never-expiring token tavsiya etiladi) va
   `.env` faylidagi `META_PAGE_ACCESS_TOKEN` ga yozing.

> Eslatma: Meta odatda ilovangizni "Live" rejimga o'tkazishdan oldin
> App Review'dan (`leads_retrieval` ruxsati uchun) o'tkazishni talab qiladi.
> Test rejimida o'zingizning test formangiz bilan sinab ko'rishingiz mumkin.

## 3-QADAM: Serverni ishga tushirish

```bash
# Kerakli kutubxonalarni o'rnatish
pip install -r requirements.txt

# .env faylini sozlash
cp .env.example .env
# .env faylini o'zingizning ma'lumotlaringiz bilan to'ldiring

# Serverni ishga tushirish
python app.py
```

Server standart holatda `5000`-portda ishlaydi. Meta webhook'i internetdan
kirish imkoniyati bo'lgan HTTPS manzilni talab qiladi, shuning uchun:

- **Test qilish uchun**: [ngrok](https://ngrok.com/) yoki shunga o'xshash vosita bilan
  lokal serveringizni vaqtinchalik internetga chiqaring (`ngrok http 5000`).
- **Ishlab chiqarish uchun**: serverni haqiqiy hostingga (masalan Render, Railway,
  VPS + Nginx, yoki Google Cloud Run) joylashtiring.

## Fayllar tuzilishi

```
meta-leads-bot/
├── app.py              # Asosiy Flask server (webhook qabul qiladi)
├── sheets.py           # Google Sheets bilan ishlash funksiyalari
├── requirements.txt    # Python kutubxonalari
├── .env.example        # Sozlamalar namunasi
└── README.md           # Shu fayl
```

## Google Sheets'dagi ustunlar

| Vaqt | Lead ID | Ism | Telefon | Email | Form ID | Ad ID | Campaign ID |
|------|---------|-----|---------|-------|---------|-------|-------------|

## Keyingi qadamlar (ixtiyoriy takliflar)

- Telegram'ga ham bildirishnoma yuborish (masalan, yangi lead kelganda menejerga xabar).
- Ma'lumotlarni Google Sheets bilan bir qatorda CRM'ga ham yozish.
- Xatoliklarni (masalan, Meta API tokenning muddati tugashi) Telegram orqali kuzatib borish.

Shu funksiyalardan birortasi kerak bo'lsa, aytib qo'ying — qo'shib beraman.
