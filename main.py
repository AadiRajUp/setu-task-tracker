from flask import Flask,redirect, url_for,render_template,session,request,jsonify
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime
import sqlite3
import os

# Here we will load all the .env files
load_dotenv() # Loads .env file
FLASK_SECRET_KEY= os.getenv("FLASK_SECRET_KEY")


app = Flask(__name__,static_url_path="/setu/static")
app.secret_key = "YAYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
def getdb():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


# Blueprint section temporary only for admin
from tables import tables_bp
app.register_blueprint(tables_bp)

# Login decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for('getLoginPage'))
        return func(*args, **kwargs)
    return wrapper

@app.get("/setu/")
@login_required
def getMainPage():
    return render_template('index.html')

@app.get("/setu/form")
@login_required
def getFormPage():
    if session["userrole"] not in ["Admin","Supervisor"]:
        return redirect(url_for('getMainPage'))
    return render_template('form.html')

@app.get('/setu/completed')
@login_required
def getCompletedPage():
    return render_template('completed.html')

@app.get('/setu/login')
def getLoginPage():
    error = request.args.get("error")
    return render_template('login.html',error=error)
@app.get('/setu/notices')
@login_required
def getNoticePage():
    return render_template("notice.html")

@app.get('/setu/addnotice')
@login_required
def getAddNoticePage():
    return render_template("addnotice.html")

@app.post('/setu/search')
@login_required
def search():

    # q,visibility,tasktype
    data = request.get_json()
    q = data["q"]
    visibility = data["visibility"]
    tasktype = data["tasktype"]



    # Visibility can only be either public or private
    if visibility not in ["public","private"]:
            return jsonify({"message":"Invalid Request Bad Visibility"}),400

    # checking perms according to role
    if session['userrole']=="Admin":
        if tasktype not in ["assignedtome","assignedbyme","all","absall"]:
            return jsonify({"message":"Invalid Request"}),400
    elif session['userrole']=="Supervisor":
        if tasktype not in ["assignedtome","assignedbyme","all"]:
            return jsonify({"message":"Invalid Request"}),400
    elif session['userrole']=="Volunteer":
        if tasktype not in ["assignedtome","all"]:
            return jsonify({"message":"Invalid Request"}),400
    else:
        return jsonify({"message":"Invalid Role"}),500
    query = """
    SELECT
    tasks.tid,
    tasks.title,
    tasks.description,
    tasks.progress,
    tasks.assigned_date,
    tasks.progress_text,
    tasks.people_working,
    tasks.deadline,
    u1.username AS assigned_to,
    u2.username AS assigned_by
    FROM tasks
    JOIN users u1 ON tasks.assigned_to = u1.uid
    JOIN users u2 ON tasks.assigned_by = u2.uid
    WHERE (tasks.title LIKE ? OR u1.username LIKE ?)
    AND u1.UID LIKE ?
    AND u2.UID LIKE ?
    AND tasks.visibility = ?
    AND tasks.completed = 0;
    """

    task_name = "%"
    assigned_to = "%"
    assigned_by = "%"
    if q != "":
        task_name = q
    if tasktype == "assignedtome":
        assigned_to = int(session["userid"])
    if tasktype == "assignedbyme":
        assigned_by = int(session["userid"])

    if visibility== "private":
        if tasktype=="all":
            return jsonify([])
    conn = getdb()
    rows = conn.execute(query,(f"%{task_name}%",f"%{task_name}%",assigned_to,assigned_by,visibility)).fetchall()
    data = [dict(r) for r in rows]
    conn.close()
    print((f"%{task_name}%",f"%{task_name}%",assigned_to,assigned_by,visibility))
    print(session)
    print(data)
    return jsonify(data)



@app.post('/setu/completedsearch')
@login_required
def completed_search():

    # q,visibility,tasktype
    data = request.get_json()
    q = data["q"]
    visibility = data["visibility"]
    tasktype = data["tasktype"]



    # Visibility can only be either public or private
    if visibility not in ["public","private"]:
            return jsonify({"message":"Invalid Request Bad Visibility"}),400

    # checking perms according to role
    if session['userrole']=="Admin":
        if tasktype not in ["assignedtome","assignedbyme","all","absall"]:
            return jsonify({"message":"Invalid Request"}),400
    elif session['userrole']=="Supervisor":
        if tasktype not in ["assignedtome","assignedbyme","all"]:
            return jsonify({"message":"Invalid Request"}),400
    elif session['userrole']=="Volunteer":
        if tasktype not in ["assignedtome","all"]:
            return jsonify({"message":"Invalid Request"}),400
    else:
        return jsonify({"message":"Invalid Role"}),500
    query = """
    SELECT
    tasks.tid,
    tasks.title,
    tasks.description,
    tasks.progress,
    tasks.assigned_date,
    tasks.progress_text,
    tasks.people_working,
    tasks.deadline,
    u1.username AS assigned_to,
    u2.username AS assigned_by
    FROM tasks
    JOIN users u1 ON tasks.assigned_to = u1.uid
    JOIN users u2 ON tasks.assigned_by = u2.uid
    WHERE (tasks.title LIKE ? OR u1.username LIKE ?)
    AND u1.UID LIKE ?
    AND u2.UID LIKE ?
    AND tasks.visibility = ?
    AND tasks.completed = 1;
    """

    task_name = "%"
    assigned_to = "%"
    assigned_by = "%"
    if q != "":
        task_name = q
    if tasktype == "assignedtome":
        assigned_to = int(session["userid"])
    if tasktype == "assignedbyme":
        assigned_by = int(session["userid"])

    if visibility== "private":
        if tasktype=="all":
            return jsonify([])
    conn = getdb()
    rows = conn.execute(query,(f"%{task_name}%",f"%{task_name}%",assigned_to,assigned_by,visibility)).fetchall()
    data = [dict(r) for r in rows]
    conn.close()
    return jsonify(data)




@app.post("/setu/login")
def login():
    username = request.form["username"].strip()
    password = request.form["password"].strip()

    query = """
    select * from users
    where username = ?
    and password = ?;
    """
    conn= getdb()
    row = conn.execute(query,(username,password)).fetchone()
    conn.close()
    if row is None:
        return redirect(url_for('getLoginPage',error="Incorrect Username or Password"))
    session["userid"]=int(row["UID"])
    session["username"]=row["username"]
    session["userrole"]=row["userclass"]
    return redirect(url_for("getMainPage"))


@app.post("/setu/tasks")
@login_required
def handletask():
    title = request.form["title"]
    description = request.form["description"]
    assigned_to = int(request.form["assignedto"])
    assigned_by = int(session["userid"])
    deadline = datetime.strptime(request.form["deadline"], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
    assigned_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    visibility= request.form["visibility"]

    query = "insert into tasks(title,description,assigned_to,assigned_by,deadline,assigned_date,visibility) values(?,?,?,?,?,?,?)"
    try:
        conn = getdb()
        conn.execute(query, (title, description, assigned_to, assigned_by, deadline, assigned_date,visibility))
        conn.commit()
        return redirect(url_for('getMainPage'))
    except sqlite3.Error as e:
        print(e)
        conn.rollback()
        return redirect(url_for('getMainPage', error="Something went wrong"))
    finally:
        conn.close()

@app.post('/setu/addnotice')
@login_required
def handleNotice():
    title = request.form["title"]
    description = request.form["description"]
    assigned_by = int(session["userid"])
    assigned_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    query = "insert into notices(title,published_date,description,published_by) values(?,?,?,?)"
    try:
        conn = getdb()
        conn.execute(query, (title,  assigned_date, description, assigned_by))
        conn.commit()
        return redirect(url_for('getMainPage'))
    except sqlite3.Error as e:
        print(e)
        conn.rollback()
        return redirect(url_for('getMainPage', error="Something went wrong"))
    finally:
        conn.close()
@app.get("/setu/edit/<tid>")
@login_required
def getEditPage(tid):
    query = """
    select * from tasks
    where tid = ?;
    """
    conn= getdb()
    row = conn.execute(query,(tid,)).fetchone()

    if row is None:
        return redirect(url_for('getMainPage'))
    if row["assigned_to"]!= int(session["userid"]):
        return redirect(url_for('getMainPage'))

    conn.close()
    return render_template("edit.html",task=row)

@app.post("/setu/edit")
@login_required
def edit():
    tid = request.form["tid"]
    progress = request.form["progress"]
    progresstext = request.form["progresstext"]
    peopleworking = request.form["peopleworking"]
    query = """
    select * from tasks
    where tid = ?;
    """
    conn=getdb()
    row = conn.execute(query,(tid,)).fetchone()
    if row is None:
        return redirect(url_for('getMainPage'))
    if row["assigned_to"]!= int(session["userid"]):
        return redirect(url_for('getMainPage')) #access denied that is not yours to edit

    query = "update tasks set progress = ?, progress_text=?, people_working = ? where tid = ?"
    try:
        conn.execute(query, (progress, progresstext, peopleworking, tid))
        conn.commit()
        return redirect(url_for('getMainPage'))
    except sqlite3.Error as e:
        print(e)
        conn.rollback()  # undo any partial changes
        return redirect(url_for('getMainPage'))
    finally:
        conn.close()
        return redirect(url_for('getMainPage'))


@app.post("/setu/delete")
@login_required
def delete():
    data= request.get_json()
    tid = data["tid"]
    query = """
    select * from tasks
    where tid = ?;
    """
    conn=getdb()
    row = conn.execute(query,(tid,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"message": "not found"}), 404
    if row["assigned_by"]!= int(session["userid"]) and session["userrole"]!="Admin":
        return jsonify({"message": "unauthorized"}), 403#access denied that is not yours to delete
    query = "delete from tasks where tid = ?;"
    conn = getdb()
    conn.execute(query,(tid,))
    conn.commit()
    conn.close()
    return jsonify({"message": "ok"}), 200


@app.post("/setu/finish")
@login_required
def finish():
    data= request.get_json()
    tid = data["tid"]
    query = """
    select * from tasks
    where tid = ?;
    """
    conn=getdb()
    row = conn.execute(query,(tid,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"message": "not found"}), 404
    if row["assigned_by"]!= int(session["userid"]) and session["userrole"]!="Admin":
        return jsonify({"message": "unauthorized"}), 403 #access denied that is not yours to decide
    query = "update tasks set completed = 1 where tid = ?;"
    conn = getdb()
    conn.execute(query,(tid,))
    conn.commit()
    conn.close()
    return jsonify({"message": "ok"}), 200
@app.get('/setu/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('getLoginPage'))

@app.post('/setu/notices')
@login_required
def fetch_notice():
    query = """
    SELECT
    notices.nid,
    notices.title,
    notices.description,
    notices.published_date,
    u1.username AS published_by
    FROM notices
    JOIN users u1 ON notices.published_by = u1.uid
    ORDER BY nid DESC;
    """
    conn = getdb()
    rows = conn.execute(query).fetchall()
    data = [dict(r) for r in rows]
    conn.close()
    return jsonify(data)
@app.post('/setu/deletenotice')
@login_required
def delete_notice():
    data= request.get_json()
    nid = data["nid"]
    query = """
    select * from notices
    where nid = ?;
    """
    conn=getdb()
    row = conn.execute(query,(nid,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"message": "not found"}), 404
    if row["published_by"]!= int(session["userid"]) and session["userrole"]!="Admin":
        return jsonify({"message": "unauthorized"}), 403#access denied that is not yours to delete
    query = "delete from notices where nid = ?;"
    conn = getdb()
    conn.execute(query,(nid,))
    conn.commit()
    conn.close()
    return jsonify({"message": "ok"}), 200

@app.errorhandler(500)
def server_error(e):
    return jsonify({"message": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found"}), 404

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)

