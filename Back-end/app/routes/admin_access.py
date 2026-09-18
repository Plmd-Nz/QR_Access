from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import Promotion, PointAcces
from .auth import jwt_required 
from sqlalchemy.orm import joinedload 

admin_access_bp = Blueprint('admin_access', __name__)

# Fonction de traduction locale pour adapter la BD au Front-end
def local_point_acces_to_dict(p):
    return {
        "id": p.id,
        "nom_point": p.nom,  # Front attend nom_point, BD a nom
        "type_acces": p.type_acces, 
        "promotion_id": p.promotion_cible_id, # Front attend promotion_id, BD a promotion_cible_id
        "promotion_nom": p.promotion.nom if (hasattr(p, 'promotion') and p.promotion) else None,
        "heure_debut": "08:00", # Valeurs par défaut car absentes du modèle
        "heure_fin": "17:00"
    }

# Mapping pour transformer les types du Front vers les ENUM de la BD
TYPE_MAPPING = {
    'CAMPUS': 'Principal',
    'AUDITOIRE': 'Cours',
    'SALLE_EXAMEN': 'Examen',
    'AUTRE': 'Laboratoire'
}

# ----------------------------------------------------------
# 11.1. CRÉATION D'UN POINT D'ACCÈS
# ----------------------------------------------------------
@admin_access_bp.route('/points_acces', methods=['POST'])
#@jwt_required()
def create_point_acces():
    data = request.get_json()
    
    # Validation des champs venant du Front
    if not data.get('nom_point') or not data.get('type_acces'):
        return jsonify({"message": "Le nom et le type sont requis."}), 400
    
    try:
        promo_id = data.get('promotion_id')
        if promo_id:
            if not Promotion.query.get(int(promo_id)):
                return jsonify({"message": "Promotion non trouvée."}), 404

        # Traduction du type Front vers ENUM BD
        type_db = TYPE_MAPPING.get(data['type_acces'].upper(), 'Principal')

        new_point = PointAcces(
            nom=data['nom_point'],
            type_acces=type_db,
            promotion_cible_id=promo_id
        )
        
        db.session.add(new_point)
        db.session.commit()
        
        return jsonify({
            "message": "Point d'Accès créé.", 
            "point_acces": local_point_acces_to_dict(new_point)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur: {str(e)}"}), 500

# ----------------------------------------------------------
# 11.2. LECTURE DE TOUS LES POINTS
# ----------------------------------------------------------
@admin_access_bp.route('/points_acces', methods=['GET'])
#@jwt_required()
def get_all_points_acces():
    try:
        # On utilise le nom de la relation définie dans ton modèle (souvent 'promotion')
        points = PointAcces.query.all() 
        result = [local_point_acces_to_dict(p) for p in points]
        return jsonify({"total": len(result), "points_acces": result}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la lecture : {str(e)}"}), 500

# ----------------------------------------------------------
# 11.3. MISE À JOUR
# ----------------------------------------------------------
@admin_access_bp.route('/points_acces/<int:point_id>', methods=['PUT'])
#@jwt_required()
def update_point_acces(point_id):
    data = request.get_json()
    point = PointAcces.query.get(point_id)

    if not point:
        return jsonify({"message": "Point non trouvé."}), 404

    try:
        # Adaptation dynamique des champs
        if 'nom_point' in data:
            point.nom = data['nom_point']
        
        if 'promotion_id' in data:
            point.promotion_cible_id = data['promotion_id']
            
        if 'type_acces' in data:
            point.type_acces = TYPE_MAPPING.get(data['type_acces'].upper(), point.type_acces)

        db.session.commit()
        return jsonify({
            "message": "Mis à jour avec succès.", 
            "point_acces": local_point_acces_to_dict(point)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur : {str(e)}"}), 500

# ----------------------------------------------------------
# 11.4. SUPPRESSION
# ----------------------------------------------------------
@admin_access_bp.route('/points_acces/<int:point_id>', methods=['DELETE'])
#@jwt_required()
def delete_point_acces(point_id):
    point = PointAcces.query.get(point_id)
    if not point:
        return jsonify({"message": "Point non trouvé."}), 404
        
    try:
        db.session.delete(point)
        db.session.commit()
        return jsonify({"message": "Supprimé avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erreur : Ce point est probablement lié à des historiques."}), 409