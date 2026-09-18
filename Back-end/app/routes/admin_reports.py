from flask import Blueprint, request, jsonify, send_file, current_app
from .auth import jwt_required
from ..models import Presence, Etudiant, Absence  # Ajout de Absence
from datetime import datetime # Import indispensable
from io import BytesIO

admin_reports_bp = Blueprint('admin_reports', __name__)

@admin_reports_bp.route('/daily-call-list', methods=['GET', 'OPTIONS'])
#@jwt_required()
def get_daily_call_list():
    """
    Génère la liste d'appel fusionnée (Présences + Absences)
    pour une promotion et une date précise.
    """
    if request.method == 'OPTIONS':
        return '', 200

   
    promo_id = request.args.get('promotion_id', type=int) # Force le type entier
    date_str = request.args.get('date')

    if not promo_id or not date_str:
        return jsonify({"message": "Promotion et Date sont requises."}), 400

    try:
        # On délègue TOUT au service pour éviter de multiplier les requêtes ici
        from ..services.reporting_service import generate_pdf_daily_call_list
       
        # Le service s'occupe de Presence, Absence et du tri alphabétique
        buffer, filename = generate_pdf_daily_call_list(promo_id, date_str)

        if buffer:
            return send_file(
                BytesIO(buffer),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )

        return jsonify({"message": "Aucune donnée trouvée ou erreur de génération"}), 404

    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération du rapport: {e}")
        return jsonify({"message": "Une erreur interne est survenue"}), 500

@admin_reports_bp.route('/financial-status', methods=['GET'])
#@jwt_required()
def get_financial_report():
    promo_id = request.args.get('promotion_id', type=int)
    # On récupère le seuil depuis la config de l'app
    seuil = current_app.config.get('PAIEMENT_SEUIL_MINIMUM', 0)

    if not promo_id:
        return jsonify({"message": "ID de promotion requis"}), 400

    from ..services.reporting_service import generate_pdf_financial_status
    buffer, filename = generate_pdf_financial_status(promo_id, seuil)

    if buffer:
        return send_file(
            BytesIO(buffer),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    return jsonify({"message": "Erreur de génération"}), 500
