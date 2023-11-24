import sqlite3
import random

db_path = 'instance/list.db'


def create_todo():
    # Only run this to reset the database file!
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS todo')

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

    cursor.execute('DROP TABLE IF EXISTS users')

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
        ("TheBoss", "0321498r7nxy34871ryyufhfgu", "ceo"),
        ("Jennifer", "1F1xTh1ng5", "dev"),
        ("oskar", "sc4nd1p4ss1", "user"),
        ("lina", "2sc4nd1nav14", "user"),
        ("freja", "fr3yj4_pass", "user"),
        ("emil", "3m1l_scandinav", "user"),
        ("karin", "k4r1n_987", "user"),
        ("joakim", "j0ak1m_654", "user"),
        ("sofia", "s0f1a_pass", "user"),
        ("larssen", "la77sen_sure", "user"),
        ("maja", "m4j4_pwd", "user"),
        ("victor", "v1ct0r_231", "user"),
        ("astrid", "a5tr1d_456", "user"),
        ("johan", "j0han_789", "user"),
        ("linnea", "l1nnea_101", "user"),
        ("nikolaj", "n1k0laj_202", "user"),
        ("gustav", "gu5tav_303", "user"),
        ("elise", "3l1se_404", "user"),
        ("mathias", "math1a5_505", "user"),
        ("ingrid", "1ngr1d_606", "user"),
        ("erik", "er1k_707", "user"),
        ("siri", "s1ri_808", "user"),
        ("siri", "flag{y0u_f0unD_tHe_u5er_l1st}", "user")
    ]

    # Insert the user data into the table
    cursor.executemany('''
    INSERT INTO users (username, password, user_group) VALUES (?, ?, ?)
    ''', users_data)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def add_user(u, p, r):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert the user data into the table
    users_data = (str(u), str(p), str(r))
    print(users_data)
    cursor.execute("INSERT INTO users (username, password, user_group) VALUES (?, ?, ?)", users_data)

    conn.commit()
    conn.close()


def populate_todo_for_users():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all users
    cursor.execute("SELECT username FROM users")
    user_names = cursor.fetchall()

    # Default todos to be added for each user
    default_todo = "Welcome! This is your first todo."

    # Sample todos for randomization
    sample_todos = [
        "Buy groceries",
        "Finish report",
        "Meet with Sarah at 2pm",
        "Pay electricity bill",
        "Schedule doctor appointment",
        "Book flight tickets",
        "Plan weekend getaway",
        "Send out meeting invites",
        "Clean the house",
        "Renew gym membership",
        "Call mom",
        "flag{l1st_h4ck3r!}"
    ]

    # For each user, add the default todo
    for user_name in user_names:
        cursor.execute("INSERT INTO todo (content, user) VALUES (?, ?)", (default_todo, user_name[0]))

        # Randomly assign additional todos for users
        additional_todos_count = random.randint(1, 5)  # add between 1 to 5 additional todos
        for _ in range(additional_todos_count):
            content = random.choice(sample_todos)
            cursor.execute("INSERT INTO todo (content, user) VALUES (?, ?)", (content, user_name[0]))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_todo()
    create_and_populate_users_db()
    populate_todo_for_users()
