# app/routes/scan.py

from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models import Etudiant, PointAcces, RegistreAcces, Presence
from datetime import datetime, date, time
import os
from sqlalchemy.orm import joinedload
from .serializers import paiement_to_dict
from .serializers import point_acces_to_dict

scan_bp = Blueprint('scan', __name__)

# ==========================================================
# 1. ROUTE DE LISTE DES POINTS D'ACCÈS (POUR CONFIGURATION)
#    GET /api/scan/points_acces
# ==========================================================
@scan_bp.route('/points_acces', methods=['GET'])
def get_points_acces():
    """
    Retourne la liste complète des points d'accès disponibles.
    Utilisé par le terminal de scan pour sélectionner sa position.
    """
    try:
        # 1. Récupérer tous les points d'accès, triés par nom
        points = PointAcces.query.order_by(PointAcces.nom).all()
        
        # 2. Sérialisation simple des données
        points_list = [{
            'id': p.id,
            'nom': p.nom,
            'type_acces': p.type_acces,
            # Le promotion_cible_id n'est pas critique pour le Front-end ici
        } for p in points]
        
        return jsonify({
            "message": "Liste des points d'accès récupérée avec succès.",
            "data": points_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des points d'accès: {e}")
        return jsonify({"message": f"Erreur interne du serveur lors de la récupération des points d'accès: {e}"}), 500


# ==========================================================
# 2. ROUTE DE RÉCUPÉRATION DES SCANS RÉCENTS (POUR AFFICHAGE)
#    GET /api/scan/recent
# ==========================================================
@scan_bp.route('/recent', methods=['GET'])
def get_recent_scans():
    """
    Retourne les 10 derniers enregistrements du Registre d'Accès.
    Utilisé par l'interface de Scan pour afficher l'historique en temps réel.
    """
    try:
        # 1. Récupérer les 10 derniers enregistrements, chargeant les relations d'un coup (joinedload)
        recent_registres = RegistreAcces.query.options(
            # Charger l'étudiant et sa promotion associée
            joinedload(RegistreAcces.etudiant).joinedload(Etudiant.promotion_obj), 
            # Charger le point d'accès
            joinedload(RegistreAcces.point_acces) 
        ).order_by(
            RegistreAcces.timestamp.desc()
        ).limit(10).all()
        
        scans_list = []
        for reg in recent_registres:
            etudiant_info = None
            
            # Les objets sont déjà chargés, pas de requête supplémentaire en base de données
            if reg.etudiant:
                # Assurez-vous que la relation 'promotion_obj' existe sur votre modèle Etudiant
                promotion_nom = reg.etudiant.promotion_obj.nom if reg.etudiant.promotion_obj else 'N/A'
                
                etudiant_info = {
                    'matricule': reg.etudiant.matricule,
                    'nom_complet': f"{reg.etudiant.nom} {reg.etudiant.postnom} {reg.etudiant.prenom}",
                    'promotion': promotion_nom
                }
                
            point_acces_nom = reg.point_acces.nom if reg.point_acces else 'Inconnu'
            
            scans_list.append({
                'id': reg.id,
                'timestamp': reg.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
                'statut': reg.statut,
                'raison_refus': reg.raison_refus,
                'point_acces_nom': point_acces_nom,
                'etudiant': etudiant_info
            })
            
        return jsonify({
            "message": "Historique des scans récupéré et optimisé.",
            "data": scans_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des scans récents: {e}")
        return jsonify({"message": f"Erreur interne du serveur lors de la récupération des scans récents: {e}"}), 500

# ==========================================================
# ROUTE DE VALIDATION D'ACCÈS ET DE PRÉSENCE
# POST /api/scan
# ==========================================================

@scan_bp.route('/', methods=['POST'])
def scan_qr_code():
    """ 
    Gère la tentative de scan d'un étudiant à un point d'accès.
    Applique les règles de paiement et de présence stricte.
    """
    
    
    
    # ------------------ 0. RÈGLES DE TEMPS (Avant toute recherche BDD) ------------------
    data = request.get_json()
    current_dt = datetime.now()
    
    # 0.1. Règle du Dimanche
    if current_dt.weekday() == 6: # Le 6 correspond au dimanche (lundi=0, dimanche=6)
        raison_refus = "L'enregistrement des présences est désactivé le Dimanche."
        # Note: Nous n'avons pas d'ID d'étudiant ici, car nous voulons échouer le plus tôt possible
        # On suppose ici que qr_code_cle et point_acces_id sont disponibles dans data pour l'appel à _finalize_scan_transaction
        qr_code_cle = data.get('qr_code_cle')
        point_acces_id = data.get('point_acces_id')
        return _finalize_scan_transaction(qr_code_cle, point_acces_id, 'refuse', raison_refus)

    # 0.2. Règle de l'Heure Limite (si nous voulons bloquer le scan académique après 17h00)
    
    # Récupérer l'heure limite depuis la configuration
    mark_hour = current_app.config['ABSENT_MARK_HOUR'] 
    
    if current_dt.hour >= mark_hour:
        # Si c'est après 17h00, on refuse l'accès pour la présence
        raison_refus = "L'heure limite de scan (17h00) est dépassée. Accès refusé pour la présence."
        # On suppose ici que qr_code_cle et point_acces_id sont disponibles dans data pour l'appel à _finalize_scan_transaction
        qr_code_cle = data.get('qr_code_cle')
        point_acces_id = data.get('point_acces_id')
        return _finalize_scan_transaction(qr_code_cle, point_acces_id, 'refuse', raison_refus)
    

    # ------------------ 1. Récupération des Données ------------------
    
    required_fields = ['qr_code_cle', 'point_acces_id']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Données de scan incomplètes (clé QR et ID d'accès requis)."}), 400
    
    qr_code_cle = data['qr_code_cle']
    point_acces_id = data['point_acces_id']
    
    # Initialisation des variables de transaction
    statut_acces = 'refuse'
    raison_refus = None
    etudiant = None
    point_acces = None

    try:
        # Récupération de l'entité Étudiant (ultra-rapide par clé unique)
        etudiant = Etudiant.query.filter_by(qr_code_cle=qr_code_cle).first()
        if not etudiant:
            raison_refus = "Clé QR code non reconnue ou désactivée."
            return _finalize_scan_transaction(qr_code_cle, point_acces_id, 'refuse', raison_refus)

        # Récupération du Point d'Accès
        point_acces = PointAcces.query.get(point_acces_id)
        if not point_acces:
            raison_refus = "Point d'accès non configuré."
            return _finalize_scan_transaction(qr_code_cle, point_acces_id, 'refuse', raison_refus)

        # ------------------ 2. Règle Critique : Vérification du Paiement ------------------
        
        # Le seuil de paiement est défini dans app/config.py
        seuil_minimum = current_app.config['PAIEMENT_SEUIL_MINIMUM']
        
        if etudiant.montant_total_paye < seuil_minimum:
            if point_acces.type_acces == 'Examen':
             statut_acces = 'refuse'
             # Le refus est ferme pour tous les types d'accès si le seuil n'est pas atteint
            
             raison_refus = f"Paiement insuffisant. Solde : {etudiant.montant_total_paye} / Seuil : {seuil_minimum}."
             return _finalize_scan_transaction(qr_code_cle, point_acces_id, statut_acces, raison_refus, etudiant.id, point_acces.id)

        # ------------------ 3. Accès AUTORISÉ (Paiement OK) ------------------
        
        statut_acces = 'autorise'
        
        # ------------------ 4. Règle de Présence (Validation Académique) ------------------
        
        is_presence_validated = False
        
        # Règle : La présence n'est validée que si c'est un point 'Cours' ET que c'est l'auditoire de sa promotion
        if point_acces.type_acces == 'Cours':
            
            # Vérification de la règle stricte : Etudiant est-il dans son auditoire attitré ?
            if etudiant.promotion_id == point_acces.promotion_cible_id:
                
                # Double-scan check (empêche la tricherie par re-scan du même point le même jour)
                existing_presence = Presence.query.filter_by(
                    etudiant_id=etudiant.id, 
                    point_acces_id=point_acces.id, 
                    date_presence=date.today()
                ).first()

                if not existing_presence:
                    # Enregistrement de la Présence Académique (Succès)
                    new_presence = Presence(
                        etudiant_id=etudiant.id,
                        point_acces_id=point_acces.id,
                        date_presence=date.today(),
                        heure_scan=datetime.now().time()
                    )
                    db.session.add(new_presence)
                    is_presence_validated = True
                else:
                    # L'accès est toujours autorisé, mais la présence n'est pas enregistrée deux fois
                    current_app.logger.info(f"Double scan détecté pour {etudiant.matricule} à {point_acces.nom}.")
            else:
                # Accès autorisé, mais non compté comme présence académique (Règle stricte)
                current_app.logger.info(f"Accès autorisé mais non compté comme présence pour {etudiant.matricule} (scan à {point_acces.nom}).")

        # ------------------ 5. Finalisation de la Transaction (Registre d'Accès) ------------------

        # Enregistre le passage, qu'il y ait eu validation de présence ou non
        response = _finalize_scan_transaction(qr_code_cle, point_acces_id, statut_acces, raison_refus, etudiant.id, point_acces.id)

        # ------------------ 6. Construction de la Réponse pour le Frontend ------------------

        response_data = {
            "statut_acces": statut_acces,
            "message": f"ACCÈS AUTORISÉ à {point_acces.nom}." + (" PRÉSENCE VALIDÉE." if is_presence_validated else ""),
            "matricule": etudiant.matricule,
            "nom_complet": f"{etudiant.nom} {etudiant.postnom} {etudiant.prenom}",
            "promotion": etudiant.promotion_obj.nom,
            "photo_path": etudiant.photo_path # Affichage immédiat de la photo de profil
        }
        
        return jsonify({"success": True, "data": response_data}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur serveur lors du scan: {e}")
        # Enregistrement d'une tentative refusée due à une erreur interne
        return _finalize_scan_transaction(qr_code_cle, point_acces_id, 'refuse', f"Erreur interne du serveur: {e}")


def _finalize_scan_transaction(qr_code_cle, point_acces_id, statut, raison, etudiant_id=None, point_acces_id_int=None):
    """ Fonction utilitaire pour enregistrer le Registre d'Accès et commit la transaction. """
    
    # 1. Tenter d'obtenir les IDs si non fournis (pour les erreurs avant le fetch)
    if etudiant_id is None:
        etudiant = Etudiant.query.filter_by(qr_code_cle=qr_code_cle).first()
        if etudiant: etudiant_id = etudiant.id
    
    try:
        point_acces_id_int = int(point_acces_id)
    except:
        point_acces_id_int = None # ID invalide si l'erreur arrive très tôt

    # 2. Enregistrement dans le Registre (essentiel pour la traçabilité !)
    new_registre = RegistreAcces(
        etudiant_id=etudiant_id, # Peut être NULL si étudiant non trouvé
        point_acces_id=point_acces_id_int,
        timestamp=datetime.utcnow(),
        statut=statut,
        raison_refus=raison
    )
    
    db.session.add(new_registre)
    db.session.commit()
    
    # 3. Retour en cas de Refus
    if statut == 'refuse':
        response_data = {
            "statut_acces": statut,
            "message": raison
        }
        return jsonify({"success": False, "data": response_data}), 403 # 403 Forbidden
    
    # Si statut est 'autorise', le code principal doit continuer pour construire la réponse complète
    return None # Retourne None si l'enregistrement a réussi et que l'accès est autorisé