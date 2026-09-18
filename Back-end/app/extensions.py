# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from flask_mail import Mail 

# 1. Base de Données (ORM)
db = SQLAlchemy()

# 2. Sécurité (Hachage des mots de passe)
bcrypt = Bcrypt()

# 3. Tâches Planifiées (Marquage des absents)
scheduler = APScheduler()

# 4. Mail (pour l'envoi des emails)
mail = Mail()