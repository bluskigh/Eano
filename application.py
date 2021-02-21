from flask import Flask, session, request, render_template, redirect, jsonify, make_response
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
import json
from datetime import datetime


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

db = SQL("sqlite:///users.db")

def createProgressToday():
    date = datetime.now().strftime("%d-%m-%Y")
    if len(db.execute("SELECT amnt FROM done WHERE user_id=? AND day=?", session["user_id"], date)) == 0:
        db.execute("INSERT INTO done (done_id, user_id, amnt, day) VALUES(NULL, ?, 0, ?)", session["user_id"], date)

@app.route("/")
def index():
    if session:
        return redirect("/main")
    return render_template("index.html", s=session, home=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return "Password did not match"

        # check if the user exists
        if len(db.execute("SELECT id FROM users WHERE username=?", username)):
            return "That username is taken"

        pass_hash = generate_password_hash(confirmation)
        db.execute("INSERT INTO users VALUES(?, ?, ?, ?)", None, username, pass_hash, 5)
        return redirect("/login")

    return render_template("login.html", loginpage=False, header="Sign Up", f=True, s=session, home=False, title="EANO | Login")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")

        # scan the database for username, compare the passwords
        obj = db.execute("SELECT * FROM users WHERE username=?", username)
        if len(obj) and obj[0]["username"] == username and check_password_hash(obj[0]["password"], request.form.get("password")):
            session["user_id"] = obj[0]["id"]
            session["username"] = obj[0]["username"]
            return redirect("/main")
    return render_template("login.html", loginpage=True, header="Log In", f=True, s=None, home=False, title="EANO | Login")

@app.route("/main", methods=["POST", "GET"])
def main():
    FOLDER = False
    f_id = None
    info = None
    if request.method == "POST":
        if request.get_json():
            obj = request.get_json()
            FOLDER = obj["foldername"]
            folderType = obj["folderType"]
            startAmnt = int(obj["startAmount"])

            # add to the database
            if FOLDER and folderType and startAmnt>=0:
                # check if the folder does not exist in the database
                if len(db.execute("SELECT f_id FROM folders WHERE title=? AND user_id=?", FOLDER, session["user_id"])) == 0:
                    db.execute("INSERT INTO folders (f_id, user_id, title, amnt) VALUES(NULL, ?, ?, ?)", session["user_id"], FOLDER, startAmnt)
                    if startAmnt > 0:
                        # get id of newly created folder
                        f_id = int(db.execute("SELECT f_id FROM folders WHERE title=? AND user_id=? AND amnt=? LIMIT 1", FOLDER, session["user_id"], startAmnt)[0]["f_id"])
                        # create notes and insert them into notes, using the new f_id
                        for note in range(startAmnt):
                            db.execute("INSERT INTO notes (note_id, folder_id, title, desc, priority) VALUES(NULL, ?, ?, ?, ?)", f_id, "Todo {}".format(note), "You automatically generated me :) <3", note)
                else:
                    # let the user know that it a folder with that name already exist
                    return make_response(jsonify({"message":"EXIST"}), 401)
            else:
                # let the user know that invalid keyword arguments were entered
                return make_response(jsonify({"message":"ERROR"}), 409)

            # everything was added fine.
            return make_response(jsonify({"message":"OK"}), 200)

        # user has added a new todo to his collection
        if request.form.get("todoname"):
            priority = int(request.form.get("priority"))
            desc = request.form.get("desc")
            FOLDER = request.form.get("todoFolder")
            f_id= int(db.execute("SELECT f_id FROM folders WHERE title = ? AND user_id = ?", FOLDER, session["user_id"])[0]["f_id"])
            db.execute("INSERT INTO notes (note_id, folder_id, title, desc, priority) VALUES(NULL, ?, ?, ?, ?)", f_id, request.form.get("todoname"), desc, priority)
            amnt = int(db.execute("SELECT amnt FROM folders WHERE user_id = ? AND title = ?", session["user_id"], FOLDER)[0]["amnt"])
            db.execute("UPDATE folders SET amnt = amnt + 1 WHERE f_id = ? AND user_id = ?", f_id, session["user_id"])
        # user has selected a folder from his collection
        elif request.form.get("picked") or request.form.get("deleteFolder"):
            r = request.form.get("information").split(",")
            user_id = int(r[1])
            f_id = int(r[2])
            FOLDER = r[0]
            if request.form.get("deleteFolder"):
                db.execute("DELETE FROM folders WHERE f_id = ? AND user_id = ? AND title = ?", f_id, user_id, FOLDER)
                # delete todos in that folder
                db.execute("DELETE FROM notes WHERE folder_id = ?", f_id)
                FOLDER = None
        elif request.form.get("information"):
            r = request.form.get("information").split(",")
            FOLDER = r[0]
            info = [r[1], r[2], r[3], r[4], r[5]]
            f_id = int(r[5])
            if request.form.get("delete") or request.form.get("done"):
                isChecked = False
                if request.form.get("done"):
                    isChecked = True
                    createProgressToday()
                    date = datetime.now().strftime("%d-%m-%Y")
                    # if len(db.execute("SELECT done_id FROM done WHERE user_id = ? AND day = ?", session["user_id"], date)) == 0:
                    #     # insert into the database
                    #     db.execute("INSERT INTO done (done_id, user_id, amnt, day) VALUES(NULL, ?, 0, ?)", session["user_id"], date)
                    # add one to the done for the day
                    db.execute("UPDATE done SET amnt = amnt + 1 WHERE user_id = ? AND day = ?", session["user_id"], date)

                # add to the history database
                db.execute("INSERT INTO history (history_id, user_id, folder_id, folder, title, desc, priority, isChecked) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], f_id, FOLDER, r[1], r[2], r[3], isChecked)

                # delete from the database
                db.execute("DELETE FROM notes WHERE note_id=? AND folder_id = ? AND title=?", int(r[4]), f_id, r[1])
                if int(db.execute("SELECT amnt FROM folders WHERE f_id=? AND user_id=?", f_id, session["user_id"])[0]["amnt"]) > 0:
                    db.execute("UPDATE folders SET amnt = amnt - 1 WHERE f_id=? AND user_id=? ", f_id, session["user_id"])
                info=None

        try:
            f_id= int(db.execute("SELECT f_id FROM folders WHERE title = ? AND user_id = ?", FOLDER, session["user_id"])[0]["f_id"])
        except:
            pass

    # TODO: when deleting a folder, also delete all the todo that were in that folder

    TODOS = db.execute("SELECT * FROM notes WHERE folder_id = ?", f_id)
    FOLDERS = db.execute("SELECT * FROM folders WHERE user_id = ?", session["user_id"])
    return render_template("main.html", s=session, todos=TODOS, folders=FOLDERS, folder=FOLDER, pickedTodoInfo=info, title="EANO | Home")

@app.route("/update", methods=["POST"])
def update():
    elements = request.form.get("folder").split(",")
    FOLDER = elements[0]
    note_id = elements[1]
    newTitle = request.form.get("title")
    newDesc = request.form.get("desc")
    newPriority = request.form.get("priority")

    f_id= int(db.execute("SELECT f_id FROM folders WHERE title = ? AND user_id = ?", FOLDER, session["user_id"])[0]["f_id"])
    if newTitle:
        db.execute("UPDATE notes SET title = ? WHERE note_id = ? AND folder_id = ?", newTitle, note_id, f_id)
    if newDesc:
        db.execute("UPDATE notes SET desc = ? WHERE note_id = ? AND folder_id = ?", newDesc, note_id, f_id)
    if newPriority:
        db.execute("UPDATE notes SET priority = ? WHERE note_id = ? AND folder_id = ?", newPriority, note_id, f_id)

    TODOS = db.execute("SELECT * FROM notes WHERE folder_id = ?", f_id)
    FOLDERS = db.execute("SELECT * FROM folders WHERE user_id = ?", session["user_id"])
    return render_template("main.html", s=session, todos=TODOS, folders=FOLDERS, folder=FOLDER, title="EANO | Home")

@app.route("/error")
def error():
    return "{}".format(request.args.get("message"))



@app.route("/progress")
def progress():
    # just in case there has been no progress created for the current day
    createProgressToday()

    dailyGoal = int(db.execute("SELECT dailyGoal FROM users WHERE id= ?", session["user_id"])[0]["dailyGoal"])
    obj = db.execute("SELECT * FROM done WHERE user_id = ?", session["user_id"])
    # need list, to consider the case when the user does not stop using this application after a day, which needs to keep track of every day, and so we are going to calculate the percentage of goal met thus day
    DONE = []
    for key in obj:
        doneAmnt = int(key['amnt'])
        p = (int(doneAmnt * 100) / dailyGoal)
        key["p"] = p
        DONE.append(key)

    return render_template("progress.html", s=session, done=DONE, h=False, title="EANO | Progress")

@app.route("/options", methods=["POST", "GET"])
def options():
    if request.method == "POST":
        # update the dailygoal amount for the current user
        amnt = int(request.form.get("update"))
        db.execute("UPDATE users SET dailyGoal = ? WHERE id = ?", amnt, session["user_id"])
        return redirect("/")
    return render_template("options.html", s=session, title="EANO | Options")

@app.route("/history")
def history():
    ITEMS = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])
    return render_template("progress.html", h=True, items=ITEMS, s=session, title="EANO | History")

@app.route("/undo", methods=["POST"])
def undo():
    if request.method == "POST":
        r = request.get_json()
        obj = r

        if r.get("delete") or r.get("addFolder"):
            obj = r["data"]

        folderTitle = obj["folderTitle"]

        if r.get("addFolder"):
            # create the folder, then add that to the folder
            db.execute("INSERT INTO folders (f_id, user_id, title, amnt) VALUES(NULL, ?, ?, 0)", session["user_id"], folderTitle)

        f_id = obj["folderId"]
        historyId = obj["historyId"]
        title = obj["title"]
        desc = obj["desc"]
        priority = obj["priority"]
        isChecked = int(obj["isChecked"])

        # add 1 to the folder, if it still exists
        ### send back error, saying that folder does not exist anymore, would you like to create it again?
        ##### if yes, create it again, add it there, etc.
        # add to the notes of the folder
        # delete from history

        # if not going to delete
        if r.get("delete") == None:
            # just to make sure

            # check to see if the folder exist
            if len(db.execute("SELECT f_id FROM folders WHERE user_id = ? AND title=?", session["user_id"], folderTitle)) == 0:
                return make_response(jsonify({"message":"Does not exist."}), 501)

            f_id = int(db.execute("SELECT f_id FROM folders WHERE title=? AND user_id=?", folderTitle, session["user_id"])[0]["f_id"])

            # since the fodler exist, add one to its amnt, and add note to its corressponding folder_id
            db.execute("UPDATE folders SET amnt = amnt + 1 WHERE title= ? AND user_id = ? LIMIT 1", folderTitle, session["user_id"])

            # add to the notes
            db.execute("INSERT INTO notes (note_id, folder_id, title, desc, priority) VALUES(NULL, ?, ?, ?, ?)", f_id, title, desc, priority)

        # if its a checked todo type, then remove from the amnt of done for the current day
        if isChecked:
            date = datetime.now().strftime("%d-%m-%Y")
            db.execute("UPDATE done SET amnt = amnt - 1 WHERE user_id = ? AND day = ?", session["user_id"], date)

        # will always occur when undoing, albeit, when not undoing, but still deleting... or undoing, so still removing from history
        db.execute("DELETE FROM history WHERE history_id = ? AND user_id = ?", historyId, session["user_id"])
        # on the page, it will delete it using javascript
        return make_response(jsonify({"message":"OK"}), 200)

    return make_response(jsonify({"message":"OK"}), 200)

@app.route("/account", methods=["POST", "GET"])
def account():
    if request.method == "POST":
        obj = request.get_json()
        username = None
        if obj.get("username"):
            username = obj["username"]
        password = None
        confirmation = None
        if obj.get("password"):
            password = obj["password"]
            if obj.get("confirmation"):
                confirmation = obj["confirmation"]
            else:
                return make_response(jsonify({"message":"Confirmation not provided."}), 406)

        print("Password: {}".format(password))
        print("COnfirmation: {}".format(confirmation))

        if password != confirmation:
            return make_response(jsonify({"message":"ERROR", "reason":"Confirmation did not match."}), 409)
            # return jsonify({"message":"Confrmation incorrect."})

        if password:
            # password did match, so update it in the users database
            # check if the password given is the same as his old password
            if check_password_hash(db.execute("SELECT password FROM users WHERE id=?", session["user_id"])[0]["password"], confirmation):
                return make_response(jsonify({"message":"Password's same."}), 501)

            # password are the same, so update it
            db.execute("UPDATE users SET password = ? WHERE id = ? LIMIT 1", generate_password_hash(confirmation), session["user_id"])

        # if user provided username to update, update it
        if username:
            # check if the username is equal to his current username
            if db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[0]["username"] == username:
                return make_response(jsonify({"message":"Same username."}), 501)
            # check fi the username exists already
            if len(db.execute("SELECT username FROM users WHERE username = ?", username)):
                return make_response(jsonify({"message":"Already exists"}), 409)
            # username is not the same, so update his username
            db.execute("UPDATE users SET username = ? WHERE id = ? LIMIT 1", username, session["user_id"])
            session["username"] = username

        # everything went well, so return 200 okay status code.
        return make_response(jsonify({"message":"OK"}), 200)
    return render_template("account.html", s=session, title="EANO | Account")

@app.route("/sort", methods=["POST"])
def sort():
    obj =  request.get_json()
    if obj:
        option = obj["option"]
        folder = obj["folder"]

        f_id = int(db.execute("SELECT f_id FROM folders WHERE title = ? AND user_id = ?", folder, session["user_id"])[0]["f_id"])
        todos = db.execute("SELECT * FROM notes WHERE folder_id=?", f_id)
        for todo in todos:
            print("\n{}".format(todo))
        length = len(todos)
        indexes = [x for x in range(length)]

        if option == '1':
            # desc priority
            for i in range(length):
                current = todos[i]
                for z in range(i, length):
                    currentZ = todos[z]

                    if currentZ["priority"] > current["priority"]:
                        temp = indexes[i]
                        indexes[i] = indexes[z]
                        indexes[z] = temp
                        current, currentZ = currentZ, current
                        todos[i] = current
                        todos[z] = currentZ
        elif option == '2':
            # asc priority
            for i in range(length):
                current = todos[i]
                for z in range(i, length):
                    currentZ = todos[z]
                    if currentZ["priority"] < current["priority"]:
                        temp = indexes[i]
                        indexes[i] = indexes[z]
                        indexes[z] = temp
                        current, currentZ = currentZ, current
                        todos[i] = current
                        todos[z] = currentZ

        elif option == '3':
            # title
            for i in range(length):
                current = todos[i]
                for z in range(i, length):
                    currentZ = todos[z]
                    if currentZ["title"] < current["title"]:
                        temp = indexes[i]
                        indexes[i] = indexes[z]
                        indexes[z] = temp
                        current, currentZ = currentZ, current
                        todos[i] = current
                        todos[z] = currentZ
    else:
        return make_response(jsonify({"message":"ERROR"}), 409)

    print(indexes)

    response = make_response(jsonify({"message":"OK", "body":indexes}), 200)
    return response