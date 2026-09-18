# app/__init__.py

from flask import Flask , jsonify
from .config import Config
from .extensions import db, bcrypt, scheduler, mail
import os
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv


# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"]
        }},
        supports_credentials=True
        )

    # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # Configuration du dossier d'upload si non existant
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
# =========================================================
    # CONFIGURATION ET INITIALISATION DE FLASK-JWT-EXTENDED
    # =========================================================
    
    # 1. Configuration de la clé secrète et de l'expiration
    # IMPORTANT : Remplacez cette clé par une longue chaîne aléatoire et sécurisée
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') 
    app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY') 
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) # Token expire après 1 heure
    
    # 2. Initialisation de l'instance JWT
    jwt = JWTManager(app)

    # 3. Gestion des erreurs JWT (Pour retourner une réponse JSON claire au Frontend)
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"message": "Token JWT manquant ou non fourni.", "logged_in": False}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Le jeton d'accès a expiré. Veuillez vous reconnecter.", "logged_in": False}), 401
    
    # Optionnel : Gestionnaire pour un jeton invalide (signature incorrecte)
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({"message": "Le jeton d'accès est invalide.", "logged_in": False}), 401

    # ===========================================
    # Enregistrement des Blueprints (Routes API)
    # ===========================================
    
    # Importation des Blueprints
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.scan import scan_bp
    from .routes.main import main_bp

    # Enregistrement
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(scan_bp, url_prefix='/api/scan')
    app.register_blueprint(main_bp, url_prefix='/')

    # ===========================================
    # Tâches Planifiées (Scheduler)
    # ===========================================
    
    # Le scheduler ne doit être lancé qu'une fois
    if app.config['SCHEDULER_API_ENABLED']:
        scheduler.init_app(app)
        # Importation et ajout des tâches (nous le ferons après avoir défini la logique)
        from .services.data_service import mark_absents_daily 
        # Ajout de la tâche: Exécution quotidienne à l'heure et minute définies dans config.py
        scheduler.add_job(
            id='mark_absents', 
            func=mark_absents_daily,
            # Le job doit être passé avec l'application pour accéder au contexte (db.session)
            args=(app,), 
            trigger='cron', 
            hour=app.config['ABSENT_MARK_HOUR'], 
            minute=app.config['ABSENT_MARK_MINUTE'] # 17h01
        )
        
        # Lance le scheduler après le contexte de l'application
        if not scheduler.running: # S'assurer qu'il ne démarre qu'une fois
            scheduler.start()


    return app