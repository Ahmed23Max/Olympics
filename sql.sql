ça cest les tableau que j'ai cree : -- Création de la table OffresDeBillets
CREATE TABLE Offres (
    id SERIAL PRIMARY KEY,
    type_billet VARCHAR(100),
    prix NUMERIC(10, 2),
    nombre_billets_disponibles INTEGER,
    date_debut_vente DATE,
    date_fin_vente DATE
);

-- Billets pour les événements sportifs
INSERT INTO Offres (type_billet, prix, nombre_billets_disponibles, date_debut_vente, date_fin_vente)
VALUES ('Billet pour la finale du 100 mètres masculin', 75.00, 500, '2024-08-01', '2024-08-10'),
       ('Billet pour la finale du saut en longueur féminin', 65.00, 400, '2024-08-02', '2024-08-11'),
       ('Billet pour la finale du 100 mètres nage libre masculin', 80.00, 600, '2024-08-03', '2024-08-12'),
       ('Billet pour la finale du relais 4x100 mètres nage libre féminin', 70.00, 450, '2024-08-04', '2024-08-13'),
       ('Billet pour la finale du concours général individuel masculin', 85.00, 550, '2024-08-05', '2024-08-14'),
       ('Billet pour la finale du sol féminin', 75.00, 400, '2024-08-06', '2024-08-15'),
       ('Billet pour le match de demi-finale', 90.00, 800, '2024-08-07', '2024-08-16'),
       ('Billet pour le match de la médaille de bronze', 70.00, 600, '2024-08-08', '2024-08-17');

-- Billets pour les cérémonies
INSERT INTO Offres (type_billet, prix, nombre_billets_disponibles, date_debut_vente, date_fin_vente)
VALUES ('Billet pour la cérémonie d''ouverture avec accès aux tribunes principales', 150.00, 2000, '2024-07-25', '2024-08-01'),
       ('Billet pour la cérémonie d''ouverture avec accès aux tribunes secondaires', 100.00, 3000, '2024-07-25', '2024-08-01'),
       ('Billet pour la cérémonie de clôture avec accès aux tribunes principales', 120.00, 1800, '2024-08-20', '2024-08-25'),
       ('Billet pour la cérémonie de clôture avec accès aux tribunes secondaires', 80.00, 2500, '2024-08-20', '2024-08-25');

-- Billets pour d'autres activités
INSERT INTO Offres (type_billet, prix, nombre_billets_disponibles, date_debut_vente, date_fin_vente)
VALUES ('Billet pour la visite guidée du village olympique pour les athlètes', 50.00, 300, '2024-07-20', '2024-08-05'),
       ('Billet pour la visite guidée du village olympique pour les spectateurs', 40.00, 500, '2024-07-20', '2024-08-05');