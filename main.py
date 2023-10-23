from flask import render_template, request, redirect, make_response, send_from_directory
import datetime
import config as conf
import jwt
import subprocess
import db as db_config
from functools import wraps


# Attack chain part 1 - Initial access and web application takeover
# 1. HTML manipulation
# 2. Broken access control. with Gobuster
# 3. Understand IDOR and abuse it.
# 4. XSS with post and/or usernames -> Use a proxy to send it to another user!
# 5. admin takeover with post xss cookie stealer.

# Attack chain part 2 - System access and takeover
# 6. JWT secret cracking and CEO takeover.
# 7. LFI vulnerability to read system files. Find secrets.
# 8. RCE to execute commands. Open a reverse shell.


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect("/")
        try:
            data = jwt.decode(token, conf.secret_key, algorithms=["HS256"])
            return f(data=data, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return "Session expired!", 403
        except jwt.InvalidTokenError:
            return "Invalid token!", 403

    return decorated_function


@conf.app.route("/")
def home():
    return render_template("login.html")


@conf.app.route("/waiting", methods=["GET", "POST"])
@jwt_required
def waiting(data):
    if request.method == "POST":
        try:
            file = request.form.get("file")
            command = subprocess.check_output(
                f"type {file}", shell=True, text=True, stderr=subprocess.STDOUT
            )
            return render_template(
                "wait.html",
                command=command,
                user=data["user"],
                group=data["group"],
            )
        except:
            return render_template(
                "wait.html", user=data["user"], group=data["group"]
            )
    else:
        return render_template(
            "wait.html", user=data["user"], group=data["group"]
        )


@conf.app.route('/image/<image_name>')
def serve_image(image_name):
    return send_from_directory('images', image_name)


@conf.app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            db_config.add_user(
                request.form.get("username"),
                request.form.get("password"),
                request.form.get("role"),
            )
        except Exception as e:
            print(f"Could not add the user:\n{e}")
            return render_template("register.html")
        return render_template("login.html", msg="User created! Please log in.")
    else:
        return render_template("register.html")


# The POST request for getting the username and password.
@conf.app.route("/login", methods=["POST"])
def login():
    # Get the information from the user.
    username = request.form.get("username")
    password = request.form.get("password")
    db_users = conf.Users.query.order_by(conf.Users.userId).all()

    for user in db_users:
        if username in user.username and password == user.password:
            # If the username and password is correct, generate JWT with the secret key.
            token = jwt.encode(
                {
                    "user": username,
                    "group": user.user_group,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                },
                conf.secret_key,
                algorithm="HS256",
            )
            if user.user_group == "guest":
                resp = make_response(redirect("/waiting"))
            else:
                resp = make_response(redirect("/list"))
            resp.set_cookie("token", token)
            return resp
    return render_template("login.html", error_msg="Invalid credentials")


@conf.app.route("/list", methods=["POST", "GET"])
@jwt_required
def index(data):
    if request.method == "POST":
        new_task = conf.Todo(content=request.form["content"], user=data["user"])
        try:
            conf.db.session.add(new_task)
            conf.db.session.commit()
            return redirect("/list")
        except Exception as e:
            return f"An error occurred while creating the task: {str(e)}"
    else:
        tasks = conf.Todo.query.order_by(conf.Todo.date_created).all()
        return render_template(
            "list.html", tasks=tasks, user=data["user"], group=data["group"]
        )


@conf.app.route("/connection", methods=["POST", "GET"])
@jwt_required
def connect(data):
    if data["group"] == "dev":
        if request.method == "POST":
            try:
                ip = request.form.get("connect")
                command = subprocess.check_output(
                    f"ping {ip}", shell=True, text=True, stderr=subprocess.STDOUT
                )
                return render_template(
                    "connect.html",
                    command=command,
                    user=data["user"],
                    group=data["group"],
                )
            except:
                return render_template(
                    "connect.html", user=data["user"], group=data["group"]
                )
        else:
            return render_template(
                "connect.html", user=data["user"], group=data["group"]
            )


@conf.app.route("/manage_users", methods=["POST", "GET"])
@jwt_required
def manage_users(data):
    if data["group"] == "dev":
        users = conf.Users.query.order_by(conf.Users.userId).all()
        return render_template(
            "manage_users.html", user=data["user"], group=data["group"], users=users
        )


@conf.app.route("/delete/<int:id>")
@jwt_required
def delete(id, data):
    try:
        conf.db.session.delete(conf.Todo.query.get_or_404(id))
        conf.db.session.commit()
        tasks = conf.Todo.query.order_by(conf.Todo.date_created).all()
        return render_template(
            "list.html", tasks=tasks, user=data["user"], group=data["group"]
        )
    except Exception as e:
        return f"An error occurred while deleting the task: {str(e)}"


@conf.app.route("/update/<int:id>", methods=["GET", "POST"])
@jwt_required
def update(id, data):
    task = conf.Todo.query.get_or_404(id)

    if request.method == "POST":
        conf.Todo.query.get_or_404(id).content = request.form["content"]

        try:
            conf.db.session.commit()
            tasks = conf.Todo.query.order_by(conf.Todo.date_created).all()
            return render_template(
                "list.html", tasks=tasks, user=data["user"], group=data["group"]
            )
        except Exception as e:
            return f"An error occurred while updating the task: {str(e)}"
    else:
        return render_template(
            "update.html", task=task, user=data["user"], group=data["group"]
        )


# Only users in the "admin" group can access this resource.
@conf.app.route("/admin")
@jwt_required
def admin(data):
    if data["group"] == "admin":
        users = conf.Users.query.order_by(conf.Users.userId).all()
        return render_template(
            "admin.html", user=data["user"], group=data["group"], users=users
        )
    else:
        tasks = conf.Todo.query.order_by(conf.Todo.date_created).all()
        return render_template(
            "list.html", tasks=tasks, user=data["user"], group=data["group"]
        )


# A secret place only logged-in users can visit. (To test authentication).
@conf.app.route("/secret")
@jwt_required
def secret(data):
    if data["group"] == "admin" or data["group"] == "user":
        return render_template(
            "secret.html", user=data["user"], group=data["group"]
        )
    else:
        return make_response(redirect("/"))


# A logout button that clears the cookie.
@conf.app.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    resp.set_cookie("token", "", expires=0)
    return resp


if __name__ == "__main__":
    db_config.create_todo()
    db_config.create_and_populate_users_db()
    db_config.populate_todo_for_users()
    conf.app.run(host="0.0.0.0", port=5000, debug=True)
