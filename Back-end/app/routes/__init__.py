# app/routes/__init__.py (CORRIGÉ)

from .admin import admin_bp
from .scan import scan_bp
from .auth import auth_bp
from .main import main_bp
from .paiement import paiement_bp

def register_blueprints(app):
    """ Enregistre tous les Blueprints (modules de routes) à l'application Flask. """
    
    # Routes API
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Ceci permet de conserver l'URL /api/admin/paiements tout en séparant le code.
    #app.register_blueprint(paiement_bp, url_prefix='/api/admin')

    # CORRECTION : 'scan' au lieu de 'scan'
    app.register_blueprint(scan_bp, url_prefix='/api/scan') 
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth') 
    
    # Route racine (accueil)
    app.register_blueprint(main_bp, url_prefix='/')
    
    