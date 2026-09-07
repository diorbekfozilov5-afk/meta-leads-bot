"""
Meta (Facebook/Instagram) Lead Ads -> Google Sheets (Apps Script orqali)

Ishlash tartibi:
1. Foydalanuvchi Meta reklamasidagi lead formasini to'ldiradi.
2. Meta bizning /webhook manzilimizga "leadgen" hodisasi haqida xabar yuboradi
   (xabarda faqat leadgen_id bo'ladi, to'liq ma'lumot bo'lmaydi).
3. Biz shu leadgen_id bilan Meta Graph API'dan lead'ning to'liq ma'lumotini
   (ism, telefon, email va h.k.) so'rab olamiz.
4. Ma'lumotni Google Apps Script web app manziliga POST qilamiz, u esa
   Google Sheets'ga yangi qator sifatida yozadi.

Ishga tushirishdan oldin: .env faylini to'ldiring va README.md'ni o'qing.
"""

import os
import logging
from datetime import datetime

import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leads-bot")

# --- Sozlamalar (.env fayldan yoki Render Environment Variables'dan olinadi) ---
VERIFY_TOKEN = os.environ["META_VERIFY_TOKEN"]            # webhook tasdiqlash uchun o'zingiz o'ylab topgan so'z
PAGE_ACCESS_TOKEN = os.environ["META_PAGE_ACCESS_TOKEN"]  # Meta Business'dan olinadigan token
GRAPH_API_VERSION = os.environ.get("META_GRAPH_API_VERSION", "v21.0")
GOOGLE_SCRIPT_URL = os.environ["GOOGLE_SCRIPT_URL"]       # Apps Script web app manzili (.../exec)


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta birinchi marta webhook manzilini sozlaganda shu yerga GET so'rov yuboradi."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook tasdiqlandi.")
        return challenge, 200

    logger.warning("Webhook tasdiqlash muvaffaqiyatsiz: noto'g'ri token.")
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    """Meta yangi lead kelganda shu yerga POST so'rov yuboradi."""
    payload = request.get_json(silent=True) or {}
    logger.info("Webhook payload keldi: %s", payload)

    try:
        entries = payload.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                if change.get("field") != "leadgen":
                    continue
                value = change.get("value", {})
                leadgen_id = value.get("leadgen_id")
                form_id = value.get("form_id")
                ad_id = value.get("ad_id")

                if not leadgen_id:
                    logger.warning("leadgen_id topilmadi, o'tkazib yuborildi: %s", value)
                    continue

                lead_data = fetch_lead_details(leadgen_id)
                save_lead(lead_data, form_id=form_id, ad_id=ad_id)

    except Exception:
        logger.exception("Webhook'ni qayta ishlashda xatolik yuz berdi.")
        # Meta'ga baribir 200 qaytaramiz, aks holda u qayta-qayta urinaveradi
        return jsonify(status="error"), 200

    return jsonify(status="ok"), 200


def fetch_lead_details(leadgen_id: str) -> dict:
    """Meta Graph API'dan lead'ning to'liq ma'lumotini (ism, telefon, email...) oladi."""
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{leadgen_id}"
    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "fields": "field_data,created_time,ad_id,form_id,campaign_id,adgroup_id",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # field_data -> [{"name": "full_name", "values": ["Ali Aliyev"]}, ...] shaklida keladi,
    # buni oddiy {"full_name": "Ali Aliyev"} lug'atga aylantiramiz
    fields = {}
    for item in data.get("field_data", []):
        name = item.get("name")
        values = item.get("values", [])
        fields[name] = values[0] if values else ""

    return {
        "leadgen_id": leadgen_id,
        "created_time": data.get("created_time"),
        "campaign_id": data.get("campaign_id"),
        "fields": fields,
    }


def save_lead(lead_data: dict, form_id=None, ad_id=None):
    """Lead ma'lumotini Google Apps Script orqali Google Sheets'ga yozadi."""
    fields = lead_data.get("fields", {})
    payload = {
        "vaqt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "leadgen_id": lead_data.get("leadgen_id", ""),
        "full_name": fields.get("full_name", ""),
        "phone_number": fields.get("phone_number", ""),
        "email": fields.get("email", ""),
        "form_id": form_id or "",
        "ad_id": ad_id or "",
        "campaign_id": lead_data.get("campaign_id", ""),
    }

    response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
    response.raise_for_status()
    logger.info("Yangi lead Google Sheets'ga yozildi: %s", payload)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
