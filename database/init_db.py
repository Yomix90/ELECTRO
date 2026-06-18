"""
Script d'initialisation de la base de données avec données de démonstration.
Usage: python database/init_db.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database.models import db, Admin, Category, Product, ProductImage, SiteSettings

app = create_app()


def init_database():
    with app.app_context():
        db.create_all()
        print("[OK] Tables créées.")

        # ──────────────────────────────────────────
        # PARAMÈTRES DU SITE
        # ──────────────────────────────────────────
        defaults = {
            "nom_boutique": "ELECTRO-ORDINATEUR",
            "slogan_fr": "Votre spécialiste en informatique",
            "slogan_ar": "متخصصون في الحلول التقنية",
            "whatsapp_principal": "+212600000000",
            "whatsapp_secondaire": "",
            "email": "contact@electro-ordinateur.ma",
            "telephone": "+212522000000",
            "adresse_fr": "123 Rue de l'Informatique, Casablanca",
            "adresse_ar": "123 شارع الإعلاميات، الدار البيضاء",
            "horaires_fr": "Lun–Sam : 09h00–19h00",
            "horaires_ar": "الاثنين–السبت: 09:00–19:00",
            "facebook": "https://facebook.com/electroordinateur",
            "instagram": "https://instagram.com/electroordinateur",
            "google_maps_embed": "",
            "couleur_primaire": "#1a237e",
            "couleur_secondaire": "#ff6b35",
            "devise": "DH",
            "message_whatsapp_fr": "Bonjour, je suis intéressé(e) par : {nom} — Réf: {ref} — Prix: {prix} DH. {url}",
            "message_whatsapp_ar": "مرحباً، أنا مهتم بـ: {nom} — المرجع: {ref} — السعر: {prix} درهم. {url}",
            "a_propos_fr": "ELECTRO-ORDINATEUR est votre partenaire de confiance pour tous vos besoins informatiques depuis plus de 10 ans. Nous proposons une large gamme d'ordinateurs, de composants et d'accessoires aux meilleurs prix.",
            "a_propos_ar": "إلكترو أورديناتور هو شريكك الموثوق لجميع احتياجاتك في مجال الإعلاميات منذ أكثر من 10 سنوات. نقدم مجموعة واسعة من أجهزة الكمبيوتر والمكونات والملحقات بأفضل الأسعار.",
            "seuil_stock_faible": "5",
            "mode_maintenance": "0",
            "afficher_prix": "1",
            "logo": "",
        }

        for key, val in defaults.items():
            if not SiteSettings.query.get(key):
                db.session.add(SiteSettings(cle=key, valeur=val))
        db.session.commit()
        print("[OK] Paramètres du site insérés.")

        # ──────────────────────────────────────────
        # ADMIN PAR DÉFAUT
        # ──────────────────────────────────────────
        if not Admin.query.filter_by(username="admin").first():
            admin = Admin(
                username=os.getenv("ADMIN_USERNAME", "admin"),
                email="admin@electro-ordinateur.ma",
                role="superadmin",
            )
            admin.set_password(os.getenv("ADMIN_PASSWORD", "admin123"))
            db.session.add(admin)
            db.session.commit()
            print("[OK] Compte admin créé (admin / admin123)")
        else:
            print("[INFO]  Compte admin déjà existant.")

        # ──────────────────────────────────────────
        # CATÉGORIES
        # ──────────────────────────────────────────
        categories_data = [
            ("PC Bureau", "أجهزة كمبيوتر مكتبية", "pc-bureau", "bi-pc-display", 1),
            ("Laptops", "أجهزة محمولة", "laptops", "bi-laptop", 2),
            ("Composants", "مكونات الكمبيوتر", "composants", "bi-cpu", 3),
            ("Périphériques", "الملحقات", "peripheriques", "bi-mouse", 4),
            ("Imprimantes", "طابعات", "imprimantes", "bi-printer", 5),
            ("Accessoires", "إكسسوارات", "accessoires", "bi-headset", 6),
            ("Occasion / Reconditionné", "مستعمل / مُجدَّد", "occasion", "bi-recycle", 7),
            ("Réseau & Câblage", "الشبكات والأسلاك", "reseau", "bi-router", 8),
        ]

        cat_map = {}
        for nom_fr, nom_ar, slug, icone, ordre in categories_data:
            if not Category.query.filter_by(slug=slug).first():
                cat = Category(
                    nom_fr=nom_fr, nom_ar=nom_ar, slug=slug, icone=icone, ordre=ordre
                )
                db.session.add(cat)
                db.session.flush()
                cat_map[slug] = cat.id
            else:
                c = Category.query.filter_by(slug=slug).first()
                cat_map[slug] = c.id

        db.session.commit()
        print("[OK] Catégories insérées.")

        # ──────────────────────────────────────────
        # PRODUITS DE DÉMONSTRATION
        # ──────────────────────────────────────────
        demo_products = [
            {
                "reference": "LAP-DELL-I5-001",
                "nom_fr": "Dell Inspiron 15 — Intel Core i5",
                "nom_ar": "ديل إنسبيرون 15 — إنتل كور i5",
                "description_fr": "Laptop Dell Inspiron 15 équipé d'un processeur Intel Core i5 de 12ème génération, idéal pour le travail et les études. Écran Full HD 15.6 pouces, autonomie excellente.",
                "description_ar": "لابتوب Dell Inspiron 15 مجهز بمعالج Intel Core i5 من الجيل الثاني عشر، مثالي للعمل والدراسة. شاشة Full HD مقاس 15.6 بوصة، عمر بطارية ممتاز.",
                "categorie_slug": "laptops",
                "marque": "Dell",
                "prix": 6500,
                "prix_promo": 5999,
                "quantite_stock": 8,
                "etat": "neuf",
                "specs": {"CPU": "Intel Core i5-1235U", "RAM": "8 Go DDR4", "Stockage": "512 Go SSD NVMe", "Écran": "15.6\" Full HD IPS", "GPU": "Intel Iris Xe Graphics", "OS": "Windows 11 Home", "Garantie": "1 an"},
                "en_vedette": True,
            },
            {
                "reference": "LAP-HP-I7-002",
                "nom_fr": "HP EliteBook 840 G9 — Core i7 Pro",
                "nom_ar": "HP EliteBook 840 G9 — كور i7 للمحترفين",
                "description_fr": "Le HP EliteBook 840 G9 est un ultrabook professionnel robuste avec processeur Intel Core i7, sécurité avancée et autonomie de 16h. Parfait pour les professionnels en déplacement.",
                "description_ar": "HP EliteBook 840 G9 لابتوب احترافي متين بمعالج Intel Core i7، أمان متقدم واستقلالية تصل إلى 16 ساعة. مثالي للمحترفين في التنقل.",
                "categorie_slug": "laptops",
                "marque": "HP",
                "prix": 12500,
                "prix_promo": None,
                "quantite_stock": 3,
                "etat": "neuf",
                "specs": {"CPU": "Intel Core i7-1255U", "RAM": "16 Go DDR5", "Stockage": "512 Go SSD", "Écran": "14\" Full HD IPS Anti-reflet", "GPU": "Intel Iris Xe", "OS": "Windows 11 Pro", "Autonomie": "16h", "Garantie": "3 ans"},
                "en_vedette": True,
            },
            {
                "reference": "PC-BUREAU-GAM-003",
                "nom_fr": "PC Gaming Tour — Ryzen 7 + RTX 4060",
                "nom_ar": "كمبيوتر مكتبي للألعاب — Ryzen 7 + RTX 4060",
                "description_fr": "PC gamer haut de gamme avec AMD Ryzen 7 et RTX 4060. Profitez d'une expérience gaming fluide en 1080p et 1440p. Boîtier RGB, refroidissement liquide.",
                "description_ar": "كمبيوتر مكتبي للألعاب بمعالج AMD Ryzen 7 وبطاقة RTX 4060. استمتع بتجربة ألعاب سلسة بدقة 1080p و1440p. هيكل RGB وتبريد سائل.",
                "categorie_slug": "pc-bureau",
                "marque": "Custom Build",
                "prix": 18500,
                "prix_promo": 16999,
                "quantite_stock": 2,
                "etat": "neuf",
                "specs": {"CPU": "AMD Ryzen 7 7700X", "RAM": "32 Go DDR5 6000MHz", "Stockage": "1 To SSD NVMe PCIe 4.0", "GPU": "NVIDIA RTX 4060 8 Go", "Alimentation": "750W 80+ Gold", "Refroidissement": "AIO 240mm", "Garantie": "2 ans"},
                "en_vedette": True,
            },
            {
                "reference": "COMP-RAM-DDR4-004",
                "nom_fr": "RAM Kingston 16 Go DDR4 3200MHz",
                "nom_ar": "ذاكرة Kingston 16 جيجا DDR4 3200MHz",
                "description_fr": "Barrette de RAM Kingston FURY Beast 16 Go DDR4 3200MHz. Compatible avec la plupart des plateformes Intel et AMD. Profil XMP 2.0 pour overclocking automatique.",
                "description_ar": "شريط ذاكرة Kingston FURY Beast 16 جيجا DDR4 3200MHz. متوافق مع معظم منصات Intel وAMD. ملف XMP 2.0 للرفع التلقائي للتردد.",
                "categorie_slug": "composants",
                "marque": "Kingston",
                "prix": 450,
                "prix_promo": None,
                "quantite_stock": 25,
                "etat": "neuf",
                "specs": {"Capacité": "16 Go (1x16Go)", "Type": "DDR4", "Fréquence": "3200 MHz", "Latence": "CL16", "Profil XMP": "XMP 2.0", "Garantie": "À vie"},
                "en_vedette": False,
            },
            {
                "reference": "PER-CLAV-MECA-005",
                "nom_fr": "Clavier Mécanique Gaming Redragon K552",
                "nom_ar": "لوحة مفاتيح ميكانيكية للألعاب Redragon K552",
                "description_fr": "Clavier mécanique compact TKL avec switches rouges linéaires. Rétroéclairage RGB, construction métallique robuste. Parfait pour les gamers et les développeurs.",
                "description_ar": "لوحة مفاتيح ميكانيكية مضغوطة TKL بمفاتيح حمراء خطية. إضاءة خلفية RGB، هيكل معدني متين. مثالية للاعبين والمطورين.",
                "categorie_slug": "peripheriques",
                "marque": "Redragon",
                "prix": 350,
                "prix_promo": None,
                "quantite_stock": 15,
                "etat": "neuf",
                "specs": {"Type": "Mécanique TKL", "Switches": "Red (Linéaires)", "Rétroéclairage": "RGB", "Connexion": "USB", "Anti-ghosting": "Oui, 87 touches", "Garantie": "1 an"},
                "en_vedette": False,
            },
            {
                "reference": "IMP-HP-LASER-006",
                "nom_fr": "Imprimante HP LaserJet Pro M404dn",
                "nom_ar": "طابعة HP LaserJet Pro M404dn",
                "description_fr": "Imprimante laser monochrome professionnelle avec impression recto-verso automatique et connectivité réseau. Vitesse 38 ppm, idéale pour les bureaux.",
                "description_ar": "طابعة ليزر أحادية اللون احترافية مع طباعة دوبلكس تلقائية واتصال بالشبكة. سرعة 38 صفحة في الدقيقة، مثالية للمكاتب.",
                "categorie_slug": "imprimantes",
                "marque": "HP",
                "prix": 3200,
                "prix_promo": None,
                "quantite_stock": 5,
                "etat": "neuf",
                "specs": {"Type": "Laser monochrome", "Vitesse": "38 ppm", "Résolution": "1200 x 1200 dpi", "Recto-verso": "Automatique", "Connectivité": "USB + Ethernet", "Format papier": "A4", "Garantie": "1 an"},
                "en_vedette": False,
            },
            {
                "reference": "LAP-LENOVO-OCC-007",
                "nom_fr": "Lenovo ThinkPad T480 — Occasion Grade A",
                "nom_ar": "Lenovo ThinkPad T480 — مستعمل درجة أ",
                "description_fr": "ThinkPad T480 reconditionné en excellent état. Testé et certifié, batterie neuve. Idéal pour les étudiants et petits budgets. Garantie 6 mois.",
                "description_ar": "ThinkPad T480 مُجدَّد في حالة ممتازة. مُختبر ومُعتمد، بطارية جديدة. مثالي للطلاب والميزانيات الصغيرة. ضمان 6 أشهر.",
                "categorie_slug": "occasion",
                "marque": "Lenovo",
                "prix": 2800,
                "prix_promo": None,
                "quantite_stock": 4,
                "etat": "occasion",
                "specs": {"CPU": "Intel Core i5-8250U", "RAM": "8 Go DDR4", "Stockage": "256 Go SSD", "Écran": "14\" Full HD IPS", "OS": "Windows 10 Pro", "État": "Grade A (Excellent)", "Garantie": "6 mois"},
                "en_vedette": True,
            },
            {
                "reference": "ACC-MON-24-008",
                "nom_fr": "Écran 24\" Samsung Full HD — 75Hz IPS",
                "nom_ar": "شاشة 24 بوصة Samsung Full HD — 75Hz IPS",
                "description_fr": "Moniteur Samsung 24 pouces Full HD avec dalle IPS, taux de rafraîchissement 75Hz et temps de réponse 5ms. Support réglable en hauteur, HDMI + VGA.",
                "description_ar": "شاشة Samsung 24 بوصة Full HD بلوحة IPS، معدل تحديث 75Hz وزمن استجابة 5ms. حامل قابل للضبط، HDMI + VGA.",
                "categorie_slug": "peripheriques",
                "marque": "Samsung",
                "prix": 1800,
                "prix_promo": 1650,
                "quantite_stock": 10,
                "etat": "neuf",
                "specs": {"Taille": "24 pouces", "Résolution": "1920 x 1080 (Full HD)", "Type dalle": "IPS", "Taux de rafraîchissement": "75Hz", "Temps de réponse": "5ms", "Ports": "HDMI, VGA", "Garantie": "2 ans"},
                "en_vedette": False,
            },
            {
                "reference": "COMP-SSD-500-009",
                "nom_fr": "SSD Samsung 970 EVO Plus 500 Go NVMe",
                "nom_ar": "SSD Samsung 970 EVO Plus 500 جيجا NVMe",
                "description_fr": "SSD NVMe M.2 Samsung avec lectures séquentielles de 3500 Mo/s. Parfait pour booster votre PC ou remplacer un ancien HDD. Garantie 5 ans.",
                "description_ar": "SSD NVMe M.2 من Samsung بسرعات قراءة تسلسلية تصل إلى 3500 ميجابايت/ثانية. مثالي لتسريع جهازك أو استبدال HDD قديم. ضمان 5 سنوات.",
                "categorie_slug": "composants",
                "marque": "Samsung",
                "prix": 600,
                "prix_promo": None,
                "quantite_stock": 20,
                "etat": "neuf",
                "specs": {"Capacité": "500 Go", "Interface": "M.2 NVMe PCIe 3.0", "Lecture séquentielle": "3500 Mo/s", "Écriture séquentielle": "3300 Mo/s", "Endurance": "300 TBW", "Garantie": "5 ans"},
                "en_vedette": False,
            },
            {
                "reference": "ACC-CASQ-HYPER-010",
                "nom_fr": "Casque Gaming HyperX Cloud II — Rouge",
                "nom_ar": "سماعة الألعاب HyperX Cloud II — أحمر",
                "description_fr": "Casque gaming HyperX Cloud II avec son surround 7.1 virtuel, microphone détachable anti-bruit. Confort exceptionnel avec coussinets en mousse à mémoire.",
                "description_ar": "سماعة HyperX Cloud II للألعاب مع صوت محيطي 7.1 افتراضي، ميكروفون قابل للفصل مضاد للضوضاء. راحة استثنائية مع وسادات من الإسفنج المشكّل.",
                "categorie_slug": "accessoires",
                "marque": "HyperX",
                "prix": 800,
                "prix_promo": 699,
                "quantite_stock": 7,
                "etat": "neuf",
                "specs": {"Pilotes": "53mm", "Fréquence": "15Hz–25kHz", "Impédance": "60 Ω", "Son surround": "7.1 virtuel (USB)", "Microphone": "Détachable, cardioïde", "Connexion": "3.5mm + USB", "Garantie": "2 ans"},
                "en_vedette": False,
            },
            {
                "reference": "PC-BUREAU-OFFI-011",
                "nom_fr": "PC Bureau Bureau — Intel i3 Office Pack",
                "nom_ar": "كمبيوتر مكتبي — إنتل i3 للمكاتب",
                "description_fr": "PC de bureau complet pour usage bureautique. Livré avec clavier, souris et câble HDMI. Processeur Intel Core i3, rapide et fiable pour Word, Excel, navigation web.",
                "description_ar": "كمبيوتر مكتبي كامل للاستخدام المكتبي. يُسلَّم مع لوحة مفاتيح وفأرة وكابل HDMI. معالج Intel Core i3، سريع وموثوق لـ Word وExcel وتصفح الإنترنت.",
                "categorie_slug": "pc-bureau",
                "marque": "Custom Build",
                "prix": 3500,
                "prix_promo": None,
                "quantite_stock": 12,
                "etat": "neuf",
                "specs": {"CPU": "Intel Core i3-12100", "RAM": "8 Go DDR4", "Stockage": "256 Go SSD", "Carte graphique": "Intel UHD 730", "OS": "Windows 11 Home", "Inclus": "Clavier + Souris + Câble HDMI", "Garantie": "1 an"},
                "en_vedette": False,
            },
            {
                "reference": "RES-SWITCH-005-012",
                "nom_fr": "Switch Réseau TP-Link 8 ports Gigabit",
                "nom_ar": "سويتش شبكة TP-Link 8 منافذ جيجابت",
                "description_fr": "Switch non géré 8 ports Gigabit pour réseau domestique ou PME. Installation plug-and-play, très faible consommation énergétique.",
                "description_ar": "سويتش غير مُدار بـ 8 منافذ جيجابت لشبكات المنازل أو الشركات الصغيرة. تركيب Plug-and-Play، استهلاك طاقة منخفض جداً.",
                "categorie_slug": "reseau",
                "marque": "TP-Link",
                "prix": 250,
                "prix_promo": None,
                "quantite_stock": 30,
                "etat": "neuf",
                "specs": {"Ports": "8 x Gigabit Ethernet", "Vitesse": "10/100/1000 Mbps", "Type": "Non géré", "Alimentation": "Adaptateur externe", "Dimensions": "158 x 101 x 25 mm", "Garantie": "2 ans"},
                "en_vedette": False,
            },
        ]

        for p_data in demo_products:
            if Product.query.filter_by(reference=p_data["reference"]).first():
                continue

            cat_slug = p_data.pop("categorie_slug")
            specs_dict = p_data.pop("specs")

            product = Product(
                categorie_id=cat_map.get(cat_slug),
                specs=json.dumps(specs_dict, ensure_ascii=False),
                **p_data,
            )
            db.session.add(product)

        db.session.commit()
        print(f"[OK] {len(demo_products)} produits de démonstration insérés.")
        print("\n[OK] Base de données initialisée avec succès!")
        print("   -> Admin: admin / admin123")
        print("   -> URL: http://localhost:5000")
        print("   -> Admin: http://localhost:5000/admin/")


if __name__ == "__main__":
    init_database()
