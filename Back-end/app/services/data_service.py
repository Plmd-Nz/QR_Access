# app/services/data_service.py (MISE À JOUR)

from flask import  current_app
from ..models import Etudiant, Faculte
from ..extensions import db
import uuid
from ..models import Etudiant, Faculte, Absence, Presence # IMPORTER ABSENCE ET PRESENCE
from datetime import datetime, date # Assurez-vous d'importer 'date'
from decimal import Decimal

# ==========================================================
# 1. Génération de la clé unique (QR Code)
# ==========================================================
def generate_qr_code_key():
    """ Génère une clé unique non prédictible pour le QR code. """
    return str(uuid.uuid4()).replace('-', '') 

# ==========================================================
# 2. Génération du Matricule UCB-[CODE]-[NNNN] (SIMPLIFIÉ)
# ==========================================================
def generate_matricule(faculte_id):
    """
    Génère le matricule selon le format UCB-[CODE_FAC]-[NNNN].
    
    :param faculte_id: ID de la faculté de l'étudiant.
    :return: Chaîne de caractères du matricule généré.
    """
    # 1. Récupérer le code court de la faculté
    faculte = Faculte.query.get(faculte_id)
    if not faculte:
        raise ValueError("Faculté non trouvée.")
        
    code_fac = faculte.code_court.upper()

    # 2. Déterminer le préfixe
    prefix = f'UCB-{code_fac}-'
    
    # 3. Trouver le numéro séquentiel maximum existant pour cette faculté
    # On filtre les matricules qui commencent par notre préfixe, on trie par ordre décroissant
    # et on prend le premier pour extraire le numéro.
    last_etudiant = Etudiant.query \
        .filter(Etudiant.matricule.like(f'{prefix}%')) \
        .order_by(Etudiant.matricule.desc()) \
        .first()

    numero_seq = 1
    if last_etudiant:
        # Extraire le numéro séquentiel de la fin du matricule
        try:
            # Ex: UCB-INFO-0045 -> ['UCB', 'INFO', '0045']
            last_seq_str = last_etudiant.matricule.split('-')[-1]
            numero_seq = int(last_seq_str) + 1
        except Exception:
            # Si le format n'est pas bon, on repart de 1
            print(f"Erreur de parsing du matricule: {last_etudiant.matricule}")
            numero_seq = 1 
            
    # 4. Formater le numéro séquentiel (NNNN, ex: 1 -> 0001)
    numero_seq_formatted = str(numero_seq).zfill(4)

    return f"UCB-{code_fac}-{numero_seq_formatted}"

# ==========================================================
# 3. Mise à jour du solde dénormalisé
# ==========================================================
def update_etudiant_solde(etudiant_id, montant_ajoute):
    etudiant = Etudiant.query.get(etudiant_id)
    if etudiant:
        # 1. On s'assure que le solde actuel est un Decimal (0 si None)
        solde_actuel = Decimal(str(etudiant.montant_total_paye))
        
        # 2. On convertit le montant entrant en Decimal
        ajout = Decimal(str(montant_ajoute))
        
        # 3. On fait l'opération
        etudiant.montant_total_paye = solde_actuel + ajout
        return True
    return False

# ==========================================================
# 4. Tâche Planifiée : Marquage des absents
# ==========================================================
def mark_absents_daily(app):
    # ... (Le reste de la fonction reste inchangé) ...
    print("Tâche APScheduler : Exécution du marquage des absents...")
    """ 
    Tâche exécutée quotidiennement pour marquer les étudiants non scannés (non présents) comme absents. 
    """
    
    # Nécessaire car le scheduler s'exécute en dehors du contexte d'une requête Flask
    with app.app_context(): 
        current_date = date.today()
        current_app.logger.info(f"Début de la tâche de marquage des absents pour la date : {current_date}")
        
        # 1. Récupérer tous les étudiants actifs (nous supposons tous les étudiants pour l'instant)
        all_etudiants = Etudiant.query.all()
        
        absents_count = 0
        
        for etudiant in all_etudiants:
            # 2. Vérifier si l'étudiant a été marqué "Présent" aujourd'hui
            # La présence est enregistrée si le scan a eu lieu dans l'auditoire ciblé
            
            # Recherche d'une présence validée pour l'étudiant à cette date
            has_presence = Presence.query.filter_by(
                etudiant_id=etudiant.id,
                date_presence=current_date
            ).first()
            
            # 3. Si aucune présence validée n'est trouvée
            if not has_presence:
                
                # Double-check: Vérifier si l'étudiant n'est pas déjà marqué absent pour aujourd'hui
                already_absent = Absence.query.filter_by(
                    etudiant_id=etudiant.id,
                    date_absence=current_date
                ).first()
                
                if not already_absent:
                    # 4. Enregistrer l'Absence
                    new_absence = Absence(
                        etudiant_id=etudiant.id,
                        date_absence=current_date,
                        justifiee=False # Marqué comme non justifié par défaut
                    )
                    db.session.add(new_absence)
                    absents_count += 1
        
        try:
            db.session.commit()
            current_app.logger.info(f"Tâche terminée. {absents_count} absences enregistrées pour {current_date}.")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la validation finale des absences : {e}")