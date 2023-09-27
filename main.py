import os

from flask import render_template, request, redirect, make_response
import datetime
import config as conf
import jwt
import subprocess
import db as db_config

# TODO: Good to have: Hash all passwords with sha256
# TODO: Implement AI bot for CTF!

"""
Botten vet hemmeligheter den ikke skal fortelle uansett hva, dette er flaggene. (Lur AI til å fortelle noe bare den vet)
Du må lure botten til å si et spesifikt ord som den skal nekte å si, uansett hva. Om ordet blir sagt, så gir den flagget (Eller et skript som printer flagget)
Når en chat blir laget, så lager botten en header for samtalen (Litt som i GUIet til ChatGPT), denne er sårbar mot XSS fordi input blir ikke sanitert.
"""


# Attack chain
# 1. HTML manipulation
# 2. Understand IDOR and abuse it.
# 3. XSS with post and/or usernames -> Use a proxy to send it to another user!
# 4. admin takeover with post xss cookie stealer.
# 5. JWT secret cracking and CEO takeover.

@conf.app.route('/')
def home():
    return render_template('login.html')


@conf.app.route("/waiting", methods=["GET"])
def waiting():
    token = request.cookies.get('token')
    data = jwt.decode(token, conf.secret_key, algorithms=['HS256'])
    return render_template("wait.html", user=data["user"], group=data["group"])


@conf.app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":

        u = request.form.get('username')
        p = request.form.get('password')
        r = request.form.get('role')

        try:
            db_config.add_user(u, p, r)
        except Exception as e:
            print(f"Could not add the user:\n{e}")
            return render_template('register.html')

        return render_template('login.html', msg="User created! Please log in.")
    else:
        return render_template('register.html')


# The POST request for getting the username and password.
@conf.app.route('/login', methods=['POST'])
def login():
    # Get the information from the user.
    username = request.form.get('username')
    password = request.form.get('password')
    db_users = conf.Users.query.order_by(conf.Users.userId).all()

    for user in db_users:
        if username in user.username and password == user.password:
            # If the username and password is correct, generate JWT with the secret key.
            token = jwt.encode({
                'user': username,
                'group': user.user_group,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
            }, conf.secret_key, algorithm='HS256')
            if user.user_group == "guest":
                resp = make_response(redirect('/waiting'))
            else:
                resp = make_response(redirect('/list'))
            resp.set_cookie('token', token)
            return resp
    return render_template('login.html', error_msg="Invalid credentials")


@conf.app.route("/list", methods=["POST", "GET"])
def index():
    token = request.cookies.get('token')
    data = jwt.decode(token, conf.secret_key, algorithms=['HS256'])
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
        return render_template("list.html", tasks=tasks, user=data["user"], group=data["group"])


@conf.app.route("/connection", methods=["POST", "GET"])
def connect():
    token = request.cookies.get('token')
    data = jwt.decode(token, conf.secret_key, algorithms=['HS256'])
    if data['group'] == 'dev':
        if request.method == "POST":
            try:
                ip = request.form.get('connect')
                command = subprocess.check_output(["ping", ip], shell=True, text=True, stderr=subprocess.STDOUT)
                return render_template("connect.html", command=command, user=data["user"], group=data["group"])
            except:
                return render_template("connect.html", user=data["user"], group=data["group"])
        else:
            return render_template("connect.html", user=data["user"], group=data["group"])


@conf.app.route("/manage_users", methods=["POST", "GET"])
def manage_users():
    token = request.cookies.get('token')
    if not token:
        return redirect('/')
    try:
        data = jwt.decode(token, conf.secret_key, algorithms=['HS256'])
        if data['group'] == 'dev':
            users = conf.Users.query.order_by(conf.Users.userId).all()
            return render_template('manage_users.html', user=data["user"], group=data["group"], users=users)

    except jwt.ExpiredSignatureError:
        return 'Session expired!', 403
    except jwt.InvalidTokenError:
        return 'Invalid token!', 403


@conf.app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = conf.Todo.query.get_or_404(id)
    token = request.cookies.get('token')
    data = jwt.decode(token, conf.secret_key, algorithms=['HS256'])
    try:
        conf.db.session.delete(task_to_delete)
        conf.db.session.commit()
        tasks = conf.Todo.query.order_by(conf.Todo.date_created).all()
        return render_template("list.html", tasks=tasks, user=data["user"], group=data["group"])
    except Exception as e:
        return f"An error occurred while deleting the task: {str(e)}"


@conf.app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    token = request.cookies.get('token')
    data = jwt.decode(token, conf.secret_key, algorithms=['HS256'])
    task = conf.Todo.query.get_or_404(id)

    if request.method == "POST":
        task.content = request.form["content"]

        try:
            conf.db.session.commit()
            tasks = conf.Todo.query.order_by(conf.Todo.date_created).all()
            return render_template("list.html", tasks=tasks, user=data["user"], group=data["group"])
        except Exception as e:
            return f"An error occurred while updating the task: {str(e)}"
    else:
        return render_template("update.html", task=task, user=data["user"], group=data["group"])


# Only users in the "admin" group can access this resource.
@conf.app.route('/admin')
def admin():
    token = request.cookies.get('token')
    if not token:
        return redirect('/')
    try:
        data = jwt.decode(token, conf.secret_key, algorithms=['HS256'])
        if data['group'] == 'admin':
            users = conf.Users.query.order_by(conf.Users.userId).all()
            return render_template('admin.html', user=data["user"], group=data["group"], users=users)
        else:
            tasks = conf.Todo.query.order_by(conf.Todo.date_created).all()
            return render_template("list.html", tasks=tasks, user=data["user"], group=data["group"])
    except jwt.ExpiredSignatureError:
        return 'Session expired!', 403
    except jwt.InvalidTokenError:
        return 'Invalid token!', 403


# A secret place only logged-in users can visit. (To test authentication).
@conf.app.route('/secret')
def secret():
    token = request.cookies.get('token')
    if not token:
        return redirect('/')
    try:
        data = jwt.decode(token, conf.secret_key, algorithms=['HS256'])
        if data['group'] == 'admin' or data['group'] == 'user':
            return render_template('secret.html', user=data["user"], group=data["group"])
        else:
            return make_response(redirect('/'))
    except jwt.ExpiredSignatureError:
        return 'Session expired!', 403
    except jwt.InvalidTokenError:
        return 'Invalid token!', 403


# A logout button that clears the cookie.
@conf.app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('token', '', expires=0)
    return resp


if __name__ == "__main__":
    db_config.create_todo()
    db_config.create_and_populate_users_db()
    conf.app.run(host='0.0.0.0', port=5000, debug=True)
