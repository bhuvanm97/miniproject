from flask import Flask,render_template,redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userdb.db"
app.config["SQLALCHEMY_BINDS"] = {
    "RepoDB": "sqlite:///repodb.db",
    "FileDB": "sqlite:///filedb.db"
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "/Users/bhuvanm/Desktop/miniproject/static/files"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class UserDB(db.Model):
    userName = db.Column(db.String(20),primary_key=True)
    userPassword = db.Column(db.String(100),nullable=False)
    userFirstName = db.Column(db.String(50),nullable=False)
    userLastName = db.Column(db.String(50),nullable=False)
    userEmailID = db.Column(db.String(100),nullable=False)
    userDOB = db.Column(db.String(20),nullable=False)

    def __repr__(self) -> str:
        return f"{self.userName}"

class RepoDB(db.Model):
    __bind_key__ = 'RepoDB'
    id = db.Column(db.Integer, primary_key=True)
    userN = db.Column(db.String(20),nullable=False)
    nameOfRepo = db.Column(db.String(50),nullable = False)
    dateCreated = db.Column(db.DateTime,default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.id}"

class FileDB(db.Model):
    __bind_key__ = "FileDB"
    id = db.Column(db.Integer, primary_key=True)
    userAndRepoName = db.Column(db.String(100),nullable=False)
    fileName = db.Column(db.Text,nullable=False)
    name = db.Column(db.String(50),nullable=False)
    desc = db.Column(db.String(200))
    mimetype = db.Column(db.Text,nullable=False)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        if UserDB.query.filter_by(userName=request.form["un"]).first() is None:
            usern = request.form["un"]
            userpwd = request.form['up']
            usereid = request.form["ueid"]
            userdob = request.form["udob"]
            userfn = request.form["ufn"]
            userln = request.form["uln"]
            if userpwd != request.form["cp"]:
                return render_template("register.html",x=3)
            hashed_userpwd = bcrypt.generate_password_hash(userpwd,14)
            user = UserDB(userName=usern,userPassword=hashed_userpwd,userFirstName=userfn,userLastName=userln,userEmailID=usereid,userDOB=userdob)
            db.session.add(user)
            db.session.commit()
            return render_template("register.html",x=2)
        return render_template("register.html",x=1)
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        usern = request.form["una"]
        if UserDB.query.filter_by(userName=usern).first() is not None:
            userpwd = request.form['upa']
            if bcrypt.check_password_hash(UserDB.query.filter_by(userName=usern).first().userPassword, userpwd):
                return redirect(f"/profile/{usern}")
            else:
                return render_template("login.html",x=1)
        else:
            return render_template("login.html",x=1)

        
    return render_template("login.html")

@app.route("/profile/<string:uName>")
def profile(uName):
    user = UserDB.query.filter_by(userName=uName).first()
    repos = RepoDB.query.filter_by(userN=uName).all()
    return render_template("profile.html",user=user,repos=repos)

@app.route("/profile/<string:uName>/createrepo",methods=["GET","POST"])
def createRepo(uName):
    if request.method == "POST":
        repo = RepoDB(userN=uName,nameOfRepo=request.form["rn"])
        db.session.add(repo)
        db.session.commit()
        return redirect(f"/profile/{uName}")
    return render_template("createRepo.html",username=uName)

@app.route("/profile/<string:uName>/<int:repoID>")
def repo(uName,repoID):
    files = FileDB.query.filter_by(userAndRepoName=uName+str(repoID)).all()
    return render_template("repo.html",username=uName,repoID=repoID,files=files)

@app.route("/profile/<string:uName>/<int:repoID>/upload",methods=["GET","POST"])
def fileUpload(uName,repoID):
    File = request.files["file"]
    
    fName = File.filename.split(".")
    File.filename = fName[0] + str(datetime.utcnow) + "." + fName[1]
    fName = secure_filename(File.filename)
    File.save(os.path.join(app.config["UPLOAD_FOLDER"],fName))
    mimetype = File.mimetype
    file = FileDB(userAndRepoName=uName+str(repoID),fileName=fName,name=request.form["fileName"],desc=request.form["fileDesc"],mimetype=mimetype)
    db.session.add(file)
    db.session.commit()
    return redirect(f"/profile/{uName}/{repoID}")


if __name__ == "__main__":
    app.run(debug=True)