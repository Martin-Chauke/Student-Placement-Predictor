import pickle
import numpy as np
from flask import Flask, request, render_template, flash, session,redirect, url_for
#from flask_sqlalchemy import SQLAlchemy
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from functools import wraps

# Load the .env file
load_dotenv()


# Initialize Flask app
app = Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","dev_secret") # fall back to "dev_secret " if not found

#setup the database(sqlite) 
DATABASE="users.db"

def get_db_connection():
    conn=sqlite3.connect(DATABASE)
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    conn=get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
    )""")
   # conn.execute("DROP TABLE IF EXISTS placed_students") removes the created table
    #Create placed _students table if it doesn't exist
    conn.execute("""
    CREATE TABLE IF NOT EXISTS placed_students(
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        User_id INTEGER,
        Student_name TEXT NOT NULL,
        CGPA REAL,
        IQ_level REAL,
        Profile_score REAL,
        FOREIGN KEY(User_id) REFERENCES users(id)
    )""")

    #create default admin if not exists
    admin=conn.execute("SELECT * FROM users WHERE username=?",("admin",)).fetchone()
    if not admin:
        hashed_password=generate_password_hash("m@rtinch@uke")
        conn.execute("INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
                     ("Martin", "chaukemartin1301@gmail.com", hashed_password, 1)
                     )
    conn.commit()
    conn.close()



#This decorator restricts access to admin users only
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        conn.close()
        if not user or user["is_admin"] != 1:
            flash("Admin access required.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return wrapper

# Admin dashboard: view and remove users
@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    if request.method=="POST":
        user_id=request.form.get("remove_user_id")
        
        # prevent admin from deleting themselves
        if user_id and int(user_id)!=session["user_id"]:
            conn.execute("DELETE FROM users WHERE ID=? AND is_admin=0",(user_id,))
            conn.commit()
            flash("User removed.","success")
        elif user_id:
            flash("You cannot remove your self.","warning")

    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return render_template("admin_dashboard.html", users=users)

# Register route
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
         
        # check if user exists
        #user=User.query.filter_by(username=username).first()

        conn=get_db_connection()
        user=conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user:
            flash("Username already exists!","danger")
            conn.close()
            return redirect(url_for("register"))
        
        # Hash the password and   Create a new user
        hashed_password = generate_password_hash(password,method="pbkdf2:sha256")
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
             (username,email, hashed_password))
        conn.commit()
        conn.close()

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# Authentication login code
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        #user=User.query.filter_by(username=username).first()
        conn=get_db_connection()
        user=conn.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone()
        if user and check_password_hash(user["password"],password):
            session["user_id"]=user["id"]
            session["username"]=user["username"]
            flash("Login successful!","success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password","danger")
            return redirect(url_for("login"))
    
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.","info")
    return redirect(url_for("login"))

#protect routes (only logged-in users can access)
def login_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.","warning")
            return redirect(url_for("login"))
        return f(*args,**kwargs)
    return wrapper

# Load pretrained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
@login_required
def home():
    user_id=session.get("user_id")
    conn=get_db_connection()
    placed_students=conn.execute("SELECT * FROM placed_students WHERE User_id=?",(user_id,)
                                 ).fetchall()
    conn.close()
    return render_template("index.html", username=session.get("username"),placed_students=placed_students)

# This is a route to view placed students for the logged-in user
@app.route("/my_placed_students")
@login_required
def my_placed_students():
    user_id=session.get("user_id")
    conn=get_db_connection()
    placed_students=conn.execute("SELECT * FROM placed_students WHERE User_id=?", (user_id,)).fetchall()
    conn.close()
    return render_template("my_placed_students.html", placed_students=placed_students)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Collect form data
        cgpa = float(request.form["cgpa"])
        iq = float(request.form["iq"])
        profile_score = float(request.form["profile_score"])
        
        #Back end range validation
        if not (0 <= cgpa <= 10):
            flash("CGPA must be between 0 and 10.", "danger")
            raise ValueError("CGPA out of range!")

        if not (50 <= iq <= 200):
            flash("IQ must be between 50 and 200.", "danger")
            raise ValueError("IQ out of range!")

        if not (0 <= profile_score <= 100):
            flash("Profile Score must be between 0 and 100.", "danger")
            raise ValueError("Profile Score out of range!")

        features = np.array([[cgpa, iq, profile_score]])
        prediction = model.predict(features)[0]
        
        #Default variables
        recommendation=""

        if prediction == 1:
            placement_status = "Placed ✅"
            status = "success"
            text_color = "text-success"
            
            #Career planning  recommendation for placed students
            recommendation=(
                "Splendid work! Keep enhancing your technical skills and consider exploring internships and trainings, leadership opportunities, higher studies."
            )


            #Save the placed student
            name=request.form.get("student_name","Unknown")
            user_id=session.get("user_id")
            conn=get_db_connection()

            # Check if the student exists already(duplicates)
            existing=conn.execute("" \
            "SELECT * FROM placed_students WHERE User_id=? AND Student_name=?",(user_id,name)
            ).fetchone()
            if existing:
                flash("This student has been admitted by you.")
            else:
                conn.execute("INSERT INTO placed_students (User_id,Student_name, CGPA, IQ_level, Profile_score) VALUES (?, ?, ?, ?, ?)",
                         (user_id, name, cgpa, iq, profile_score)
                         )
            
                conn.commit()
            flash("Student details added successfully.")
            conn.close()
            #print("Student details added successfully.")

        else:
            placement_status = "Not Placed ❌"
            status = "danger"
            text_color = "text-danger"
            name=request.form.get("student_name","Unknown")
            # Career planning recommendation for not placed students
            if cgpa<6.5:
                recommendation="Focus on improving your academic performance (CGPA)."
            elif iq<100:
                recommendation="Work on problem-solving and analytical skills through practice and " \
                "aptitude training."
            elif profile_score< 50:
                recommendation="Build a stronger profile with internships, projects, or certifications."
            else:
                recommendation="Seek personalized career counseling to identify specific areas for improvement."

        # Render result template
        return render_template("result.html", 
                               placement_status=placement_status,
                               confidence="(Probability not available for this model)",
                               status=status,
                               text_color=text_color,
                               cgpa=cgpa, iq=iq, profile_score=profile_score,
                               recommendation=recommendation,
                               student_name=name)

    except Exception as e:
        return render_template("result.html", 
                               placement_status="Error",
                               confidence=str(e),
                               status="warning",
                               text_color="text-warning")

if __name__ == "__main__":
    init_db() #Ensure the users table exists
    app.run(debug=True)
