# app/routes/admin_etudiant.py
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Etudiant, Faculte, Promotion
from ..services.data_service import generate_qr_code_key, generate_matricule , update_etudiant_solde
from ..services.photo_service import process_and_save_photo, generate_student_card
from ..services.email_service import send_student_card_email
import os
from .auth import jwt_required 
from sqlalchemy.orm import joinedload 
# Importation des utilitaires de sérialisation du fichier principal
from .serializers import etudiant_to_dict, Faculte, Promotion

admin_etudiant_bp = Blueprint('admin_etudiant', __name__)


# ==========================================================
# 1. ROUTE D'INSCRIPTION D'UN NOUVEL ÉTUDIANT (CRUD : Create)
#    POST /api/admin/etudiants
# ==========================================================

@admin_etudiant_bp.route('/etudiants', methods=['POST'])
#@jwt_required()s 
def create_student():
    """ Crée un nouvel étudiant, génère le matricule/QR code, traite la photo et envoie la carte par email. """
    # (Contenu de la Route 1 ici, en utilisant etudiant_to_dict_util)
    
    # ------------------ 1. Récupération et Validation des Données ------------------
    data = request.form
    required_fields = ['nom', 'postnom', 'prenom', 'genre', 'faculte_id', 'promotion_id', 'email']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Champs manquants. Veuillez fournir toutes les informations de l'étudiant."}), 400
    
    if 'photo' not in request.files:
        return jsonify({"message": "La photo de profil est requise."}), 400
    
    photo_file = request.files['photo']
    if photo_file.filename == '':
        return jsonify({"message": "Nom de fichier photo invalide."}), 400

    try:
        faculte_id = int(data['faculte_id'])
        promotion_id = int(data['promotion_id'])
        
        # ------------------ 2. Traitement du Fichier Photo ------------------
        # 1. On crée d'abord le nom de l'étudiant à partir des données reçues
        nom_pour_fichier = f"{data['nom']}_{data['postnom']}"
        
        # 2. On passe 'photo_file' ET 'nom_pour_fichier' à la fonction


        # --- TEST DE TAILLE RÉELLE ---
        photo_file.seek(0, os.SEEK_END) # On va à la fin du fichier
        taille_reelle = photo_file.tell() # On récupère la position (taille)
        photo_file.seek(0) # ON REVIENT AU DÉBUT (CRUCIAL pour la suite)
        
        print(f"DEBUG: Photo reçue: {photo_file.filename}, Taille Réelle: {taille_reelle} octets")
        # -----------------------------


        photo_path = process_and_save_photo(photo_file, nom_pour_fichier)
        

        if not photo_path:
            return jsonify({"message": "Échec du traitement de la photo (vérifier le format et la taille). Veuillez réessayer."}), 500

        # ------------------ 3. Génération des Identifiants ------------------
        qr_code_cle = generate_qr_code_key()
        matricule = generate_matricule(faculte_id)
        
        # ------------------ 4. Création de l'Entité Étudiant ------------------
        new_etudiant = Etudiant(
            matricule=matricule,
            nom=data['nom'],
            postnom=data['postnom'],
            prenom=data['prenom'],
            genre=data['genre'],
            faculte_id=faculte_id,
            promotion_id=promotion_id,
            email=data['email'],
            photo_path=photo_path,
            qr_code_cle=qr_code_cle,
            montant_total_paye=0.00 
        )
        
        db.session.add(new_etudiant)
        db.session.commit()
        
        # ------------------ 5. Génération et Envoi de la Carte ------------------
        etudiant_obj = Etudiant.query.get(new_etudiant.id)
        card_path = generate_student_card(etudiant_obj, photo_path, qr_code_cle)

        email_success = False
        if card_path:
            full_name = f"{etudiant_obj.nom} {etudiant_obj.postnom} {etudiant_obj.prenom}"
            email_success = send_student_card_email(etudiant_obj.email, full_name, card_path)

        # ------------------ 6. Réponse Finale ------------------
        return jsonify({
            "message": "Inscription réussie",
            "data": {
                "matricule": matricule,
                "nom_complet": f"{etudiant_obj.nom} {etudiant_obj.prenom}",
                "card_url": f"http://localhost:5000/{card_path}", # URL pour afficher l'image
                "email_sent": email_success
            }
        }), 201
        
        return jsonify({"message": "Inscription de l'étudiant réussie.", "data": response_data}), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur de conversion de données : {e}"}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur serveur lors de l'inscription : {e}")
        return jsonify({"message": f"Erreur interne du serveur lors de l'inscription : {e}"}), 500


# ==========================================================
# 2. ROUTE DE LECTURE DE TOUS LES ÉTUDIANTS (CRUD : Read All)
#    GET /api/admin/etudiants
# ==========================================================

@admin_etudiant_bp.route('/etudiants', methods=['GET'])
##@jwt_required()s 
def get_all_students():
    """ Récupère la liste de tous les étudiants. """
    try:
        etudiants = Etudiant.query.options(joinedload(Etudiant.faculte_obj), joinedload(Etudiant.promotion_obj)).all()
        result = [etudiant_to_dict(e) for e in etudiants]
        return jsonify({"total": len(result), "etudiants": result}), 200

    except Exception as e:
        current_app.logger.error(f"Erreur serveur lors de la récupération des étudiants : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la lecture des étudiants."}), 500


# ==========================================================
# 3. ROUTE DE LECTURE D'UN ÉTUDIANT PAR MATRICULE (CRUD : Read One)
#    GET /api/admin/etudiants/<matricule>
# ==========================================================

@admin_etudiant_bp.route('/etudiants/<string:matricule>', methods=['GET'])
#@jwt_required()s 
def get_student(matricule):
    """ Récupère les détails d'un étudiant par son matricule. """
    try:
        etudiant = Etudiant.query.options(joinedload(Etudiant.faculte_obj), joinedload(Etudiant.promotion_obj)).filter_by(matricule=matricule).first()
        
        if not etudiant:
            return jsonify({"message": f"Aucun étudiant trouvé avec le matricule {matricule}."}), 404
            
        return jsonify({"etudiant": etudiant_to_dict(etudiant)}), 200

    except Exception as e:
        current_app.logger.error(f"Erreur serveur lors de la récupération de l'étudiant {matricule} : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la lecture de l'étudiant."}), 500


# ==========================================================
# 4. ROUTE DE MODIFICATION D'UN ÉTUDIANT (CRUD : Update)
#    PUT /api/admin/etudiants/<matricule>
# ==========================================================

@admin_etudiant_bp.route('/etudiants/<string:matricule>', methods=['PUT'])
#@jwt_required()s 
def update_student(matricule):
    """ Met à jour les informations d'un étudiant par son matricule. """
    
    data = request.get_json()
    
    try:
        etudiant = Etudiant.query.filter_by(matricule=matricule).first()
        
        if not etudiant:
            return jsonify({"message": f"Aucun étudiant trouvé avec le matricule {matricule}."}), 404
        
        allowed_fields = [
            'nom', 'postnom', 'prenom', 'genre', 'email', 
            'faculte_id', 'promotion_id'
        ]
        
        changes = False
        for field in allowed_fields:
            if field in data:
                if field in ['faculte_id', 'promotion_id']:
                    new_id = int(data[field])
                    if field == 'faculte_id' and not Faculte.query.get(new_id):
                        return jsonify({"message": f"Faculté ID {new_id} non trouvée."}), 400
                    if field == 'promotion_id' and not Promotion.query.get(new_id):
                        return jsonify({"message": f"Promotion ID {new_id} non trouvée."}), 400
                        
                    setattr(etudiant, field, new_id)
                else:
                    setattr(etudiant, field, data[field])
                
                changes = True

        if changes:
            db.session.commit()
            return jsonify({
                "message": f"Informations de l'étudiant {matricule} mises à jour avec succès.",
                "nouveau_email": etudiant.email,
                "nouvelle_promotion_id": etudiant.promotion_id
            }), 200
        else:
            return jsonify({"message": "Aucune modification fournie ou champs invalides."}), 400

    except ValueError:
        db.session.rollback()
        return jsonify({"message": "Erreur de conversion : les IDs ou le format des données sont invalides."}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur serveur lors de la modification de {matricule} : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la modification."}), 500
    

# ==========================================================
# 5. ROUTE DE SUPPRESSION/DÉSACTIVATION D'UN ÉTUDIANT (CRUD : Delete)
#    DELETE /api/admin/etudiants/<matricule>
# ==========================================================

@admin_etudiant_bp.route('/etudiants/<string:matricule>', methods=['DELETE'])
#@jwt_required()s 
def delete_student(matricule):
    """ Supprime (physiquement) un étudiant et toutes ses données associées (paiements, accès, présence). """
    
    try:
        etudiant = Etudiant.query.filter_by(matricule=matricule).first()
        
        if not etudiant:
            return jsonify({"message": f"Aucun étudiant trouvé avec le matricule {matricule}."}), 404

        photo_path_to_delete = etudiant.photo_path
        
        db.session.delete(etudiant)
        db.session.commit()
        
        if photo_path_to_delete:
            full_path = os.path.join(current_app.root_path, photo_path_to_delete)
            if os.path.exists(full_path):
                os.remove(full_path)
                
        return jsonify({
            "message": f"L'étudiant avec le matricule {matricule} a été supprimé ainsi que toutes ses données (paiements, accès, présences)."
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur serveur lors de la suppression de {matricule} : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la suppression."}), 500

@admin_etudiant_bp.route('/etudiants/select', methods=['GET'])
#@jwt_required()
def get_students_for_selection():
    try:
        # 1. On récupère les étudiants
        etudiants = Etudiant.query.all()

        # 2. On construit la liste manuellement (plus simple pour déboguer)
        result = []
        for e in etudiants:
            result.append({
                "id": e.id,
                # Vérifie bien que .nom et .matricule existent dans ton modèle Etudiant
                "display_name": f"{getattr(e, 'matricule', 'N/A')} - {e.nom}"
            })

        return jsonify({"data": result}), 200

    except Exception as e:
        # C'est ici que l'erreur s'affiche dans ton terminal Flask !
        print(f"ERREUR BACK-END : {str(e)}") 
        return jsonify({"message": f"Erreur serveur : {str(e)}"}), 500