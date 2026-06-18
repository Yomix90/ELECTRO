from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    nom_fr = db.Column(db.String(100), nullable=False)
    nom_ar = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icone = db.Column(db.String(50), default="bi-box")
    image = db.Column(db.String(255), nullable=True)
    ordre = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    produits = db.relationship("Product", backref="categorie", lazy="dynamic")

    def nom(self, lang="fr"):
        return self.nom_ar if lang == "ar" else self.nom_fr

    def __repr__(self):
        return f"<Category {self.nom_fr}>"


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    nom_fr = db.Column(db.String(200), nullable=False)
    nom_ar = db.Column(db.String(200), nullable=False)
    description_fr = db.Column(db.Text, default="")
    description_ar = db.Column(db.Text, default="")
    specs = db.Column(db.Text, default="{}")  # JSON: {"CPU": "...", "RAM": "..."}
    categorie_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    marque = db.Column(db.String(100), default="")
    prix = db.Column(db.Float, nullable=False, default=0)
    prix_promo = db.Column(db.Float, nullable=True)
    promo_debut = db.Column(db.DateTime, nullable=True)
    promo_fin = db.Column(db.DateTime, nullable=True)
    quantite_stock = db.Column(db.Integer, default=0)
    etat = db.Column(db.String(20), default="neuf")  # neuf / occasion / reconditionne
    statut = db.Column(db.String(20), default="visible")  # visible / masque / brouillon
    en_vedette = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    nb_vues = db.Column(db.Integer, default=0)
    nb_clics_whatsapp = db.Column(db.Integer, default=0)
    images = db.relationship("ProductImage", backref="product", lazy="dynamic",
                              cascade="all, delete-orphan", order_by="ProductImage.ordre")

    def nom(self, lang="fr"):
        return self.nom_ar if lang == "ar" else self.nom_fr

    def description(self, lang="fr"):
        return self.description_ar if lang == "ar" else self.description_fr

    @property
    def image_principale(self):
        img = self.images.first()
        return img.chemin_fichier if img else None

    @property
    def prix_actuel(self):
        """Retourne le prix promo si applicable, sinon le prix normal."""
        now = datetime.utcnow()
        if self.prix_promo:
            if self.promo_debut and self.promo_fin:
                if self.promo_debut <= now <= self.promo_fin:
                    return self.prix_promo
            elif self.prix_promo:
                return self.prix_promo
        return self.prix

    @property
    def en_promo(self):
        now = datetime.utcnow()
        if not self.prix_promo:
            return False
        if self.promo_debut and self.promo_fin:
            return self.promo_debut <= now <= self.promo_fin
        return bool(self.prix_promo)

    @property
    def badge(self):
        if self.quantite_stock == 0:
            return "rupture"
        if self.en_promo:
            return "promo"
        age = (datetime.utcnow() - self.date_creation).days
        if age <= 30:
            return "nouveau"
        if self.etat == "occasion":
            return "occasion"
        return None

    @property
    def en_stock(self):
        return self.quantite_stock > 0

    def get_specs_dict(self):
        import json
        try:
            return json.loads(self.specs) if self.specs else {}
        except Exception:
            return {}

    def __repr__(self):
        return f"<Product {self.reference} - {self.nom_fr}>"


class ProductImage(db.Model):
    __tablename__ = "product_images"
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    chemin_fichier = db.Column(db.String(255), nullable=False)
    ordre = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Image {self.chemin_fichier}>"


class SiteSettings(db.Model):
    __tablename__ = "site_settings"
    cle = db.Column(db.String(100), primary_key=True)
    valeur = db.Column(db.Text, default="")

    @staticmethod
    def get(key, default=""):
        s = SiteSettings.query.get(key)
        return s.valeur if s else default

    @staticmethod
    def set(key, value):
        s = SiteSettings.query.get(key)
        if s:
            s.valeur = str(value)
        else:
            s = SiteSettings(cle=key, valeur=str(value))
            db.session.add(s)
        db.session.commit()

    @staticmethod
    def get_all_dict():
        return {s.cle: s.valeur for s in SiteSettings.query.all()}

    def __repr__(self):
        return f"<Setting {self.cle}={self.valeur}>"


class Admin(db.Model, UserMixin):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="manager")  # superadmin / manager / readonly
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime, nullable=True)
    logs = db.relationship("ActivityLog", backref="admin", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    @property
    def is_superadmin(self):
        return self.role == "superadmin"

    @property
    def can_edit(self):
        return self.role in ("superadmin", "manager")

    def __repr__(self):
        return f"<Admin {self.username} ({self.role})>"


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, default="")
    ip_address = db.Column(db.String(45), default="")
    date_heure = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Log {self.action} at {self.date_heure}>"


class WhatsAppClick(db.Model):
    __tablename__ = "whatsapp_clicks"
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    date_heure = db.Column(db.DateTime, default=datetime.utcnow)
    lang = db.Column(db.String(5), default="fr")


class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    date_vente = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    nom_client = db.Column(db.String(100), nullable=False)
    telephone_client = db.Column(db.String(50), nullable=True)
    adresse_client = db.Column(db.Text, nullable=True)
    statut = db.Column(db.String(20), default="complete")  # complete, en_attente, annule
    montant_total = db.Column(db.Float, nullable=False, default=0.0)
    montant_paye = db.Column(db.Float, nullable=False, default=0.0)
    statut_paiement = db.Column(db.String(20), default="non_paye")  # non_paye, partiellement_paye, paye
    commentaire = db.Column(db.Text, nullable=True)

    items = db.relationship("SaleItem", backref="sale", lazy="dynamic", cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="sale", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def reste_a_payer(self):
        return max(0.0, self.montant_total - self.montant_paye)

    def recalculate_totals(self):
        self.montant_total = sum(item.sous_total for item in self.items)
        self.montant_paye = sum(payment.montant for payment in self.payments)
        if self.montant_paye <= 0:
            self.statut_paiement = "non_paye"
        elif self.montant_paye >= self.montant_total:
            self.statut_paiement = "paye"
        else:
            self.statut_paiement = "partiellement_paye"


class SaleItem(db.Model):
    __tablename__ = "sale_items"
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    reference_produit = db.Column(db.String(50), nullable=False)
    nom_produit = db.Column(db.String(200), nullable=False)
    quantite = db.Column(db.Integer, nullable=False, default=1)
    prix_unitaire = db.Column(db.Float, nullable=False)
    sous_total = db.Column(db.Float, nullable=False)

    produit = db.relationship("Product", backref="sale_items")


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    date_paiement = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    montant = db.Column(db.Float, nullable=False)
    mode_paiement = db.Column(db.String(50), nullable=False)  # Espèces, Virement, Versement, Autre
    reference_paiement = db.Column(db.String(100), nullable=True)
    preuve_paiement = db.Column(db.String(255), nullable=True)  # File path
    notes = db.Column(db.Text, nullable=True)

