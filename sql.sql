INSERT INTO tickets (event_date, price, available_tickets, event_name, stripe_id)
VALUES
('2024-08-23', 70.00, 200, 'Water Polo - Finale femmes', 'price_1PJehLL5fKqjqr4bSPn1vIlc'),
('2024-08-22', 70.00, 200, 'Water Polo - Finale hommes', 'price_1PJehKL5fKqjqr4bOsoJy0CY'),
('2024-08-21', 50.00, 200, 'Hockey sur gazon - Finale femmes', 'price_1PJehJL5fKqjqr4bpKR08r6I'),
('2024-08-20', 50.00, 200, 'Hockey sur gazon - Finale hommes', 'price_1PJehJL5fKqjqr4bgSTPRJHO'),
('2024-08-19', 75.00, 140, 'Boxe - Finale poids lourds femmes', 'price_1PJehBL5fKqjqr4bMOmXJs2N'),
('2024-08-18', 75.00, 140, 'Boxe - Finale poids lourds hommes', 'price_1PJehHL5fKqjqr4bERyeOYtF'),
('2024-08-17', 85.00, 110, 'Rugby - Finale femmes', 'price_1PJehHL5fKqjqr4bcItqcap1'),
('2024-08-16', 85.00, 110, 'Rugby - Finale hommes', 'price_1PJehGL5fKqjqr4bOdJM0PJX'),
('2024-08-15', 65.00, 160, 'Handball - Match préliminaire femmes', 'price_1PJehFL5fKqjqr4bWOUEfK1r'),
('2024-08-14', 65.00, 160, 'Handball - Match préliminaire hommes', 'price_1PJehFL5fKqjqr4bXoXy6Xjp'),
('2024-08-12', 50.00, 200, 'Volley-ball - Match préliminaire hommes', 'price_1PJehEL5fKqjqr4bO019td49'),
('2024-08-13', 50.00, 200, 'Volley-ball - Match préliminaire femmes', 'price_1PJehEL5fKqjqr4b1hWKIMkd'),
('2024-08-10', 60.00, 140, 'Aviron - Finale hommes', 'price_1PJehCL5fKqjqr4blLFsacAD'),
('2024-08-11', 60.00, 140, 'Aviron - Finale femmes', 'price_1PJehDL5fKqjqr4buzOjyWA2'),
('2024-08-08', 55.00, 130, 'Escrime - Finale épée hommes', 'price_1PJehBL5fKqjqr4baPdaqSXE'),
('2024-08-09', 55.00, 130, 'Escrime - Finale épée femmes', 'price_1PJehCL5fKqjqr4bsBfkBghC'),
('2024-08-07', 40.00, 250, 'Cyclisme - Course sur route femmes', 'price_1PJehBL5fKqjqr4b51nfOd3q'),
('2024-08-06', 40.00, 250, 'Cyclisme - Course sur route hommes', 'price_1PJehAL5fKqjqr4bfqT4KvYa'),
('2024-08-05', 90.00, 90, 'Tennis - Finale femmes', 'price_1PJeh9L5fKqjqr4bEZc0b8gh'),
('2024-08-04', 90.00, 90, 'Tennis - Finale hommes', 'price_1PJeh9L5fKqjqr4bXyjRf4WT'),
('2024-08-03', 70.00, 180, 'Basketball - Match préliminaire femmes', 'price_1PJeh8L5fKqjqr4bPYxmn2D5'),
('2024-08-02', 70.00, 180, 'Basketball - Match préliminaire hommes', 'price_1PJehFL5fKqjqr4b1eA4lScG'),
('2024-08-01', 80.00, 120, 'Gymnastique - Finale femmes', 'price_1PJehBL5fKqjqr4bEs5UxGZf'),
('2024-07-31', 80.00, 120, 'Gymnastique - Finale hommes', 'price_1PJehAL5fKqjqr4b2vysUaDy'),
('2024-07-30', 60.00, 150, 'Natation - 200m papillon femmes', 'price_1PJehEL5fKqjqr4b1aIMToH1'),
('2024-07-29', 60.00, 150, 'Natation - 100m nage libre hommes', 'price_1PJehCL5fKqjqr4bDFmzXdLz'),
('2024-07-28', 50.00, 200, 'Athlétisme - 200m femmes', 'price_1PJehAL5fKqjqr4bN1LZs8iR'),
('2024-07-27', 50.00, 200, 'Athlétisme - 100m hommes', 'price_1PJeh9L5fKqjqr4bMzVgqz4f')


-- Tableau tickets
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(100),
    event_date DATE,
    price DECIMAL(10, 2),
    available_tickets INTEGER CHECK (available_tickets >= 0) -- Contrainte pour s'assurer que le nombre de billets disponibles est toujours positif
);

-- Tableau purchases
CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    ticket_id INTEGER REFERENCES tickets(id),
    quantity INTEGER CHECK (quantity > 0), -- Contrainte pour s'assurer que la quantité est toujours positive
    price DECIMAL(10, 2),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
