# app/routes/serializers.py

# Importez les modèles ici car ce fichier n'importe rien des routes
from ..models import Etudiant, Faculte, Promotion , Paiement , PointAcces


# ==========================================================
# UTILITAIRE DE SÉRIALISATION (Copiés de admin.py)
# ==========================================================

def etudiant_to_dict(etudiant):
    """ Sérialise l'objet Etudiant en dictionnaire pour la réponse JSON. """
    return {
        "id": etudiant.id,
        "matricule": etudiant.matricule,
        "nom": etudiant.nom,
        "postnom": etudiant.postnom,
        "prenom": etudiant.prenom,
        "genre": etudiant.genre,
        "email": etudiant.email,
        "faculte_id": etudiant.faculte_id,
        "faculte_nom": etudiant.faculte_obj.nom if etudiant.faculte_obj else None,
        "promotion_id": etudiant.promotion_id,
        "promotion_nom": etudiant.promotion_obj.nom if etudiant.promotion_obj else None,
        "photo_path": etudiant.photo_path,
        "qr_code_cle": etudiant.qr_code_cle,
        "montant_total_paye": str(etudiant.montant_total_paye),
        "created_at": etudiant.date_creation.isoformat() if etudiant.date_creation else None
    }

def paiement_to_dict(paiement):
    """ Sérialise l'objet Paiement en dictionnaire. """
    return {
        "id": paiement.id,
        "etudiant_matricule": paiement.etudiant.matricule if paiement.etudiant else None,
        "montant": str(paiement.montant),
        "motif": paiement.motif,
        "date_paiement": paiement.date_paiement.isoformat() if paiement.date_paiement else None,
        "reference": paiement.reference,
        "annee_academique": paiement.annee_academique,
        "statut": paiement.statut,
         
    }

def faculte_to_dict(faculte):
    """ Sérialise l'objet Faculte en dictionnaire. """
    return {
        "id": faculte.id,
        "nom": faculte.nom,
        "code_court": faculte.code_court,
        "nombre_promotions": len(faculte.promotions) 
    }

def promotion_to_dict(promotion):
    """ Sérialise l'objet Promotion en dictionnaire. """
    return {
        "id": promotion.id,
        "faculte_id": promotion.faculte_id,
        "faculte_nom": promotion.faculte.nom if promotion.faculte else None, 
        "nom": promotion.nom,
        "filiere": promotion.filiere
    }

def point_acces_to_dict(p):
    """Traduit le modèle PointAcces vers le format attendu par le Frontend"""
    return {
        "id": p.id,
        "nom_point": p.nom,  # DB 'nom' -> Front 'nom_point'
        "type_acces": p.type_acces, # 'Principal', 'Cours', etc.
        "promotion_id": p.promotion_cible_id, # DB 'promotion_cible_id' -> Front 'promotion_id'
        # On récupère le nom de la promo si la relation existe
        "promotion_nom": p.promotion.nom if hasattr(p, 'promotion') and p.promotion else None,
        # Ton modèle n'a pas d'heures, on envoie des valeurs par défaut pour ne pas faire planter le Front
        "heure_debut": "08:00",
        "heure_fin": "17:00"
    }