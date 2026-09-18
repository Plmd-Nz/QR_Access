# app/config.py

import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    # 1. Clé Secrète Flask (ESSENTIELLE pour la sécurité des sessions)
    SECRET_KEY = os.getenv("SECRET_KEY", "cle_dev_qr_access")
    
    # 2. Configuration de la Base de Données MySQL
    # Structure: 'mysql+pymysql://utilisateur:mot_de_passe@hote/nom_base_de_donnees'
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. Configuration des Photos
    # Chemin absolu où seront stockées les photos traitées des étudiants
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'photos')
    # Taille maximale des fichiers (Exemple: 2 Mo)
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 

    # 4. Configuration Flask-APScheduler (Tâches planifiées)
    SCHEDULER_API_ENABLED = True
    SCHEDULER_JOBSTORES = {
        'default': {'type': 'memory'} # Stockage des jobs en mémoire pour ce projet
    }
    # Configuration de la tâche de marquage des absents (à 17h01)
    ABSENT_MARK_HOUR = 17
    ABSENT_MARK_MINUTE = 1
    
    # 5. Règle de Présence (Seuil pour les paiements - à définir)
    # Montant minimum requis pour l'accès aux activités académiques (à titre d'exemple)
    PAIEMENT_SEUIL_MINIMUM = 586.00 
    
    # Durée de la session admin avant déconnexion automatique
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

# app/config.py (Ajouter ces lignes)


# Configuration Flask-Mail
MAIL_SERVER = 'smtp.gmail.com' # Ou votre serveur SMTP (Orange, etc.)
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.getenv("MAIL_USERNAME") # Le compte émetteur
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CLIPDROP_API_KEY = os.getenv("CLIPDROP_API_KEY")