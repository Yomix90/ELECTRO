import json
import urllib.parse
from datetime import datetime
from flask import session, request, current_app
from database.models import SiteSettings


def get_lang() -> str:
    """Return current language from session, default 'fr'."""
    return session.get("lang", "fr")


def t(key: str) -> str:
    """Translate a key using loaded translations."""
    translations = current_app.config.get("TRANSLATIONS", {})
    lang = get_lang()
    return translations.get(lang, {}).get(key, key)


def is_rtl() -> bool:
    return get_lang() == "ar"


def load_translations(app):
    """Load JSON translation files into app config."""
    import os
    translations = {}
    trans_dir = os.path.join(app.root_path, "translations")
    for lang in ["fr", "ar"]:
        path = os.path.join(trans_dir, f"{lang}.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                translations[lang] = json.load(f)
    app.config["TRANSLATIONS"] = translations


def build_whatsapp_url(product, lang: str = "fr", base_url: str = "") -> str:
    """Build a WhatsApp click-to-chat URL with pre-filled message."""
    number = SiteSettings.get("whatsapp_principal", "+212600000000").replace(" ", "").replace("-", "")
    
    nom = product.nom(lang)
    prix = product.prix_actuel
    devise = SiteSettings.get("devise", "DH")
    product_url = f"{base_url}/produit/{product.id}"

    if lang == "ar":
        template = SiteSettings.get(
            "message_whatsapp_ar",
            "مرحباً، أنا مهتم بـ: {nom} — المرجع: {ref} — السعر: {prix} {devise}. {url}"
        )
    else:
        template = SiteSettings.get(
            "message_whatsapp_fr",
            "Bonjour, je suis intéressé(e) par : {nom} — Réf: {ref} — Prix: {prix} {devise}. {url}"
        )

    message = template.format(
        nom=nom,
        ref=product.reference,
        prix=f"{prix:,.0f}",
        devise=devise,
        url=product_url,
    )
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{number}?text={encoded}"


def build_whatsapp_group_url(items: list, lang: str = "fr", base_url: str = "") -> str:
    """Build WhatsApp URL for multiple products (group cart)."""
    number = SiteSettings.get("whatsapp_principal", "+212600000000").replace(" ", "").replace("-", "")
    devise = SiteSettings.get("devise", "DH")
    
    if lang == "ar":
        header = "مرحباً، أنا مهتم بالمنتجات التالية:\n"
        footer = "\nشكراً لكم."
    else:
        header = "Bonjour, je suis intéressé(e) par les articles suivants :\n"
        footer = "\nMerci."

    lines = []
    for item in items:
        nom = item.get("nom", "")
        ref = item.get("ref", "")
        prix = item.get("prix", "")
        lines.append(f"• {nom} — Réf: {ref} — {prix} {devise}")

    message = header + "\n".join(lines) + footer
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{number}?text={encoded}"


def format_price(amount: float, devise: str = "DH") -> str:
    """Format a price nicely."""
    if amount is None:
        return ""
    return f"{amount:,.0f} {devise}".replace(",", " ")


def slugify(text: str) -> str:
    """Basic slugify for category names."""
    import re
    text = text.lower().strip()
    text = re.sub(r"[àáâãäå]", "a", text)
    text = re.sub(r"[éèêë]", "e", text)
    text = re.sub(r"[ïî]", "i", text)
    text = re.sub(r"[ôö]", "o", text)
    text = re.sub(r"[üùú]", "u", text)
    text = re.sub(r"[ç]", "c", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text.strip("-")


def log_action(db, admin_id, action: str, details: str = ""):
    """Helper to create an activity log entry."""
    from database.models import ActivityLog
    log = ActivityLog(
        admin_id=admin_id,
        action=action,
        details=details,
        ip_address=request.remote_addr or "",
    )
    db.session.add(log)
