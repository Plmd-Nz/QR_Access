# app/services/photo_service.py

import os
import uuid
import requests
import qrcode
import time
from PIL import Image, ImageDraw, ImageFont
from flask import current_app
from werkzeug.utils import secure_filename

# --- Configuration des Dimensions (Modifiables selon tes nouveaux besoins) ---
CARD_WIDTH = 800
CARD_HEIGHT = 500
PASSPORT_WIDTH = 280  # Ajusté pour l'ergonomie
PASSPORT_HEIGHT = 350 # Ajusté pour l'ergonomie

# --- Gestion des Chemins et Polices (Inchangé) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
FONT_DIR = os.path.join(APP_DIR, "static", "fonts")
os.makedirs(FONT_DIR, exist_ok=True)

def download_font_if_missing(font_name, url):
    FONT_DIR = os.path.join(APP_DIR, "static", "fonts")
    font_path = os.path.join(FONT_DIR, font_name)
    if not os.path.exists(font_path):
        try:
            r = requests.get(url, timeout=10)
            with open(font_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"Erreur téléchargement police {font_name}: {e}")
    return font_path

FONT_PATH_BOLD = download_font_if_missing(
    "Popstick-Demo-Regular.ttf",
    "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf"
)

FONT_PATH_REGULAR = download_font_if_missing(
    "Poison-Regular.otf",
    "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf"
)

# --- Service de Traitement de la Photo (Inchangé) ---
def process_and_save_photo(photo_file, student_name):
    try:
        photo_file.seek(0)
        base_dir = os.path.abspath(os.path.dirname(__file__))
        upload_folder = os.path.normpath(os.path.join(base_dir, '..', 'static', 'uploads', 'students'))
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        extension = os.path.splitext(photo_file.filename)[1].lower() or '.png'
        clean_name = secure_filename(student_name)
        filename = f"{clean_name}_{uuid.uuid4().hex[:5]}{extension}"
        file_path = os.path.normpath(os.path.join(upload_folder, filename))
        photo_file.save(file_path)
        time.sleep(0.1)
        return f"static/uploads/students/{filename}"
    except Exception as e:
        print(f"ERREUR PHOTO SERVICE (Save): {e}")
        return None

# --- Service de Génération de la Carte (Nouveau Design) ---
def generate_student_card(etudiant_data, photo_path, qr_code_cle):
    try:
        full_photo_path = os.path.normpath(os.path.join(current_app.root_path, photo_path))
        
        # 1. Paramètres de Design UCB
        UCB_BLUE = (0, 51, 102)
        UCB_GOLD = (255, 204, 0)
        TEXT_WHITE = (255, 255, 255)
        BG_GRADIENT_DARK = (0, 30, 60) # Pour un effet de profondeur

        # 2. Création de la base (Dégradé simple)
        card = Image.new('RGBA', (CARD_WIDTH, CARD_HEIGHT), color=UCB_BLUE)
        draw = ImageDraw.Draw(card)
        draw.rectangle([0, 0, 15, CARD_HEIGHT], fill=UCB_GOLD)

        # 3. Chargement des Polices
        try:
            font_title = ImageFont.truetype(FONT_PATH_BOLD, 24)
            font_subtitle = ImageFont.truetype(FONT_PATH_REGULAR, 14)
            font_label = ImageFont.truetype(FONT_PATH_REGULAR, 16)
            font_value = ImageFont.truetype(FONT_PATH_REGULAR, 16)
            font_tag = ImageFont.truetype(FONT_PATH_REGULAR, 12)
        except:
            font_title = font_subtitle = font_label = font_value = font_tag = ImageFont.load_default()

        # --- PARTIE 1 : LE HEADER ---
        # Bande Jaune UCB (Positionnée à droite du logo)
        draw.rounded_rectangle([180, 40, CARD_WIDTH - 20, 110], radius=15, fill=UCB_GOLD)
        
        # Carré blanc pour le Logo (Isolé à gauche)
        draw.rounded_rectangle([40, 25, 150, 135], radius=15, fill=UCB_BLUE)
        try:
            logo_path = os.path.join(current_app.root_path, 'static', 'images', 'logo.png')
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((90, 90), Image.Resampling.LANCZOS)
                # Centrage du logo dans le carré blanc
                card.paste(logo, (50, 35), logo)
        except: pass

        # Texte dans la bande jaune
        draw.text((315, 50), "UNIVERSITE CATHOLIQUE DE BUKAVU", font=font_title, fill=UCB_BLUE)
        draw.text((365, 80), "Carte d'Étudiant Académique", font=font_subtitle, fill=UCB_BLUE)

        # --- PARTIE 2 : LE CORPS (Photo et Infos) ---
        # Cadre de la photo (Blanc épais)
        photo_x, photo_y = 50, 170
        draw.rounded_rectangle([photo_x - 10, photo_y - 10, photo_x + PASSPORT_WIDTH + 10, photo_y + PASSPORT_HEIGHT - 30], radius=20, fill="white")

        try:
            with Image.open(full_photo_path) as img:
                profile_img = img.convert("RGBA").copy()
                profile_img.thumbnail((PASSPORT_WIDTH, PASSPORT_HEIGHT), Image.Resampling.LANCZOS)
                # On utilise la photo comme masque pour les arrondis
                p_size = profile_img.size
                mask = Image.new('L', p_size, 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle([0, 0, p_size[0], p_size[1]], radius=15, fill=255)
                card.paste(profile_img, (photo_x, photo_y), mask)
        except:
            draw.rectangle([photo_x, photo_y, photo_x+PASSPORT_WIDTH, photo_y+200], fill="grey")
            draw.text((photo_x+20, photo_y+80), "PHOTO", fill="white")

        # Informations (Alignement avec deux-points verticaux)
        info_x = 380
        info_y = 180
        labels = ["NOM", "POSTNOM", "PRÉNOM", "MATRICULE", "PROMOTION"]
        values = [
            etudiant_data.nom.upper(),
            etudiant_data.postnom.upper(),
            etudiant_data.prenom,
            etudiant_data.matricule,
            etudiant_data.promotion_obj.nom
        ]

        for i, label in enumerate(labels):
            draw.text((info_x, info_y), label, font=font_label, fill=UCB_GOLD)
            draw.text((info_x + 130, info_y), ":", font=font_label, fill=UCB_GOLD) # Alignement des :
            draw.text((info_x + 150, info_y), str(values[i]), font=font_value, fill=TEXT_WHITE)
            info_y += 45

        # --- PARTIE 3 : LE FOOTER ---
        # Ligne de séparation subtile
        draw.line([380, 420, CARD_WIDTH - 40, 420], fill=UCB_GOLD, width=1)
        
        # Année académique et le tag unique #Plmd_Nz
        draw.text((380, 440), "Année Académique: 2025-2026", font=font_tag, fill=TEXT_WHITE)
        draw.text((380, 460), "#Plmd_Nz", font=font_tag, fill=UCB_GOLD)

        # QR Code dans son bloc blanc (en bas à droite)
        qr_size = 100
        qr_x, qr_y = CARD_WIDTH - qr_size - 40, CARD_HEIGHT - qr_size - 40
        draw.rounded_rectangle([qr_x - 5, qr_y - 5, qr_x + qr_size + 5, qr_y + qr_size + 5], radius=10, fill="white")
        
        qr = qrcode.QRCode(version=1, box_size=3, border=1)
        qr.add_data(qr_code_cle)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=UCB_BLUE, back_color="white").convert("RGBA")
        qr_img = qr_img.resize((qr_size, qr_size))
        card.paste(qr_img, (qr_x, qr_y), qr_img)

        # --- SAUVEGARDE ---
        final_card = card.convert("RGB")
        card_filename = f"card_{etudiant_data.matricule.replace('/', '_')}.png"
        output_dir = os.path.normpath(os.path.join(current_app.root_path, 'static', 'photos'))
        os.makedirs(output_dir, exist_ok=True)
        full_output_path = os.path.join(output_dir, card_filename)
        final_card.save(full_output_path, 'PNG', quality=95)
        
        return f"static/photos/{card_filename}"

    except Exception as e:
        current_app.logger.error(f"Erreur design carte : {e}")
        return None