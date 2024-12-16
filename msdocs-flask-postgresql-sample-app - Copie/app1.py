import psycopg2
from flask import Flask, request, jsonify, render_template

# Configuration de l'application Flask
app = Flask(__name__)

# Configuration de la base de données PostgreSQL
DB_CONFIG = {
    'host': 'allostade-server.postgres.database.azure.com',
    'database': 'allostade-database',
    'user': 'amympplfyb',
    'password': 'ogvm$PQL1Ek$DTd$',
    'port': 5432
}

# Connexion à la base de données
def connect_to_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

# Initialisation de la table pour stocker les réservations
def init_db():
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS reservations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    zone VARCHAR(10) NOT NULL,
                    row INTEGER NOT NULL,
                    seat INTEGER NOT NULL
                );
                ''')
                conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la table: {e}")
        finally:
            conn.close()

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Réservation Stade</title>
</head>
<body>
    <h1>Réservez votre place</h1>
    <form action="/reserve" method="POST">
        <label for="name">Nom :</label>
        <input type="text" id="name" name="name" required><br>
        <label for="email">Email :</label>
        <input type="email" id="email" name="email" required><br>
        <label for="phone">Téléphone :</label>
        <input type="tel" id="phone" name="phone" required><br>
        <label for="zone">Zone :</label>
        <select id="zone" name="zone" required>
            <option value="A">Zone A</option>
            <option value="B">Zone B</option>
        </select><br>
        <label for="row">Rangée :</label>
        <input type="number" id="row" name="row" min="1" max="3" required><br>
        <label for="seat">Place :</label>
        <input type="number" id="seat" name="seat" min="1" max="5" required><br>
        <button type="submit">Réserver</button>
    </form>
</body>
</html>'''

@app.route('/reserve', methods=['POST'])
def reserve():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    zone = request.form.get('zone')
    row = request.form.get('row')
    seat = request.form.get('seat')

    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                INSERT INTO reservations (name, email, phone, zone, row, seat)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                ''', (name, email, phone, zone, row, seat))
                reservation_id = cursor.fetchone()[0]
                conn.commit()
                return render_template('success.html', reservation_id=reservation_id)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la réservation: {e}")
            return render_template('error.html', error=str(e))
        finally:
            conn.close()
    else:
        return render_template('error.html', error="Impossible de se connecter à la base de données")

if __name__ == '_main_':
    init_db()
    app.run(debug=True)