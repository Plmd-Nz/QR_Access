# app/routes/payement.py
from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import Etudiant, Paiement
from ..services.data_service import update_etudiant_solde
from .auth import jwt_required 
from datetime import datetime
from sqlalchemy.orm import joinedload
from decimal import Decimal

paiement_bp = Blueprint('paiement', __name__)

# ==========================================================
# UTILITAIRE DE SÉRIALISATION (Harmonisé avec le Modèle)
# ==========================================================
def paiement_to_dict(paiement):
    """ Sérialise l'objet Paiement en dictionnaire. """
    return {
        "id": paiement.id,
        "etudiant_id": paiement.etudiant_id,
        "matricule": paiement.etudiant.matricule if paiement.etudiant else None,
        "nom_etudiant": f"{paiement.etudiant.nom} {paiement.etudiant.prenom}" if paiement.etudiant else None,
        "montant": float(paiement.montant), # Utilise 'montant' du modèle
        "motif": paiement.motif,           # Utilise 'motif' du modèle
        "date_paiement": paiement.date_paiement.isoformat(),
        "annee_academique": paiement.annee_academique,
        "statut": paiement.statut
    }

# ==========================================================
# 1. ENREGISTRER UN PAIEMENT (POST)
# ==========================================================
@paiement_bp.route('/paiements', methods=['POST'])
def record_payment():
    data = request.get_json()
    
    # On accepte 'montant_paye' et 'description' venant du FRONT
    # mais on les transforme pour le MODÈLE
    required_fields = ['etudiant_id', 'montant_paye', 'description', 'annee_academique']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Champs manquants..."}), 400

    try:
        etudiant_id = int(data['etudiant_id'])
        valeur_montant = float(data['montant_paye'])
        texte_motif = data['description']
        annee = data['annee_academique']
    except (ValueError, TypeError):
        return jsonify({"message": "ID étudiant et/ou montant invalides."}), 400

    etudiant = Etudiant.query.get(etudiant_id)
    if not etudiant:
        return jsonify({"message": f"Étudiant non trouvé."}), 404
        
    if valeur_montant <= 0:
        return jsonify({"message": "Le montant doit être positif."}), 400
        
    try:
        # CORRECTION ICI : Utilisation des noms exacts du modèle (montant, motif)
        new_paiement = Paiement(
            etudiant_id=etudiant_id,
            montant=Decimal(str(valeur_montant)),
            motif=texte_motif,
            annee_academique=annee,
            date_paiement=datetime.utcnow().date(), # .date() car ton modèle est db.Date
            statut='valide' # On le force en valide à l'inscription directe
        )
        db.session.add(new_paiement)
        
        # Mise à jour du solde
        update_etudiant_solde(etudiant_id, valeur_montant) 
        
        db.session.commit()
        db.session.refresh(etudiant)
        
        return jsonify({
            "message": "Paiement enregistré avec succès.",
            "paiement_id": new_paiement.id,
            "nouveau_solde": str(etudiant.montant_total_paye)
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur: {e}")
        return jsonify({"message": f"Erreur serveur : {str(e)}"}), 500

# ==========================================================
# 2. LECTURE DE TOUS LES PAIEMENTS (GET)
# ==========================================================
@paiement_bp.route('/paiements', methods=['GET'])
def get_all_payments():
    try:
        paiements = Paiement.query.options(joinedload(Paiement.etudiant)).order_by(Paiement.date_paiement.desc()).all()
        result = [paiement_to_dict(p) for p in paiements]
        return jsonify({"total": len(result), "paiements": result}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# ==========================================================
# 4. MODIFICATION (PUT)
# ==========================================================
@paiement_bp.route('/paiements/<int:paiement_id>', methods=['PUT'])
def update_payment(paiement_id):
    data = request.get_json()
    try:
        paiement = Paiement.query.get(paiement_id)
        if not paiement:
            return jsonify({"message": "Paiement non trouvé."}), 404
        
        etudiant = Etudiant.query.get(paiement.etudiant_id)
        old_montant = float(paiement.montant)
        
        # Mapping FRONT -> MODÈLE
        if 'montant_paye' in data:
            new_valeur = float(data['montant_paye'])
            # Ajustement du solde étudiant
            etudiant.montant_total_paye = (float(etudiant.montant_total_paye) - old_montant) + new_valeur
            paiement.montant = new_valeur
            
        if 'description' in data:
            paiement.motif = data['description']
            
        if 'annee_academique' in data:
            paiement.annee_academique = data['annee_academique']

        db.session.commit()
        return jsonify({"message": "Mis à jour avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

# ==========================================================
# 5. SUPPRESSION (DELETE)
# ==========================================================
@paiement_bp.route('/paiements/<int:paiement_id>', methods=['DELETE'])
def delete_payment(paiement_id):
    try:
        paiement = Paiement.query.get(paiement_id)
        if not paiement:
            return jsonify({"message": "Paiement non trouvé."}), 404

        etudiant = Etudiant.query.get(paiement.etudiant_id)
        if etudiant:
            etudiant.montant_total_paye = max(0.0, float(etudiant.montant_total_paye) - float(paiement.montant))
            
        db.session.delete(paiement)
        db.session.commit()
        return jsonify({"message": "Supprimé"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500