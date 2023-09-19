import sqlite3

db_path = 'instance/list.db'


def create_todo():

    # Only run this to reset the database file!
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #cursor.execute('DROP TABLE todo')

    cursor.execute('''
    CREATE TABLE todo (
        id INTEGER PRIMARY KEY,
        content VARCHAR(200) NOT NULL,
        completed INTEGER DEFAULT 0,
        date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
        user VARCHAR(100)
    )
    ''')

    cursor.execute('''
    INSERT INTO todo(id, content, completed, date_created)
    SELECT id, content, completed, date_created FROM todo
    ''')

    conn.commit()
    conn.close()


def create_and_populate_users_db():

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        userId INTEGER PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        user_group VARCHAR(50) NOT NULL
    )
    ''')

    # User data to be inserted
    users_data = [
        ("pål", "hr_ansatt1", "user"),
        ("morten", "it_ansatt3", "user"),
        ("flag_bærer_john", "54s6e5cdrf9872bgex8712gex97y3diu32hd3o487o3", "user"),
        ("admin", "admin123", "admin"),
        ("TheBoss", "0321498r7nxy34871ryyufhfgu", "user")
    ]

    # Insert the user data into the table
    cursor.executemany('''
    INSERT INTO users (username, password, user_group) VALUES (?, ?, ?)
    ''', users_data)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_and_populate_users_db()