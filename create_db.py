import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Creiamo la tabella categories
    cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Creiamo la tabella locations
    cursor.execute('''
        CREATE TABLE locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Creiamo la tabella items
    cursor.execute('''
        CREATE TABLE storage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            spot TEXT,
            notes TEXT,
            category_id INTEGER,
            location_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
    ''')

    conn.commit()
    conn.close()
    
    print("Database and table with category created successfully!")

if __name__ == "__main__":
    init_db()
