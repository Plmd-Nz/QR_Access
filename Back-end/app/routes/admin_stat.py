# app/routes/admin_finance.py
from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import Paiement, Presence, Faculte , Etudiant, Promotion, PointAcces
from ..services.data_service import update_etudiant_solde
from .auth import jwt_required 
from sqlalchemy import func
from datetime import datetime
# Importation des utilitaires de sérialisation
from .serializers import paiement_to_dict

admin_stat_bp = Blueprint('admin_stat', __name__)

# ==========================================================
# 12. ROUTE DU TABLEAU DE BORD (STATS & OVERVIEW)
#     GET /api/admin/dashboard_stats
# (Cette route était la cause de votre problème CORS/404)
# ==========================================================

@admin_stat_bp.route('/dashboard_stats', methods=['GET', 'OPTIONS'])
# @jwt_required()
def dashboard_stats():
    """ 
    Récupère les statistiques clés pour le tableau de bord :
    Total étudiants, total facultés, total paiements, étudiants du jour, etc.
    """
    
    # ------------------ 1. Gestion du Preflight OPTIONS (Optionnel si Flask-CORS est bien configuré) ------------------
    if request.method == 'OPTIONS':
        # Répondre positivement à la requête OPTIONS pour débloquer le GET
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response, 200

    # ------------------ 2. Calcul des Statistiques (GET) ------------------
    try:
        
        # A. Totaux Statiques
        total_etudiants = db.session.query(Etudiant).count()
        total_facultes = db.session.query(Faculte).count()
        total_promotions = db.session.query(Promotion).count()
        total_points_acces = db.session.query(PointAcces).count() # Assurez-vous d'importer PointAcces si nécessaire

        # B. Statistiques Financières
        total_paiements = db.session.query(func.sum(Paiement.montant)).scalar() or 0.00
        
        # C. Statistiques du Jour
        today = datetime.now().date()
        
        presences_du_jour = db.session.query(Presence).filter(
            Presence.date_presence == today 
        ).count()
        
        paiements_du_jour = db.session.query(func.sum(Paiement.montant)).filter(
            func.DATE(Paiement.date_paiement) == today
        ).scalar() or 0.00
        
        # D. Top 5 des Facultés par nombre d'Étudiants
        top_facultes = db.session.query(
            Faculte.nom, 
            func.count(Etudiant.id).label('total_etudiants')
        ).join(Etudiant, Etudiant.faculte_id == Faculte.id).group_by(Faculte.nom).order_by(
            func.count(Etudiant.id).desc()
        ).limit(5).all()

        
        return jsonify({
            "message": "Statistiques du tableau de bord récupérées avec succès.",
            "stats": {
                "total_etudiants": total_etudiants,
                "total_facultes": total_facultes,
                "total_promotions": total_promotions,
                "total_points_acces": total_points_acces,
                "total_paiements_usd": str(total_paiements),
                "presences_du_jour": presences_du_jour,
                "paiements_du_jour_usd": str(paiements_du_jour),
                "top_facultes_etudiants": [{
                    "nom": nom,
                    "count": count
                } for nom, count in top_facultes]
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Erreur serveur lors de la récupération des stats : {e}")
        return jsonify({"message": "Erreur interne lors de la récupération des statistiques."}), 500