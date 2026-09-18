# run.py

import os
os.environ['ONNX_EXECUTOR'] = 'CPU'
from app import create_app
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    # Ceci crée les tables dans la base de données (basé sur models.py)
    # C'est la première étape après l'installation du connecteur MySQL
    with app.app_context():
        # Utiliser 'db.drop_all()' si vous voulez repartir à zéro
        db.create_all() 
        print("Base de données initialisée (tables créées).")

    app.run(debug=True)