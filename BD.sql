CREATE DATABASE IF NOT EXISTS qr_access;
USE qr_access;

-- ===========================================
-- NOUVELLE TABLE 1 : facultes
-- ===========================================
CREATE TABLE IF NOT EXISTS facultes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code_court VARCHAR(10) UNIQUE NOT NULL,
    nom VARCHAR(100) UNIQUE NOT NULL
);

-- ===========================================
-- NOUVELLE TABLE 2 : promotions
-- ===========================================
CREATE TABLE IF NOT EXISTS promotions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculte_id INT NOT NULL,
    nom VARCHAR(100) NOT NULL COMMENT 'Ex: BAC-1, BAC-2, Licence',
    filiere VARCHAR(100) NULL COMMENT 'Ex: Informatique, Gestion',
    
    FOREIGN KEY (faculte_id) REFERENCES facultes(id) ON DELETE RESTRICT,
    UNIQUE KEY unique_promotion (faculte_id, nom, filiere)
);

-- ===========================================
-- 3. Table administrateurs
-- ===========================================
CREATE TABLE IF NOT EXISTS administrateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_utilisateur VARCHAR(50) UNIQUE NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL COMMENT 'Mot de passe haché (Bcrypt)',
    nom_complet VARCHAR(100) NOT NULL
);

-- ===========================================
-- 4. Table etudiants (MODIFIÉE)
-- ===========================================
CREATE TABLE IF NOT EXISTS etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matricule VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(50) NOT NULL,
    postnom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    genre ENUM('M', 'F') NOT NULL,
    
    faculte_id INT NOT NULL, 
    promotion_id INT NOT NULL, 
    
    email VARCHAR(50) UNIQUE NOT NULL,
    photo_path VARCHAR(255) DEFAULT NULL COMMENT 'Chemin local ou URL de la photo',
    qr_code_cle VARCHAR(64) UNIQUE NOT NULL COMMENT 'Clé unique (hash) du QR code',
    
    -- NOUVEAU CHAMP : Solde pour vérification rapide
    montant_total_paye DECIMAL(10, 2) DEFAULT 0.00 COMMENT 'Somme des paiements validés pour l annee en cours (Dénormalisation pour rapidité)',
    
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (faculte_id) REFERENCES facultes(id) ON DELETE RESTRICT,
    FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE RESTRICT
);

-- ===========================================
-- 5. Table points_acces (Points de scan)
-- ===========================================
CREATE TABLE IF NOT EXISTS points_acces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL COMMENT 'Nom du point d accès',
    type_acces ENUM('Principal', 'Cours', 'Examen', 'Laboratoire') NOT NULL COMMENT 'Type d accès pour application des règles',
    promotion_cible_id INT NULL COMMENT 'Clé vers la promotion dont c est l auditoire (NULL si Principal/Examen/Labo)',
    
    FOREIGN KEY (promotion_cible_id) REFERENCES promotions(id) ON DELETE SET NULL
);

-- ===========================================
-- 6. Table paiements
-- ===========================================
CREATE TABLE IF NOT EXISTS paiements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    montant DECIMAL(10, 2) NOT NULL,
    motif VARCHAR(50) NOT NULL COMMENT 'Ex: frais académique, frais d examen',
    date_paiement DATE NOT NULL,
    annee_academique VARCHAR(20) NOT NULL,
    statut ENUM('valide', 'en_attente', 'rejete', 'partiel') DEFAULT 'en_attente' NOT NULL,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE
);

-- ===========================================
-- 7. Table registre_acces (Journal de traçabilité des accès)
-- ===========================================
CREATE TABLE IF NOT EXISTS registre_acces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    point_acces_id INT NOT NULL,
    timestamp DATETIME NOT NULL COMMENT 'Date et heure complètes du scan',
    statut ENUM('autorise', 'refuse') NOT NULL,
    raison_refus TEXT COMMENT 'Raison si l accès est refusé',
    
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (point_acces_id) REFERENCES points_acces(id) ON DELETE RESTRICT
);

-- ===========================================
-- 8. Table presences (Validations de Présence)
-- ===========================================
CREATE TABLE IF NOT EXISTS presences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    point_acces_id INT NOT NULL,
    date_presence DATE NOT NULL,
    heure_scan TIME NOT NULL, 
    
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (point_acces_id) REFERENCES points_acces(id) ON DELETE RESTRICT
);

-- ===========================================
-- NOUVELLE TABLE 9 : absences (Générée par le Scheduler)
-- ===========================================
CREATE TABLE IF NOT EXISTS absences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    date_absence DATE NOT NULL,
    justifiee BOOLEAN DEFAULT FALSE NOT NULL,
    motif_justification TEXT NULL,
    
    -- L'absence d'un étudiant est directement liée à son dossier
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
    
    -- Contrainte d'intégrité: Un étudiant n'est absent qu'une fois par jour
    UNIQUE KEY unique_absence_per_day (etudiant_id, date_absence)
);

-- Initialisation des Facultés (MISE À JOUR)
INSERT INTO facultes (id, nom, code_court) VALUES
(1, 'Agronomie', 'AGRO'),
(2, 'Architecture', 'ARCH'),
(3, 'Criminologie', 'CRIM'),
(4, 'Droit', 'DROIT'),
(5, 'Economie', 'ECO'),
(6, 'Environnement', 'ENV'),
(7, 'Informatique', 'INFO'),
(8, 'Medecine', 'MED'),
(9, 'Polytechnique', 'POLY'),
(10, 'Science Sociale', 'SS');

-- Inserction admin et mot de passe
INSERT INTO administrateurs VALUES (1,'admin' , '$2b$12$IvSTgTl0wVTSA9njXK2XQOingBjFQGottmQ9CsmPkTStVbbvateV.', 'Plmd Nz');
-- Définition des ID des Facultés pour les insertions de Promotions
SET @ID_AGR = 1; SET @ID_ARCH = 2; SET @ID_CRIM = 3; SET @ID_DROIT = 4;
SET @ID_ECO = 5; SET @ID_ENV = 6; SET @ID_INFO = 7; SET @ID_MED = 8;
SET @ID_POLY = 9; SET @ID_SS = 10;

-- Insertion des promotions
INSERT INTO promotions (faculte_id, nom) VALUES
-- 1-3. Agronomie
(@ID_AGR, 'BAC1-AGR'), (@ID_AGR, 'BAC2-AGR'), (@ID_AGR, 'BAC3-AGR'),
-- 4-7. Architecture
(@ID_ARCH, 'BAC0-ARCHI'), (@ID_ARCH, 'BAC1-ARCHI'), (@ID_ARCH, 'BAC2-ARCHI'), (@ID_ARCH, 'BAC3-ARCHI'),
-- 8-10. Criminologie
(@ID_CRIM, 'BAC1-CRIM'), (@ID_CRIM, 'BAC2-CRIM'), (@ID_CRIM, 'BAC3-CRIM'),
-- 11-13. Droit
(@ID_DROIT, 'BAC1-DROIT'), (@ID_DROIT, 'BAC2-DROIT'), (@ID_DROIT, 'BAC3-DROIT'),
-- 14-16. Economie
(@ID_ECO, 'BAC1-ECO'), (@ID_ECO, 'BAC2-ECO'), (@ID_ECO, 'BAC3-ECO'),
-- 17-19. Environnement
(@ID_ENV, 'BAC1-ENV'), (@ID_ENV, 'BAC2-ENV'), (@ID_ENV, 'BAC3-ENV'),
-- 20-22. Informatique
(@ID_INFO, 'BAC1-INFO'), (@ID_INFO, 'BAC2-INFO'), (@ID_INFO, 'BAC3-INFO'),
-- 23-25. Medecine
(@ID_MED, 'BAC1-MED'), (@ID_MED, 'BAC2-MED'), (@ID_MED, 'BAC3-MED'),
-- 26-29. Polytechnique
(@ID_POLY, 'BAC0-POLY'), (@ID_POLY, 'BAC1-POLY'), (@ID_POLY, 'BAC2-POLY'), (@ID_POLY, 'BAC3-POLY'),
-- 30-32. Science Sociale
(@ID_SS, 'BAC1-SS'), (@ID_SS, 'BAC2-SS'), (@ID_SS, 'BAC3-SS'); 


-- Insertion des 37 Points d'Accès
INSERT INTO points_acces (nom, type_acces, promotion_cible_id) VALUES
-- Points Principaux (NULL)
('Entrée Principale Nord', 'Principal', NULL),
('Entrée Principale Sud', 'Principal', NULL),
-- Points d'Examen (NULL)
('Salle Examen A', 'Examen', NULL),
('Salle Examen B', 'Examen', NULL),
('Salle Examen C', 'Examen', NULL),
('Salle Examen D', 'Examen', NULL),
('Salle Examen E', 'Examen', NULL),
-- Points de Cours (Liés à l'ID de la Promotion, qui va de 1 à 32)
('BAC-1 ARGRO', 'Cours', 1),  ('BAC-2 ARGRO', 'Cours', 2),  ('BAC-3 ARGRO', 'Cours', 3), -- Agronomie
('BAC0-ARCHI', 'Cours', 4),  ('BAC1-ARCHI', 'Cours', 5),  ('BAC2-ARCHI', 'Cours', 6),  ('BAC3-ARCHI', 'Cours', 7), -- Architecture
('BAC-1 CRIMI', 'Cours', 8),  ('BAC-2 CRIMI', 'Cours', 9),  ('BAC-3 CRIMI', 'Cours', 10), -- Criminologie
('BAC-1 DROIT', 'Cours', 11), ('BAC-2 DROIT', 'Cours', 12), ('BAC-3 DROIT', 'Cours', 13), -- Droit
('BAC-1 ECO', 'Cours', 14), ('BAC-2 ECO', 'Cours', 15), ('BAC-3 ECO', 'Cours', 16), -- Economie
('BAC-1 ENV', 'Cours', 17), ('BAC-2 ENV', 'Cours', 18), ('BAC-3 ENV', 'Cours', 19), -- Environnement
('BAC-1 INFO', 'Cours', 20), ('BAC-2 INFO', 'Cours', 21), ('BAC-3 INFO', 'Cours', 22), -- Informatique
('BAC-1 MED', 'Cours', 23), ('BAC-2 MED', 'Cours', 24), ('BAC-3 MED', 'Cours', 25), -- Medecine
('BAC0-POLY', 'Cours', 26), ('BAC1-POLY', 'Cours', 27), ('BAC2-POLY', 'Cours', 28), ('BAC3-POLY', 'Cours', 29), -- Polytechnique
('BAC-1 Sc-S', 'Cours', 30), ('BAC-2 Sc-S', 'Cours', 31), ('BAC-3 Sc-S', 'Cours', 32); -- Science Sociale