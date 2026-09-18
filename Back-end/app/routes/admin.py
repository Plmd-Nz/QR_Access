# app/routes/admin.py (Le fichier de base mis à jour)

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ..extensions import db
# On importe TOUS les modèles ici, car ils sont utilisés par les sous-modules
from ..models import Etudiant, Faculte, Promotion , Presence , Paiement , RegistreAcces , PointAcces 
from ..services.data_service import generate_qr_code_key, generate_matricule , update_etudiant_solde
from ..services.photo_service import process_and_save_photo, generate_student_card
from ..services.email_service import send_student_card_email
import os
from .auth import jwt_required 
from flask import send_file
from ..services.reporting_service import generate_csv_report
from io import BytesIO
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime, timedelta

# ==========================================================
# IMPORTATION ET ENREGISTREMENT DES SOUS-MODULES DE ROUTES
# Ceci doit se faire AVANT toute tentative d'importation de admin.py
# par un sous-module.
# ==========================================================

from .admin_etudiant import admin_etudiant_bp
from .paiement import paiement_bp
from .admin_academic import admin_academic_bp
from .admin_access import admin_access_bp
from .admin_reports import admin_reports_bp 
from .admin_stat import admin_stat_bp

# Définition du Blueprint principal
admin_bp = Blueprint('admin', __name__)

# Enregistrement des sous-Blueprints sur le Blueprint principal 'admin_bp'
admin_bp.register_blueprint(admin_etudiant_bp)
admin_bp.register_blueprint(paiement_bp)
admin_bp.register_blueprint(admin_academic_bp)
admin_bp.register_blueprint(admin_access_bp)
admin_bp.register_blueprint(admin_reports_bp) 
admin_bp.register_blueprint(admin_stat_bp)

# NOTE IMPORTANTE : Toutes les fonctions de sérialisation ont été déplacées
# dans app/routes/serializers.py et doivent être utilisées depuis là.