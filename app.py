from flask import Flask, render_template, request, redirect
import psycopg2
import os

# Prendiamo il DATABASE_URL dalle variabili d'ambiente
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)

# Funzione per connettersi al database
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# Setup database: crea tabelle e dati iniziali
def setup_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Creiamo le tabelle se non esistono
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS storage (
            id SERIAL PRIMARY KEY,
            item TEXT NOT NULL,
            location_id INTEGER REFERENCES locations(id),
            spot TEXT,
            notes TEXT,
            category_id INTEGER REFERENCES categories(id)
        );
    ''')

    # Inseriamo valori iniziali se non ci sono
    cur.execute("INSERT INTO categories (name) VALUES ('Altro') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO categories (name) VALUES ('Viaggio') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO categories (name) VALUES ('Vestiti') ON CONFLICT DO NOTHING;")

    cur.execute("INSERT INTO locations (name) VALUES ('Solaio Nonno') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO locations (name) VALUES ('Garage Tatona') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO locations (name) VALUES ('Garage Tatina') ON CONFLICT DO NOTHING;")
    cur.execute("INSERT INTO locations (name) VALUES ('Solaio Nostro') ON CONFLICT DO NOTHING;")

    conn.commit()
    cur.close()
    conn.close()

# Avviamo il setup
setup_db()

# Home page per inserire oggetti
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM categories')
    categories = cur.fetchall()

    cur.execute('SELECT * FROM locations')
    locations = cur.fetchall()

    if request.method == 'POST':
        item = request.form['item']
        location_id = request.form['location']
        spot = request.form['spot']
        notes = request.form['notes']
        category_id = request.form['category']

        cur.execute('''
            INSERT INTO storage (item, location_id, spot, notes, category_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (item, location_id, spot, notes, category_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect('/list')

    cur.close()
    conn.close()
    return render_template('index.html', categories=categories, locations=locations)

# Pagina lista oggetti
@app.route('/list')
def list_items():
    q = request.args.get('q', '')
    location_filter = request.args.get('location', '')
    reset = request.args.get('reset', '')

    if reset:
        q = ''
        location_filter = ''

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM locations')
    locations = cur.fetchall()

    query = '''
        SELECT storage.*, categories.name AS category_name, locations.name AS location_name
        FROM storage
        LEFT JOIN categories ON storage.category_id = categories.id
        LEFT JOIN locations ON storage.location_id = locations.id
    '''
    params = []

    if q:
        query += ' WHERE storage.item ILIKE %s OR storage.notes ILIKE %s OR locations.name ILIKE %s'
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])

    if location_filter:
        if 'WHERE' in query:
            query += ' AND storage.location_id = %s'
        else:
            query += ' WHERE storage.location_id = %s'
        params.append(location_filter)

    query += ' ORDER BY storage.item ASC'

    cur.execute(query, params)
    items = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('list.html', items=items, locations=locations, location_filter=location_filter, search_query=q)

# Pagina modifica oggetti
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM categories')
    categories = cur.fetchall()

    cur.execute('SELECT * FROM locations')
    locations = cur.fetchall()

    if request.method == 'POST':
        item = request.form['item']
        location_id = request.form['location']
        spot = request.form['spot']
        notes = request.form['notes']
        category_id = request.form['category']

        cur.execute('''
            UPDATE storage
            SET item = %s, location_id = %s, spot = %s, notes = %s, category_id = %s
            WHERE id = %s
        ''', (item, location_id, spot, notes, category_id, item_id))

        conn.commit()
        cur.close()
        conn.close()
        return redirect('/list')

    cur.execute('SELECT * FROM storage WHERE id = %s', (item_id,))
    item = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('edit.html', item=item, categories=categories, locations=locations)

# Cancellare oggetto
@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM storage WHERE id = %s', (item_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/list')

# Gestione categorie
@app.route('/manage_categories')
def manage_categories():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM categories')
    categories = cur.fetchall()

    cur.close()
    conn.close()

    categories.sort(key=lambda x: x[1].lower())

    return render_template('manage_categories.html', categories=categories)

@app.route('/add_category', methods=['POST'])
def add_category():
    category_name = request.form['category']
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('INSERT INTO categories (name) VALUES (%s) ON CONFLICT DO NOTHING', (category_name,))

    conn.commit()
    cur.close()
    conn.close()
    return redirect('/manage_categories')

@app.route('/delete_category/<int:category_id>')
def delete_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM categories WHERE id = %s', (category_id,))

    conn.commit()
    cur.close()
    conn.close()
    return redirect('/manage_categories')

# Gestione locations
@app.route('/manage_locations')
def manage_locations():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM locations')
    locations = cur.fetchall()

    cur.close()
    conn.close()

    locations.sort(key=lambda x: x[1].lower())

    return render_template('manage_locations.html', locations=locations)

@app.route('/add_location', methods=['POST'])
def add_location():
    location_name = request.form['location']
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('INSERT INTO locations (name) VALUES (%s) ON CONFLICT DO NOTHING', (location_name,))

    conn.commit()
    cur.close()
    conn.close()
    return redirect('/manage_locations')

@app.route('/delete_location/<int:location_id>')
def delete_location(location_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM locations WHERE id = %s', (location_id,))

    conn.commit()
    cur.close()
    conn.close()
    return redirect('/manage_locations')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
