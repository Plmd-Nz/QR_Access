# app/services/reporting_service.py

from ..extensions import db
from ..models import Etudiant, Presence, Absence # Importation des modèles nécessaires
from fpdf import FPDF # fpdf2 est importé sous le nom FPDF
import pandas as pd
from io import BytesIO
from datetime import datetime
from flask import current_app

# ==========================================================
# 1. GÉNÉRATION DE RAPPORT CSV (Pour l'Analyse)
# ==========================================================

def generate_csv_report(query, columns, filename):
    """
    Récupère les données d'une requête SQLAlchemy et les retourne sous forme de buffer CSV.

    :param query: Requête SQLAlchemy.
    :param columns: Liste des noms de colonnes.
    :param filename: Nom du fichier.
    :return: Tuple (Buffer en octets, Nom du fichier)
    """
    try:
        # Convertir les résultats de la requête en liste de dictionnaires
        results = [
            {col: getattr(row, col) for col in columns} 
            for row in query.all()
        ]
        
        # Créer un DataFrame Pandas
        df = pd.DataFrame(results, columns=columns)

        # Utiliser StringIO pour créer le fichier en mémoire
        buffer = BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8')
        buffer.seek(0)
        
        return buffer, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération du rapport CSV: {e}")
        return None, None

# ==========================================================
# 2. GÉNÉRATION DE RAPPORT PDF (Présence - Design Moderne)
# ==========================================================

class PDFReport(FPDF):
    """ Classe personnalisée pour le rapport PDF avec un design propre. """
    
    def header(self):
        # 1. Logo (Placeholder)
        # self.image(os.path.join(current_app.root_path, 'static/logo.png'), 10, 8, 33) 
        
        # 2. Titre du Rapport (Centré)
        self.set_font('Arial', 'B', 15)
        self.set_fill_color(0, 51, 102) # UCB Blue
        self.set_text_color(255, 255, 255)
        self.cell(self.w - 20, 10, 'UNIVERSITÉ CATHOLIQUE DE BUKAVU', 0, 1, 'C', 1)
        
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.cell(self.w - 20, 10, f'Rapport d\'Assiduité - Généré le {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_pdf_daily_call_list(promotion_id, date_str):
    """
    Génère le rapport de présence/absence fusionné pour une promotion et une date.
    """
    try:
        from ..models import Promotion, Etudiant, Presence, Absence
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        promotion = Promotion.query.get(promotion_id)
        
        if not promotion:
            return None, None

        # 1. Récupérer les données de manière optimisée
        # On récupère tous les étudiants de la promo triés alphabétiquement
        etudiants = Etudiant.query.filter_by(promotion_id=promotion_id).order_by(Etudiant.nom).all()
        
        # On récupère les IDs des présents et des absents pour cette date
        presents_dict = {p.etudiant_id: p.heure_scan for p in Presence.query.filter_by(date_presence=target_date).all()}
        absents_ids = [a.etudiant_id for a in Absence.query.filter_by(date_absence=target_date).all()]

        # 2. Initialisation du PDF
        pdf = PDFReport('P', 'mm', 'A4')
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # En-tête spécifique à la promotion
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"PROMOTION : {promotion.nom.upper()}", 0, 1, 'L')
        pdf.cell(0, 10, f"DATE DU RAPPORT : {target_date.strftime('%d/%m/%Y')}", 0, 1, 'L')
        pdf.ln(5)

        # Configuration du tableau
        col_widths = [40, 85, 35, 30]
        titles = ['MATRICULE', 'NOM COMPLET', 'STATUT', 'HEURE SCAN']
        
        # Header gris foncé
        pdf.set_fill_color(50, 50, 50)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 10)
        for i, title in enumerate(titles):
            pdf.cell(col_widths[i], 8, title, 1, 0, 'C', 1)
        pdf.ln()

        # 3. Remplissage des lignes
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 9)

        for e in etudiants:
            nom_complet = f"{e.nom} {e.postnom} {e.prenom}".upper()
            
            # Détermination du statut
            if e.id in presents_dict:
                statut = "PRESENT"
                info = presents_dict[e.id].strftime('%H:%M')
                pdf.set_text_color(0, 128, 0) # Vert
            elif e.id in absents_ids:
                statut = "ABSENT"
                info = "--:--"
                pdf.set_text_color(200, 0, 0) # Rouge
            else:
                statut = "NON MARQUÉ" # Cas où le scheduler n'est pas encore passé
                info = "--:--"
                pdf.set_text_color(100, 100, 100)

            pdf.cell(col_widths[0], 7, e.matricule, 1, 0, 'L')
            pdf.cell(col_widths[1], 7, nom_complet[:40], 1, 0, 'L') # On limite la longueur du nom
            pdf.cell(col_widths[2], 7, statut, 1, 0, 'C')
            pdf.cell(col_widths[3], 7, info, 1, 0, 'C')
            pdf.ln()
            pdf.set_text_color(0, 0, 0) # Reset couleur pour la ligne suivante

        filename = f"Liste_Appel_{promotion.nom}_{date_str}.pdf"
        return pdf.output(dest='S').encode('latin-1'), filename

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération du rapport : {e}")
        return None, None

def generate_pdf_financial_status(promotion_id, seuil_exige):
    """
    Génère un rapport de l'état des paiements pour une promotion.
    """
    try:
        from ..models import Promotion, Etudiant
        
        promotion = Promotion.query.get(promotion_id)
        if not promotion:
            return None, None

        # Récupérer les étudiants de la promo
        etudiants = Etudiant.query.filter_by(promotion_id=promotion_id).order_by(Etudiant.nom).all()

        pdf = PDFReport('P', 'mm', 'A4')
        pdf.alias_nb_pages()
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"ÉTAT DES PAIEMENTS : {promotion.nom.upper()}", 0, 1, 'L')
        pdf.cell(0, 10, f"SEUIL EXIGÉ : {seuil_exige} USD", 0, 1, 'L')
        pdf.ln(5)

        # Tableau
        col_widths = [40, 80, 35, 35]
        titles = ['MATRICULE', 'NOM COMPLET', 'MONTANT PAYÉ', 'STATUT']
        
        pdf.set_fill_color(0, 51, 102) # Bleu UCB
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 10)
        for i, title in enumerate(titles):
            pdf.cell(col_widths[i], 8, title, 1, 0, 'C', 1)
        pdf.ln()

        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 9)

        for e in etudiants:
            pdf.cell(col_widths[0], 7, e.matricule, 1, 0, 'L')
            pdf.cell(col_widths[1], 7, f"{e.nom} {e.postnom} {e.prenom}"[:35].upper(), 1, 0, 'L')
            pdf.cell(col_widths[2], 7, f"{e.montant_total_paye} USD", 1, 0, 'R')
            
            # Vérification du seuil
            if e.montant_total_paye >= seuil_exige:
                pdf.set_text_color(0, 128, 0)
                pdf.cell(col_widths[3], 7, 'EN RÈGLE', 1, 0, 'C')
            else:
                pdf.set_text_color(200, 0, 0)
                pdf.cell(col_widths[3], 7, 'INSOLVABLE', 1, 0, 'C')
            
            pdf.set_text_color(0, 0, 0)
            pdf.ln()

        filename = f"Etat_Financier_{promotion.nom.replace(' ', '_')}.pdf"
        return pdf.output(dest='S').encode('latin-1'), filename

    except Exception as e:
        current_app.logger.error(f"Erreur rapport financier: {e}")
        return None, None