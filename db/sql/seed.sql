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
    ('Cetirizine', 'צטיריזין'),
    ('Loratadine', 'לוראטדין'),
    ('Amlodipine', 'אמלודיפין');

-- Medications
INSERT INTO medications (name_en, name_he, description_en, description_he, price, requires_prescription) VALUES
    -- Acetaminophen products (ingredient 1)
    ('Acamol', 'אקמול', 'Pain reliever and fever reducer', 'משכך כאבים ומוריד חום', 12.90, 0),
    ('Dexamol', 'דקסמול', 'Pain reliever and fever reducer', 'משכך כאבים ומוריד חום', 14.90, 0),
    ('Paracetamol Teva', 'פראצטמול טבע', 'Generic pain reliever and fever reducer', 'משכך כאבים ומוריד חום גנרי', 8.90, 0),

    -- Ibuprofen products (ingredient 2)
    ('Advil', 'אדוויל', 'Anti-inflammatory pain reliever', 'משכך כאבים אנטי דלקתי', 24.90, 0),
    ('Nurofen', 'נורופן', 'Anti-inflammatory pain reliever', 'משכך כאבים אנטי דלקתי', 27.90, 0),
    ('Ibuprofen Teva', 'איבופרופן טבע', 'Generic anti-inflammatory pain reliever', 'משכך כאבים אנטי דלקתי גנרי', 15.90, 0),

    -- Amoxicillin products (ingredient 3)
    ('Moxypen', 'מוקסיפן', 'Antibiotic for bacterial infections', 'אנטיביוטיקה לזיהומים חיידקיים', 35.00, 1),
    ('Amoxicillin Teva', 'אמוקסיצילין טבע', 'Generic antibiotic for bacterial infections', 'אנטיביוטיקה גנרית לזיהומים חיידקיים', 22.00, 1),

    -- Omeprazole products (ingredient 4)
    ('Losec', 'לוסק', 'Reduces stomach acid production', 'מפחית ייצור חומצת קיבה', 89.90, 1),
    ('Omepradex', 'אומפרדקס', 'Reduces stomach acid production', 'מפחית ייצור חומצת קיבה', 65.00, 1),
    ('Omeprazole Teva', 'אומפרזול טבע', 'Generic stomach acid reducer', 'מפחית חומצת קיבה גנרי', 35.00, 1),

    -- Metformin products (ingredient 5)
    ('Glucophage', 'גלוקופאז׳', 'Controls blood sugar levels in type 2 diabetes', 'מאזן רמות סוכר בדם בסוכרת סוג 2', 45.00, 1),
    ('Metformin Teva', 'מטפורמין טבע', 'Generic blood sugar control for type 2 diabetes', 'מאזן סוכר גנרי לסוכרת סוג 2', 25.00, 1),

    -- Lisinopril products (ingredient 6)
    ('Zestril', 'זסטריל', 'ACE inhibitor for high blood pressure', 'מעכב ACE ליתר לחץ דם', 67.50, 1),

    -- Atorvastatin products (ingredient 7)
    ('Lipitor', 'ליפיטור', 'Lowers cholesterol levels', 'מוריד רמות כולסטרול', 125.00, 1),
    ('Atorvastatin Teva', 'אטורבסטטין טבע', 'Generic cholesterol reducer', 'מוריד כולסטרול גנרי', 45.00, 1),

    -- Diphenhydramine products (ingredient 8)
    ('Benadryl', 'בנדריל', 'Antihistamine for allergies', 'אנטיהיסטמין לאלרגיות', 29.90, 0),

    -- Pseudoephedrine products (ingredient 9)
    ('Sudafed', 'סודאפד', 'Nasal decongestant', 'מפחית גודש באף', 32.00, 0),

    -- Cetirizine products (ingredient 10)
    ('Zyrtec', 'זירטק', 'Non-drowsy allergy relief', 'הקלה מאלרגיות ללא ישנוניות', 39.90, 0),
    ('Histazine', 'היסטזין', 'Non-drowsy allergy relief', 'הקלה מאלרגיות ללא ישנוניות', 29.90, 0),

    -- Loratadine products (ingredient 11) - COMPLETELY OUT OF STOCK (no alternatives)
    ('Claritine', 'קלריטין', 'Long-lasting allergy relief', 'הקלה ממושכת מאלרגיות', 42.00, 0),

    -- Amlodipine products (ingredient 12) - COMPLETELY OUT OF STOCK (no alternatives)
    ('Norvasc', 'נורבסק', 'Calcium channel blocker for high blood pressure', 'חוסם תעלות סידן ליתר לחץ דם', 85.00, 1);

-- Medication-Ingredient relationships
INSERT INTO medication_ingredients (medication_id, ingredient_id) VALUES
    -- Acetaminophen medications
    (1, 1),   -- Acamol
    (2, 1),   -- Dexamol
    (3, 1),   -- Paracetamol Teva

    -- Ibuprofen medications
    (4, 2),   -- Advil
    (5, 2),   -- Nurofen
    (6, 2),   -- Ibuprofen Teva

    -- Amoxicillin medications
    (7, 3),   -- Moxypen
    (8, 3),   -- Amoxicillin Teva

    -- Omeprazole medications
    (9, 4),   -- Losec
    (10, 4),  -- Omepradex
    (11, 4),  -- Omeprazole Teva

    -- Metformin medications
    (12, 5),  -- Glucophage
    (13, 5),  -- Metformin Teva

    -- Lisinopril medications
    (14, 6),  -- Zestril

    -- Atorvastatin medications
    (15, 7),  -- Lipitor
    (16, 7),  -- Atorvastatin Teva

    -- Diphenhydramine medications
    (17, 8),  -- Benadryl

    -- Pseudoephedrine medications
    (18, 9),  -- Sudafed

    -- Cetirizine medications
    (19, 10), -- Zyrtec
    (20, 10), -- Histazine

    -- Loratadine medications (no alternatives)
    (21, 11), -- Claritine

    -- Amlodipine medications (no alternatives)
    (22, 12); -- Norvasc

-- Stock (with interesting scenarios)
INSERT INTO stock (medication_id, dosage, quantity) VALUES
    -- Acamol: COMPLETELY OUT OF STOCK
    (1, '500mg', 0),
    (1, '250mg', 0),
    -- Dexamol: in stock (alternative for Acamol 500mg)
    (2, '500mg', 120),
    (2, '250mg', 60),
    -- Paracetamol Teva: in stock (cheap alternative)
    (3, '500mg', 200),

    -- Advil: 400mg OUT OF STOCK, 200mg low stock
    (4, '200mg', 8),
    (4, '400mg', 0),
    -- Nurofen: in stock (alternative for Advil)
    (5, '200mg', 75),
    (5, '400mg', 50),
    -- Ibuprofen Teva: in stock (cheap alternative)
    (6, '200mg', 150),
    (6, '400mg', 100),

    -- Moxypen: low stock
    (7, '500mg', 5),
    (7, '250mg', 12),
    -- Amoxicillin Teva: in stock (cheaper alternative)
    (8, '500mg', 80),
    (8, '250mg', 60),

    -- Losec: OUT OF STOCK completely
    (9, '20mg', 0),
    (9, '40mg', 0),
    -- Omepradex: in stock (alternative)
    (10, '20mg', 45),
    (10, '40mg', 30),
    -- Omeprazole Teva: in stock (cheap alternative)
    (11, '20mg', 100),
    (11, '40mg', 75),

    -- Glucophage: in stock
    (12, '500mg', 60),
    (12, '850mg', 40),
    -- Metformin Teva: in stock (cheaper)
    (13, '500mg', 150),
    (13, '850mg', 90),

    -- Zestril: in stock
    (14, '10mg', 35),
    (14, '20mg', 20),

    -- Lipitor: 20mg OUT OF STOCK
    (15, '10mg', 50),
    (15, '20mg', 0),
    -- Atorvastatin Teva: in stock (cheap alternative for Lipitor 20mg)
    (16, '10mg', 120),
    (16, '20mg', 85),

    -- Benadryl: in stock
    (17, '25mg', 75),

    -- Sudafed: low stock
    (18, '60mg', 3),

    -- Zyrtec: very low stock
    (19, '10mg', 2),
    -- Histazine: in stock (alternative for Zyrtec)
    (20, '10mg', 95),

    -- Claritine: COMPLETELY OUT OF STOCK (no alternatives exist)
    (21, '10mg', 0),

    -- Norvasc: COMPLETELY OUT OF STOCK (no alternatives exist)
    (22, '5mg', 0),
    (22, '10mg', 0);

-- Users
INSERT INTO users (pin, name) VALUES
    ('1234', 'David Cohen'),
    ('5678', 'Sarah Levy'),
    ('9012', 'Michael Ben-Ari'),
    ('3456', 'Rachel Green'),
    ('7890', 'Yossi Mizrachi');

-- Prescriptions (various interesting scenarios)
INSERT INTO prescriptions (user_id, medication_id, dosage, months_supply, months_fulfilled, expires_at) VALUES
    -- David: Glucophage (in stock) - active, partially fulfilled
    (1, 12, '500mg', 6, 2, '2026-06-01'),
    -- David: Lipitor 20mg (OUT OF STOCK) - needs alternative
    (1, 15, '20mg', 12, 4, '2026-12-01'),

    -- Sarah: Zestril (in stock) - active, none fulfilled yet
    (2, 14, '10mg', 3, 0, '2026-03-15'),
    -- Sarah: Norvasc (OUT OF STOCK, NO ALTERNATIVES) - problematic scenario
    (2, 22, '5mg', 6, 1, '2026-08-01'),

    -- Michael: Losec (OUT OF STOCK) - needs alternative
    (3, 9, '20mg', 2, 1, '2026-02-28'),

    -- Rachel: Moxypen (low stock) - active prescription
    (4, 7, '500mg', 1, 0, '2026-01-31'),

    -- Yossi: Glucophage - EXPIRED prescription
    (5, 12, '850mg', 6, 3, '2024-12-01'),
    -- Yossi: Lipitor - FULLY FULFILLED (no refills remaining)
    (5, 15, '10mg', 3, 3, '2026-06-01'),
    -- Yossi: Claritine (OUT OF STOCK, NO ALTERNATIVES) - double problem
    (5, 21, '10mg', 2, 0, '2026-04-15');
