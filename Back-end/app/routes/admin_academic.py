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
from .serializers import Faculte, Promotion , faculte_to_dict, promotion_to_dict

admin_academic_bp = Blueprint('admin_academic', __name__)


# ==========================================================
# GESTION DES FACULTÉS (CRUD : 9.x)
# ==========================================================

# ----------------------------------------------------------
# 9.1. CRÉATION D'UNE FACULTÉ (Create)
#    POST /api/admin/facultes
# ----------------------------------------------------------

@admin_academic_bp.route('/facultes', methods=['POST'])
#@jwt_required()
def create_faculte():
    data = request.get_json()
    if not data or 'nom' not in data or 'code_court' not in data:
        return jsonify({"message": "Nom et code_court de la faculté sont requis."}), 400
    
    try:
        new_faculte = Faculte(
            nom=data['nom'],
            code_court=data['code_court'].upper()
        )
        db.session.add(new_faculte)
        db.session.commit()
        return jsonify({"message": "Faculté créée avec succès.", "faculte": faculte_to_dict(new_faculte)}), 201
    
    except Exception as e:
        db.session.rollback()
        # Gérer l'erreur de duplication (nom ou code_court déjà existant)
        if 'IntegrityError' in str(type(e)):
            return jsonify({"message": "Erreur: Le nom ou le code court de cette faculté existe déjà."}), 409
        current_app.logger.error(f"Erreur serveur lors de la création de faculté : {e}")
        return jsonify({"message": f"Erreur interne du serveur : {e}"}), 500


# ----------------------------------------------------------
# 9.2. LECTURE DE TOUTES LES FACULTÉS (Read All)
#    GET /api/admin/facultes
# ----------------------------------------------------------

@admin_academic_bp.route('/facultes', methods=['GET'])
#@jwt_required()
def get_all_facultes():
    try:
        # Utiliser joinedload(Faculte.promotions) pour le décompte des promotions
        facultes = Faculte.query.all()
        result = [faculte_to_dict(f) for f in facultes]
        return jsonify({"total": len(result), "facultes": result}), 200
    
    except Exception as e:
        current_app.logger.error(f"Erreur serveur lors de la lecture des facultés : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la lecture des facultés."}), 500


# ----------------------------------------------------------
# 9.3. MISE À JOUR D'UNE FACULTÉ (Update)
#    PUT /api/admin/facultes/<int:faculte_id>
# ----------------------------------------------------------

@admin_academic_bp.route('/facultes/<int:faculte_id>', methods=['PUT'])
#@jwt_required()
def update_faculte(faculte_id):
    data = request.get_json()
    faculte = Faculte.query.get(faculte_id)

    if not faculte:
        return jsonify({"message": f"Faculté ID {faculte_id} non trouvée."}), 404

    changes = False
    try:
        if 'nom' in data and data['nom'] != faculte.nom:
            faculte.nom = data['nom']
            changes = True
        
        if 'code_court' in data and data['code_court'].upper() != faculte.code_court:
            faculte.code_court = data['code_court'].upper()
            changes = True

        if changes:
            db.session.commit()
            return jsonify({"message": "Faculté mise à jour avec succès.", "faculte": faculte_to_dict(faculte)}), 200
        else:
            return jsonify({"message": "Aucune modification fournie."}), 400

    except Exception as e:
        db.session.rollback()
        if 'IntegrityError' in str(type(e)):
            return jsonify({"message": "Erreur: Le nom ou le code court de cette faculté existe déjà."}), 409
        current_app.logger.error(f"Erreur serveur lors de la mise à jour de faculté : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la mise à jour."}), 500


# ----------------------------------------------------------
# 9.4. SUPPRESSION D'UNE FACULTÉ (Delete)
#    DELETE /api/admin/facultes/<int:faculte_id>
# ----------------------------------------------------------

@admin_academic_bp.route('/facultes/<int:faculte_id>', methods=['DELETE'])
#@jwt_required()
def delete_faculte(faculte_id):
    faculte = Faculte.query.get(faculte_id)

    if not faculte:
        return jsonify({"message": f"Faculté ID {faculte_id} non trouvée."}), 404
        
    try:
        db.session.delete(faculte)
        db.session.commit()
        return jsonify({"message": f"La faculté '{faculte.nom}' a été supprimée avec succès."}), 200

    except Exception as e:
        db.session.rollback()
        # Gérer la contrainte de clé étrangère (ondelete='RESTRICT')
        if 'IntegrityError' in str(type(e)): 
            return jsonify({
                "message": "Suppression impossible.",
                "detail": "Cette faculté est encore liée à une ou plusieurs promotions. Veuillez supprimer les promotions associées avant de supprimer la faculté."
            }), 409
        current_app.logger.error(f"Erreur serveur lors de la suppression de faculté : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la suppression."}), 500


# ==========================================================
# GESTION DES PROMOTIONS (CRUD : 10.x)
# ==========================================================

# ----------------------------------------------------------
# 10.1. CRÉATION D'UNE PROMOTION (Create)
#    POST /api/admin/promotions
# ----------------------------------------------------------

@admin_academic_bp.route('/promotions', methods=['POST'])
#@jwt_required()
def create_promotion():
    data = request.get_json()
    required_fields = ['faculte_id', 'nom', 'filiere']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Les champs faculte_id, nom et filiere sont requis."}), 400
    
    try:
        faculte_id = int(data['faculte_id'])
        
        # Vérification de l'existence de la faculté
        faculte = Faculte.query.get(faculte_id)
        if not faculte:
             return jsonify({"message": f"Faculté ID {faculte_id} non trouvée."}), 404

        new_promotion = Promotion(
            faculte_id=faculte_id,
            nom=data['nom'],
            filiere=data.get('filiere')
        )
        db.session.add(new_promotion)
        db.session.commit()
        return jsonify({"message": "Promotion créée avec succès.", "promotion": promotion_to_dict(new_promotion)}), 201
    
    except ValueError:
        return jsonify({"message": "L'ID de la faculté doit être un nombre entier valide."}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur serveur lors de la création de promotion : {e}")
        return jsonify({"message": f"Erreur interne du serveur : {e}"}), 500


# ----------------------------------------------------------
# 10.2. LECTURE DE TOUTES LES PROMOTIONS (Read All)
#    GET /api/admin/promotions
# ----------------------------------------------------------

@admin_academic_bp.route('/promotions', methods=['GET'])
#@jwt_required()
def get_all_promotions():
    try:
        # Optimisation : Charger la relation 'faculte' en même temps
        promotions = Promotion.query.options(joinedload(Promotion.faculte)).all() 
        result = [promotion_to_dict(p) for p in promotions]
        return jsonify({"total": len(result), "promotions": result}), 200
    
    except Exception as e:
        current_app.logger.error(f"Erreur serveur lors de la lecture des promotions : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la lecture des promotions."}), 500


# ----------------------------------------------------------
# 10.3. MISE À JOUR D'UNE PROMOTION (Update)
#    PUT /api/admin/promotions/<int:promotion_id>
# ----------------------------------------------------------

@admin_academic_bp.route('/promotions/<int:promotion_id>', methods=['PUT'])
#@jwt_required()
def update_promotion(promotion_id):
    data = request.get_json()
    promotion = Promotion.query.get(promotion_id)

    if not promotion:
        return jsonify({"message": f"Promotion ID {promotion_id} non trouvée."}), 404

    changes = False
    try:
        # Mise à jour des champs autorisés
        allowed_fields = ['nom', 'filiere', 'faculte_id']
        
        for field in allowed_fields:
            if field in data:
                if field == 'faculte_id':
                    new_faculte_id = int(data[field])
                    # Vérifier si la nouvelle faculté existe
                    if not Faculte.query.get(new_faculte_id):
                        return jsonify({"message": f"Faculté ID {new_faculte_id} non trouvée."}), 404
                    setattr(promotion, field, new_faculte_id)
                else:
                    setattr(promotion, field, data[field])
                changes = True

        if changes:
            db.session.commit()
            # Recharger pour avoir le nom de la faculté mis à jour
            updated_promotion = Promotion.query.options(joinedload(Promotion.faculte)).get(promotion_id) 
            return jsonify({"message": "Promotion mise à jour avec succès.", "promotion": promotion_to_dict(updated_promotion)}), 200
        else:
            return jsonify({"message": "Aucune modification fournie."}), 400

    except ValueError:
        db.session.rollback()
        return jsonify({"message": "Erreur de conversion : l'ID de la faculté doit être un entier."}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur serveur lors de la mise à jour de promotion : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la mise à jour."}), 500


# ----------------------------------------------------------
# 10.4. SUPPRESSION D'UNE PROMOTION (Delete)
#    DELETE /api/admin/promotions/<int:promotion_id>
# ----------------------------------------------------------

@admin_academic_bp.route('/promotions/<int:promotion_id>', methods=['DELETE'])
#@jwt_required()
def delete_promotion(promotion_id):
    promotion = Promotion.query.get(promotion_id)

    if not promotion:
        return jsonify({"message": f"Promotion ID {promotion_id} non trouvée."}), 404
        
    try:
        db.session.delete(promotion)
        db.session.commit()
        return jsonify({"message": f"La promotion '{promotion.nom}' a été supprimée avec succès."}), 200

    except Exception as e:
        db.session.rollback()
        # Gérer la contrainte de clé étrangère (Étudiant ou PointAcces est lié)
        if 'IntegrityError' in str(type(e)):
            return jsonify({
                "message": "Suppression impossible.",
                "detail": "Cette promotion est encore liée à des étudiants ou des points d'accès. Veuillez supprimer ou réaffecter les entités liées avant de supprimer cette promotion."
            }), 409
        current_app.logger.error(f"Erreur serveur lors de la suppression de promotion : {e}")
        return jsonify({"message": "Erreur interne du serveur lors de la suppression."}), 500

