from flask import Flask,request,redirect,render_template,url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from json import loads,dumps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mock.db"
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100),default=str(uuid4), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    place = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20),nullable=False)
    crops = db.Column(db.String(200))
    model = db.Column(db.String(50))

    def __repr__(self):
        print("<User>")

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        Type = request.form['type']
        place = request.form['place']
        phone = request.form['phone']
        crops = ""
        model = ""
        uid = str(uuid4())
        print(Type)
        checkUser = Users.query.filter_by(username=username).all()
        if len(checkUser) == 0:
            if Type == "farmer":
                crops = "[]"
                model = "NA"
            elif Type == "trucker":
                crops = ""
                model = request.form['model']

            user = Users(uid=uid,username=username,password = password, type=Type,place=place,phone=phone,crops=crops,model=model)
            db.session.add(user)
            db.session.commit()

            resp = make_response(redirect("/"))
            resp.set_cookie("token",uid)
            return resp
        else:
            return "Username in use <a href='/register'>Try again</a>"
    return render_template("register.html")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        attemptedUser = Users.query.filter_by(username=username).first()
        if attemptedUser.password == password:
            resp = make_response(redirect("/"))
            resp.set_cookie("token",attemptedUser.uid)
            return resp
        else:
            return "Wrong password, <a href='/login'>Try again</a>"
    return render_template("login.html")

@app.route("/", methods=["POST","GET"])
def index():
    if request.method == "POST":
        pass
    if request.cookies.get("token") is not None:
        user = Users.query.filter_by(uid=request.cookies.get("token")).first()
        return render_template("index.html", user=user)
    else:
        return redirect("register")
    
@app.route("/crops",methods=["POST","GET"])
def crops():
    user = Users.query.filter_by(uid=request.cookies.get("token")).first()
    if request.method == "POST":
        crop = request.form['crop']
        crops = loads(user.crops)
        crops.append(crop)

        user.crops=dumps(crops)
        db.session.commit()

        return redirect("/crops")

    return render_template("crops.html", user=user, crops=loads(user.crops))

@app.route("/delete-<int:i>")
def delete(i):
    user = Users.query.filter_by(uid=request.cookies.get("token")).first()
    crops = loads(user.crops)
    crops.pop(i)
    user.crops = dumps(crops)
    db.session.commit()
    return redirect("/crops")

@app.route("/truckers")
def truckers():
    truckers = Users.query.filter_by(type="trucker").all()
    return render_template("truckers.html",truckers=truckers)

@app.route("/place-order-<int:id>",methods=["POST","GET"])
def place(id):
    if request.method == "POST":
        crop = request.form['crop']
        farmer = Users.query.filter_by(uid=request.cookies.get("token")).first()
        trucker = Users.query.filter_by(type="trucker").all()[id]
        return "ok"
    uid = request.cookies.get("token")
    trucker = Users.query.filter_by(type="trucker").all()
    trucker = trucker[id]
    farmer = Users.query.filter_by(uid=uid).first()
    return render_template("place.html",trucker=trucker,uid=uid, crops=loads(farmer.crops))
if __name__ == "__main__":
    app.run(debug=True)