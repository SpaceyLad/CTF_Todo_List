import db as db_config
from app import app

if __name__ == "__main__":
    db_config.create_todo()
    db_config.create_and_populate_users_db()
    db_config.populate_todo_for_users()
    app.run(host="0.0.0.0", port=5000, debug=True)
