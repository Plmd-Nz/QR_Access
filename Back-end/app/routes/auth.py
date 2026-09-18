# app/routes/auth.py

from flask import Blueprint, request, jsonify, current_app
from ..models import Administrateur
from ..extensions import bcrypt, db
from functools import wraps

# Importation des fonctions Flask-JWT-Extended
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies

auth_bp = Blueprint('auth', __name__)

# ==========================================================
# UTILITAIRE CRITIQUE : DÉCORATEUR D'AUTHENTIFICATION (OBSOLÈTE)
# ==========================================================

# NOTE IMPORTANTE : Le décorateur 'login_required' basé sur la session 
# n'est plus utilisé. Nous utilisons désormais '@jwt_required()' de Flask-JWT-Extended.
# Il est laissé ici, commenté, pour référence ou suppression future, mais ne sera pas appelé.
# def login_required(f):
#     """ 
#     Décorateur personnalisé pour s'assurer que l'utilisateur est connecté
#     avant d'accéder à une route. (Ancienne version basée sur la session)
#     """
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'admin_id' not in session:
#             return jsonify({"message": "Accès non autorisé. Veuillez vous connecter."}), 401
        
#         admin = Administrateur.query.get(session['admin_id'])
#         if not admin:
#             session.pop('admin_id', None)
#             return jsonify({"message": "Accès non autorisé. Utilisateur introuvable."}), 401
            
#         return f(*args, **kwargs)
#     return decorated_function


# ==========================================================
# 1. ROUTE DE CONNEXION (Login) - MISE À JOUR JWT
#    POST /api/auth/login
# ==========================================================
@auth_bp.route('/login', methods=['POST'])
def login():

    print("HEADERS:", request.headers)
    print("JSON:", request.get_json())

    data = request.get_json()
    nom_utilisateur = data.get('nom_utilisateur')
    mot_de_passe = data.get('mot_de_passe')

    if not nom_utilisateur or not mot_de_passe:
        return jsonify({"message": "Nom d'utilisateur et mot de passe requis."}), 400

    # 1. Récupération de l'utilisateur
    admin = Administrateur.query.filter_by(nom_utilisateur=nom_utilisateur).first()

    # 2. Vérification du mot de passe haché (Bcrypt)
    if admin and bcrypt.check_password_hash(admin.mot_de_passe_hash, mot_de_passe):
        
        # 3. Authentification réussie : CRÉATION ET ENVOI DU JETON JWT
        # L'identité du jeton est l'ID de l'administrateur
        access_token = create_access_token(identity=admin.id)
        
        return jsonify({
            "message": "Connexion réussie.", 
            "admin_name": admin.nom_complet,
            "access_token": access_token  # <--- C'est ici que le Frontend récupère le token
        }), 200
    else:
        # 4. Échec de l'authentification
        return jsonify({"message": "Nom d'utilisateur ou mot de passe invalide."}), 401

# ==========================================================
# 2. ROUTE DE DÉCONNEXION (Logout) - MISE À JOUR JWT
#    POST /api/auth/logout
# ==========================================================
@auth_bp.route('/logout', methods=['POST'])
#@jwt_required() # Vérifie la validité du jeton AVANT d'exécuter la fonction
def logout():
    # La déconnexion côté JWT se fait en demandant au client de supprimer le token.
    # Le token est désormais invalide s'il n'est plus envoyé.
    
    # Si le token était dans les cookies (avec Flask-JWT-Extended), on ferait :
    # response = jsonify({"message": "Déconnexion réussie."})
    # unset_jwt_cookies(response)
    # return response
    
    # Pour votre configuration (Frontend gère le localStorage), un message de succès suffit.
    return jsonify({"message": "Déconnexion réussie."}), 200


# ==========================================================
# 3. ROUTE DE STATUT DE CONNEXION (Utile pour le Frontend) - MISE À JOUR JWT
#    GET /api/auth/status
# ==========================================================
@auth_bp.route('/status', methods=['GET'])
#@jwt_required(optional=True) # Permet l'accès même sans jeton, mais vérifie s'il y en a un
def status():
    """ Vérifie si le jeton fourni est valide. """
    current_admin_id = get_jwt_identity()
    
    if current_admin_id:
        # Un jeton valide a été trouvé
        admin = Administrateur.query.get(current_admin_id)
        if admin:
            return jsonify({
                "logged_in": True,
                "admin_name": admin.nom_complet
            }), 200
            
    # Pas de jeton valide ou utilisateur supprimé
    return jsonify({"logged_in": False}), 200