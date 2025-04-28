from flask import Flask, render_template, request, redirect
import sqlite3

def setup_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create categories table
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    ''')

    # Create locations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    ''')

    # Insert initial categories
    c.execute("INSERT OR IGNORE INTO categories (name) VALUES ('Altro')")
    c.execute("INSERT OR IGNORE INTO categories (name) VALUES ('Viaggio')")
    c.execute("INSERT OR IGNORE INTO categories (name) VALUES ('Vestiti')")

    # Insert initial locations
    c.execute("INSERT OR IGNORE INTO locations (name) VALUES ('Solaio Nonno')")
    c.execute("INSERT OR IGNORE INTO locations (name) VALUES ('Garage Tatona')")
    c.execute("INSERT OR IGNORE INTO locations (name) VALUES ('Garage Tatina')")
    c.execute("INSERT OR IGNORE INTO locations (name) VALUES ('Solaio Nostro')")

    conn.commit()
    conn.close()

# Run the setup when app starts
setup_db()

app = Flask(__name__)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # This makes the data easier to use
    return conn

# Home page to add new items
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()

    categories = conn.execute('SELECT * FROM categories').fetchall()
    locations = conn.execute('SELECT * FROM locations').fetchall()

    if request.method == 'POST':
        item = request.form['item']
        location_id = request.form['location']
        spot = request.form['spot']
        notes = request.form['notes']
        category_id = request.form['category']

        conn.execute('''
            INSERT INTO storage (item, location_id, spot, notes, category_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (item, location_id, spot, notes, category_id))
        conn.commit()
        conn.close()

        return redirect('/list')

    conn.close()
    return render_template('index.html', categories=categories, locations=locations)

# Page to list all items
@app.route('/list')
def list_items():
    q = request.args.get('q', '')  # Get the search query
    location_filter = request.args.get('location', '')  # Get the selected location filter
    reset = request.args.get('reset', '')  # Check if reset is clicked
    
    # If reset is clicked, clear both filters
    if reset:
        q = ''
        location_filter = ''

    conn = get_db_connection()

    # Fetch locations for the dropdown
    locations = conn.execute('SELECT * FROM locations').fetchall()
    
    # Base query for storage items
    query = 'SELECT storage.*, categories.name AS category_name, locations.name AS location_name FROM storage'
    params = []
    
    # Join with categories and locations tables to get names
    query += ' LEFT JOIN categories ON storage.category_id = categories.id'
    query += ' LEFT JOIN locations ON storage.location_id = locations.id'


    # Apply filters if search query is provided
    if q:
        query += ' WHERE storage.item LIKE ? OR storage.notes LIKE ? OR locations.name LIKE ?'
        params = ['%' + q + '%', '%' + q + '%', '%' + q + '%']

    # Apply location filter if selected
    if location_filter:
        if 'WHERE' in query:
            query += ' AND storage.location_id = ?'
        else:
            query += ' WHERE storage.location_id = ?'
        params.append(location_filter)

    # Execute the query with filters applied
    items = conn.execute(query, params).fetchall()
    conn.close()

    # Render the list template with the correct filter values
    return render_template('list.html', items=items, locations=locations, location_filter=location_filter, search_query=q)

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    conn = get_db_connection()

    categories = conn.execute('SELECT * FROM categories').fetchall()
    locations = conn.execute('SELECT * FROM locations').fetchall()

    if request.method == 'POST':
        item = request.form['item']
        location_id = request.form['location']
        spot = request.form['spot']
        notes = request.form['notes']
        category_id = request.form['category']

        conn.execute('''
            UPDATE storage
            SET item = ?, location_id = ?, spot = ?, notes = ?, category_id = ?
            WHERE id = ?
        ''', (item, location_id, spot, notes, category_id, item_id))
        conn.commit()
        conn.close()
        return redirect('/list')

    item = conn.execute('SELECT * FROM storage WHERE id = ?', (item_id,)).fetchone()
    conn.close()

    return render_template('edit.html', item=item, categories=categories, locations=locations)

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM storage WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect('/list')

# Route to display categories and manage them
@app.route('/manage_categories')
def manage_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()

    categories.sort(key=lambda x: x['name'].lower())

    return render_template('manage_categories.html', categories=categories)

# Route to manage adding categories
@app.route('/add_category', methods=['POST'])
def add_category():
    category_name = request.form['category']
    conn = get_db_connection()
    conn.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
    conn.commit()
    conn.close()
    return redirect('/manage_categories')

# Route to delete a category
@app.route('/delete_category/<int:category_id>')
def delete_category(category_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    conn.commit()
    conn.close()
    return redirect('/manage_categories')


# Route to display locations and manage them
@app.route('/manage_locations')
def manage_locations():
    conn = get_db_connection()
    locations = conn.execute('SELECT * FROM locations').fetchall()
    conn.close()

    locations.sort(key=lambda x: x['name'].lower())

    return render_template('manage_locations.html', locations=locations)

# Route to manage adding locations
@app.route('/add_location', methods=['POST'])
def add_location():
    location_name = request.form['location']
    conn = get_db_connection()
    conn.execute('INSERT INTO locations (name) VALUES (?)', (location_name,))
    conn.commit()
    conn.close()
    return redirect('/manage_locations')

# Route to delete a location
@app.route('/delete_location/<int:location_id>')
def delete_location(location_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM locations WHERE id = ?', (location_id,))
    conn.commit()
    conn.close()
    return redirect('/manage_locations')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
