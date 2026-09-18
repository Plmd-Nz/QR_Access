# app/models.py

from .extensions import db
from datetime import datetime

# ===========================================
# 1. Tables de Référence (Facultés & Promotions)
# ===========================================

class Faculte(db.Model):
    __tablename__ = 'facultes'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    code_court = db.Column(db.String(10), unique=True, nullable=False)
    
    # Relation : Une Faculté peut avoir plusieurs Promotions
    promotions = db.relationship('Promotion', backref='faculte', lazy=True)

    def __repr__(self):
        return f'<Faculte {self.nom}>'

class Promotion(db.Model):
    __tablename__ = 'promotions'
    id = db.Column(db.Integer, primary_key=True)
    faculte_id = db.Column(db.Integer, db.ForeignKey('facultes.id', ondelete='RESTRICT'), nullable=False)
    nom = db.Column(db.String(100), nullable=False, comment='Ex: BAC-1 INFO')
    filiere = db.Column(db.String(100), nullable=True, comment='Ex: Informatique, Gestion')
    
    # Relation : Une Promotion peut être la Cible de plusieurs Points d'Accès
    points_acces = db.relationship('PointAcces', backref='promotion_cible', lazy=True)
    
    # Contrainte UNIQUE pour éviter les doublons dans une même faculté
    __table_args__ = (db.UniqueConstraint('faculte_id', 'nom', name='unique_promotion_per_faculte'),)

    def __repr__(self):
        return f'<Promotion {self.nom}>'

# ===========================================
# 2. Table Administrateurs
# ===========================================

class Administrateur(db.Model):
    __tablename__ = 'administrateurs'
    id = db.Column(db.Integer, primary_key=True)
    nom_utilisateur = db.Column(db.String(50), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False, comment='Mot de passe haché (Bcrypt)')
    nom_complet = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Administrateur {self.nom_utilisateur}>'

# ===========================================
# 3. Table Étudiants (Clé Centrale)
# ===========================================

class Etudiant(db.Model):
    __tablename__ = 'etudiants'
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    postnom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.Enum('M', 'F'), nullable=False)
    absences = db.relationship('Absence', backref='etudiant', lazy=True)
    
    # Clés Étrangères pour Facultés/Promotions
    faculte_id = db.Column(db.Integer, db.ForeignKey('facultes.id', ondelete='RESTRICT'), nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotions.id', ondelete='RESTRICT'), nullable=False)
    
    email = db.Column(db.String(50), unique=True, nullable=False)
    photo_path = db.Column(db.String(255), nullable=True, comment='Chemin du fichier photo traité (fond transparent)')
    qr_code_cle = db.Column(db.String(64), unique=True, nullable=False, comment='Clé unique (hash) du QR code scannable')
    
    # CHAMP DE DÉNORMALISATION (pour la rapidité du scan)
    montant_total_paye = db.Column(db.Numeric(10, 2), default=0.00, comment='Solde des paiements validés pour vérification rapide')
    
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations : Un étudiant a plusieurs paiements, accès et présences
    paiements = db.relationship('Paiement', backref='etudiant', lazy=True)
    registres_acces = db.relationship('RegistreAcces', backref='etudiant', lazy=True)
    presences = db.relationship('Presence', backref='etudiant', lazy=True)
    
    # Relations pour l'accès direct aux objets (plus facile dans le code)
    faculte_obj = db.relationship('Faculte', foreign_keys=[faculte_id], lazy=True)
    promotion_obj = db.relationship('Promotion', foreign_keys=[promotion_id], lazy=True)
    absences = db.relationship('Absence', backref='etudiant', lazy=True)

    def __repr__(self):
        return f'<Etudiant {self.matricule}>'


# ===========================================
# 4. Table Points d'Accès
# ===========================================

class PointAcces(db.Model):
    __tablename__ = 'points_acces'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False, comment='Nom du point d accès (ex: Entrée Nord, Auditoire INFO-1)')
    type_acces = db.Column(db.Enum('Principal', 'Cours', 'Examen', 'Laboratoire'), nullable=False, comment='Type d accès pour application des règles')
    
    # Clé Étrangère vers la promotion (NULL si Principal/Examen)
    promotion_cible_id = db.Column(db.Integer, db.ForeignKey('promotions.id', ondelete='SET NULL'), nullable=True, comment='ID de la promotion dont c est l auditoire attitré')

    def __repr__(self):
        return f'<PointAcces {self.nom}>'

# ===========================================
# 5. Table Paiements (Source de Vérité)
# ===========================================

class Paiement(db.Model):
    __tablename__ = 'paiements'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    motif = db.Column(db.String(50), nullable=False, comment='Ex: frais académique, frais d examen')
    date_paiement = db.Column(db.Date, nullable=False)
    annee_academique = db.Column(db.String(20), nullable=False, comment='Ex: 2024-2025')
    statut = db.Column(db.Enum('valide', 'en_attente', 'rejete', 'partiel'), default='en_attente', nullable=False)

    def __repr__(self):
        return f'<Paiement Etudiant:{self.etudiant_id} - {self.montant}>'

# ===========================================
# 6. Table Registre d'Accès (TOUTES les tentatives)
# ===========================================

class RegistreAcces(db.Model):
    __tablename__ = 'registre_acces'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)
    point_acces_id = db.Column(db.Integer, db.ForeignKey('points_acces.id', ondelete='RESTRICT'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='Date et heure complètes du scan')
    statut = db.Column(db.Enum('autorise', 'refuse'), nullable=False)
    raison_refus = db.Column(db.Text, nullable=True, comment='Raison si l accès est refusé')
    
    # Relations pour l'accès direct aux objets
    point_acces = db.relationship('PointAcces', backref='registres_acces', lazy=True)

    def __repr__(self):
        return f'<RegistreAcces {self.etudiant_id} - {self.statut}>'

# ===========================================
# 7. Table Présences (Validations Académiques)
# ===========================================

class Presence(db.Model):
    __tablename__ = 'presences'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)
    point_acces_id = db.Column(db.Integer, db.ForeignKey('points_acces.id', ondelete='RESTRICT'), nullable=False)
    date_presence = db.Column(db.Date, default=datetime.utcnow().date(), nullable=False)
    heure_scan = db.Column(db.Time, default=datetime.utcnow().time(), nullable=False)
    
    # Relations pour l'accès direct aux objets
    point_acces = db.relationship('PointAcces', backref='presences', lazy=True)
    
    # Contrainte : Un étudiant ne peut être marqué présent qu'une seule fois par jour pour un auditoire (utile pour éviter les doubles scans)
    __table_args__ = (db.UniqueConstraint('etudiant_id', 'point_acces_id', 'date_presence', name='unique_presence_per_day_per_point'),)

    def __repr__(self):
        return f'<Presence {self.etudiant_id} - {self.date_presence}>'


# ===========================================
# 8. Table Absences (Générée par le Scheduler)
# ===========================================

class Absence(db.Model):
    __tablename__ = 'absences'
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False)
    date_absence = db.Column(db.Date, default=datetime.utcnow().date(), nullable=False, unique=True)
    justifiee = db.Column(db.Boolean, default=False, nullable=False)
    motif_justification = db.Column(db.Text, nullable=True)

    # Contrainte : Un étudiant ne peut être marqué absent qu'une seule fois par jour
    __table_args__ = (db.UniqueConstraint('etudiant_id', 'date_absence', name='unique_absence_per_day'),)

    def __repr__(self):
        return f'<Absence {self.etudiant_id} - {self.date_absence}>'

# Mise à jour de la relation dans Etudiant (Facultatif, mais propre)
# Dans la classe Etudiant, ajoutez:
# absences = db.relationship('Absence', backref='etudiant', lazy=True)