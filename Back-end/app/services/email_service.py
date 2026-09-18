# app/services/email_service.py (NOUVEAU FICHIER À CRÉER)

from flask_mail import Mail, Message
from flask import current_app
import os

# Initialisation de l'extension Mail (dans app/extensions.py, il faudra l'ajouter)
mail = Mail() 

def send_student_card_email(recipient_email, student_name, card_path):
    """
    Envoie la carte d'étudiant générée par email.

    :param recipient_email: Adresse email de l'étudiant.
    :param student_name: Nom complet de l'étudiant.
    :param card_path: Chemin relatif de la carte d'étudiant (PNG).
    :return: True si succès, False sinon.
    """
    try:
        msg = Message(
            subject=f"Votre Carte d'Étudiant UCB - {student_name}",
            sender=current_app.config.get('MAIL_USERNAME', 'no-reply@ucb.cd'),
            recipients=[recipient_email]
        )
        msg.body = f"""
Cher/Chère {student_name},

Félicitations ! Votre carte d'étudiant pour l'Université Catholique de Bukavu (UCB) a été générée.

Vous trouverez en pièce jointe une copie numérique de votre carte. Veuillez la conserver précieusement. 
Votre QR Code unique est intégré pour valider votre accès aux campus et aux auditoires.

Cordialement,
L'Administration UCB
"""
        # Joindre la carte d'étudiant au mail
        full_card_path = os.path.join(current_app.root_path, card_path)
        with open(full_card_path, 'rb') as fp:
            msg.attach(f"Carte_UCB_{student_name.replace(' ', '_')}.png", "image/png", fp.read())
        # Envoyer l'email
        mail.send(msg)
        return True

    except Exception as e:
        current_app.logger.error(f"Échec de l'envoi de l'email à {recipient_email}: {e}")
        return False