-- Seed data for testing

-- Ingredients
INSERT INTO ingredients (name_en, name_he) VALUES
    ('Acetaminophen', 'אצטמינופן'),
    ('Ibuprofen', 'איבופרופן'),
    ('Amoxicillin', 'אמוקסיצילין'),
    ('Omeprazole', 'אומפרזול'),
    ('Metformin', 'מטפורמין'),
    ('Lisinopril', 'ליסינופריל'),
    ('Atorvastatin', 'אטורבסטטין'),
    ('Diphenhydramine', 'דיפנהידרמין'),
    ('Pseudoephedrine', 'פסאודואפדרין'),
    ('Cetirizine', 'צטיריזין');

-- Medications
INSERT INTO medications (name_en, name_he, description_en, description_he, price, requires_prescription) VALUES
    ('Acamol', 'אקמול', 'Pain reliever and fever reducer', 'משכך כאבים ומוריד חום', 12.90, 0),
    ('Advil', 'אדוויל', 'Anti-inflammatory pain reliever', 'משכך כאבים אנטי דלקתי', 24.90, 0),
    ('Moxypen', 'מוקסיפן', 'Antibiotic for bacterial infections', 'אנטיביוטיקה לזיהומים חיידקיים', 35.00, 1),
    ('Losec', 'לוסק', 'Reduces stomach acid production', 'מפחית ייצור חומצת קיבה', 89.90, 1),
    ('Glucophage', 'גלוקופאז׳', 'Controls blood sugar levels in type 2 diabetes', 'מאזן רמות סוכר בדם בסוכרת סוג 2', 45.00, 1),
    ('Zestril', 'זסטריל', 'ACE inhibitor for high blood pressure', 'מעכב ACE ליתר לחץ דם', 67.50, 1),
    ('Lipitor', 'ליפיטור', 'Lowers cholesterol levels', 'מוריד רמות כולסטרול', 125.00, 1),
    ('Benadryl', 'בנדריל', 'Antihistamine for allergies', 'אנטיהיסטמין לאלרגיות', 29.90, 0),
    ('Sudafed', 'סודאפד', 'Nasal decongestant', 'מפחית גודש באף', 32.00, 0),
    ('Zyrtec', 'זירטק', 'Non-drowsy allergy relief', 'הקלה מאלרגיות ללא ישנוניות', 39.90, 0);

-- Medication-Ingredient relationships
INSERT INTO medication_ingredients (medication_id, ingredient_id) VALUES
    (1, 1),  -- Acamol contains Acetaminophen
    (2, 2),  -- Advil contains Ibuprofen
    (3, 3),  -- Moxypen contains Amoxicillin
    (4, 4),  -- Losec contains Omeprazole
    (5, 5),  -- Glucophage contains Metformin
    (6, 6),  -- Zestril contains Lisinopril
    (7, 7),  -- Lipitor contains Atorvastatin
    (8, 8),  -- Benadryl contains Diphenhydramine
    (9, 9),  -- Sudafed contains Pseudoephedrine
    (10, 10); -- Zyrtec contains Cetirizine

-- Stock (with different dosages)
INSERT INTO stock (medication_id, dosage, quantity) VALUES
    (1, '500mg', 150),
    (1, '250mg', 80),
    (2, '200mg', 100),
    (2, '400mg', 45),
    (3, '500mg', 30),
    (3, '250mg', 50),
    (4, '20mg', 25),
    (4, '40mg', 15),
    (5, '500mg', 60),
    (5, '850mg', 40),
    (6, '10mg', 35),
    (6, '20mg', 20),
    (7, '10mg', 50),
    (7, '20mg', 30),
    (8, '25mg', 75),
    (9, '60mg', 55),
    (10, '10mg', 90);

-- Users
INSERT INTO users (pin, name) VALUES
    ('1234', 'David Cohen'),
    ('5678', 'Sarah Levy'),
    ('9012', 'Michael Ben-Ari'),
    ('3456', 'Rachel Green');

-- Prescriptions
INSERT INTO prescriptions (user_id, medication_id, dosage, months_supply, months_fulfilled, expires_at) VALUES
    (1, 5, '500mg', 6, 2, '2026-06-01'),  -- David: Glucophage, 6 months, 2 fulfilled
    (1, 7, '10mg', 12, 4, '2026-12-01'),  -- David: Lipitor, 12 months, 4 fulfilled
    (2, 6, '10mg', 3, 0, '2026-03-15'),   -- Sarah: Zestril, 3 months, none fulfilled
    (3, 4, '20mg', 2, 1, '2026-02-28'),   -- Michael: Losec, 2 months, 1 fulfilled
    (4, 3, '500mg', 1, 0, '2026-01-31');  -- Rachel: Moxypen, 1 month, none fulfilled
