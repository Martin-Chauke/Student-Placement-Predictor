import pickle
import numpy as np
from flask import Flask, request, render_template, flash, session,redirect, url_for
#from flask_sqlalchemy import SQLAlchemy
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime
#import random


INTERVENTIONS_NOTIFICATIONS=[
    # Academics
    {"category": "Academics", "message": "📘 Recommend remedial classes for students with consistently low CGPA."},
    {"category": "Academics", "message": "📚 Encourage faculty-led study groups for academically weak students."},
    {"category": "Academics", "message": "📝 Introduce peer tutoring programs to help students improve coursework performance."},
    {"category": "Academics", "message": "🔬 Suggest mini-projects in core subjects to strengthen practical understanding."},
    {"category": "Academics", "message": "📊 Track academic progress regularly and share with students for self-improvement."},

    # Aptitude
    {"category": "Aptitude", "message": "🧩 Organize aptitude training sessions to support students with weak logical reasoning."},
    {"category": "Aptitude", "message": "🧮 Arrange weekly quantitative reasoning practice tests."},
    {"category": "Aptitude", "message": "🎯 Encourage students to participate in inter-college aptitude competitions."},
    {"category": "Aptitude", "message": "🧠 Provide free access to aptitude question banks and e-learning resources."},
    {"category": "Aptitude", "message": "📅 Schedule regular mock aptitude assessments to track progress."},

    # Profile Building
    {"category": "Profile", "message": "💼 Encourage internships and project work to boost student profiles."},
    {"category": "Profile", "message": "🌐 Suggest students contribute to open-source projects for hands-on experience."},
    {"category": "Profile", "message": "📜 Promote industry-recognized certifications in technical and soft skills."},
    {"category": "Profile", "message": "🛠️ Help students build digital portfolios showcasing their projects."},
    {"category": "Profile", "message": "🎓 Invite alumni to share strategies for improving placement readiness."},

    # Soft Skills
    {"category": "Soft Skills", "message": "🗣️ Conduct communication skills workshops for students with weak verbal ability."},
    {"category": "Soft Skills", "message": "🤝 Arrange group discussions to improve teamwork and collaboration skills."},
    {"category": "Soft Skills", "message": "🎤 Provide public speaking and presentation practice opportunities."},
    {"category": "Soft Skills", "message": "📖 Share resources on writing professional emails and resumes."},
    {"category": "Soft Skills", "message": "💬 Host mock HR interviews to build student confidence."},

    # Career Counseling
    {"category": "Career Counseling", "message": "🎯 Plan one-on-one counseling for borderline students to identify focus areas."},
    {"category": "Career Counseling", "message": "🔍 Identify individual strengths and weaknesses through career assessments."},
    {"category": "Career Counseling", "message": "📆 Create personalized career roadmaps for students not meeting placement standards."},
    {"category": "Career Counseling", "message": "👥 Pair students with faculty mentors for continuous guidance."},
    {"category": "Career Counseling", "message": "🧭 Organize career awareness sessions on diverse job roles and industries."},

    # Technical
    {"category": "Technical", "message": "💻 Offer coding bootcamps for students with weak programming foundations."},
    {"category": "Technical", "message": "⚙️ Conduct technical workshops aligned with industry demands."},
    {"category": "Technical", "message": "📟 Encourage hackathon participation to apply problem-solving skills."},
    {"category": "Technical", "message": "🛠️ Introduce short-term courses on emerging technologies (AI, Data Science, Cloud)."},
    {"category": "Technical", "message": "🔗 Facilitate collaboration with industry professionals for skill sessions."},

    # Placement Prep
    {"category": "Placement Prep", "message": "📝 Arrange resume-building and mock interview workshops for final-year students."},
    {"category": "Placement Prep", "message": "📑 Share past placement papers and solutions for structured practice."},
    {"category": "Placement Prep", "message": "📹 Record mock interviews to provide constructive feedback."},
    {"category": "Placement Prep", "message": "🎯 Encourage timed problem-solving practice to simulate real test conditions."},
    {"category": "Placement Prep", "message": "📊 Analyze placement test results to tailor support for weak areas."},

    # General Support
    {"category": "Support", "message": "🤝 Facilitate mentorship programs pairing seniors with struggling students."},
    {"category": "Support", "message": "🏆 Recognize and reward incremental improvements in placement readiness."},
    {"category": "Support", "message": "📌 Display placement preparation tips on department notice boards."},
    {"category": "Support", "message": "📢 Provide weekly newsletters with job market updates and resources."},
    {"category": "Support", "message": "📅 Organize monthly career talks with industry leaders."},

    # Industry Exposure
    {"category": "Industry Exposure", "message": "🏭 Arrange industrial visits to help students connect theory with practice."},
    {"category": "Industry Exposure", "message": "🌍 Host company webinars to expose students to real-world expectations."},
    {"category": "Industry Exposure", "message": "🔧 Encourage participation in skill-based online competitions."},
    {"category": "Industry Exposure", "message": "🧑‍🏫 Partner with industries for live projects and case studies."},
    {"category": "Industry Exposure", "message": "📈 Share labor market trends with faculty and students for informed planning."},

    # Wellness
    {"category": "Wellness", "message": "🧘 Provide stress management and wellness workshops during placement season."},
    {"category": "Wellness", "message": "🎶 Organize cultural and recreational events to maintain student morale."},
    {"category": "Wellness", "message": "🏃 Encourage physical fitness as part of holistic placement preparation."},
    {"category": "Wellness", "message": "💡 Share success stories of past students to inspire current batches."},
    {"category": "Wellness", "message": "🙌 Celebrate small wins in placement practice to keep students motivated."},

    # Data Monitoring
    {"category": "Data Monitoring", "message": "📊 Use placement prediction trends to identify common weak factors in students."},
    {"category": "Data Monitoring", "message": "📈 Track student improvements after interventions to assess effectiveness."},
    {"category": "Data Monitoring", "message": "🗂️ Maintain detailed records of each student’s placement preparation journey."},
    {"category": "Data Monitoring", "message": "🧾 Provide quarterly reports to faculty for planning academic interventions."},
    {"category": "Data Monitoring", "message": "📍 Compare department placement readiness with institutional benchmarks."}
]


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


# Notification function
def get_daily_notification():
    today=datetime.now().timetuple().tm_yday # day of the year.
    index=today % len(INTERVENTIONS_NOTIFICATIONS) # Rotate the notifiction for eac
    return INTERVENTIONS_NOTIFICATIONS[index]


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
            session["is_admin"]=user["is_admin"]

            # Pick a random  intervention notification (Placement Insight of the Day)
           # notification=random.choice(INTERVENTIONS_NOTIFICATIONS)
            #session["daily_notification"]=notification  #Store in session 

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

    #Get daily notification from session(if any available for all users)
    notification=get_daily_notification()
    return render_template("index.html", 
                           username=session.get("username"),
                           placed_students=placed_students,
                           notification=notification)
     

# This is a route to view placed students for the logged-in user
@app.route("/my_placed_students")
@login_required
def my_placed_students():
    user_id=session.get("user_id")
    conn=get_db_connection()
    placed_students=conn.execute("SELECT * FROM placed_students WHERE User_id=?", (user_id,)).fetchall()
    conn.close()
    return render_template("my_placed_students.html", placed_students=placed_students)


#This route implements the deletion or editing of the students
#Manage placed students(Edit / Delete)
@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM placed_students WHERE Id=? AND User_id=?",
        (student_id, session["user_id"])
    ).fetchone()

    if not student:
        conn.close()
        flash("Student not found or you do not have permission.", "danger")
        return redirect(url_for("my_placed_students"))

    if request.method == "POST":
        name = request.form.get("student_name")
        cgpa = request.form.get("cgpa")
        iq = request.form.get("iq")
        profile_score = request.form.get("profile_score")

        # Basic validation if the student name has been passed
        if not name:
            flash("Student name is required.", "warning")
            return redirect(url_for("edit_student", student_id=student_id))

        conn.execute("""
            UPDATE placed_students
            SET Student_name=?, CGPA=?, IQ_level=?, Profile_score=?
            WHERE Id=? AND User_id=?
        """, (name, cgpa, iq, profile_score, student_id, session["user_id"]))
        conn.commit()
        conn.close()
        flash("Student details updated successfully.", "success")
        return redirect(url_for("my_placed_students"))

    conn.close()
    return render_template("edit_student.html", student=student)


@app.route("/delete_student/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM placed_students WHERE Id=? AND User_id=?",
        (student_id, session["user_id"])
    ).fetchone()

    if not student:
        conn.close()
        flash("Student not found or you do not have permission.", "danger")
        return redirect(url_for("my_placed_students"))

    conn.execute("DELETE FROM placed_students WHERE Id=? AND User_id=?",
                 (student_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Student removed successfully.", "info")
    return redirect(url_for("my_placed_students"))



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
                "This student demonstrates a strong likelihood of placement based on academic and profile indicators." \
                 "<<Intervention>>: Guide them toward advanced opportunities such as leadership programs, higher studies counseling, or specialized training for niche roles."
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
                recommendation="The student’s CGPA is below typical placement thresholds. " \
                "<<Intervention>>: Recommend remedial academic support, peer-assisted study groups, and structured coaching to improve subject mastery."
            elif iq<100:
                recommendation="The aptitude/IQ score is below industry expectations. " \
                " <<Intervention>>: Organize aptitude development workshops, logical reasoning practice sessions, and encourage participation in mock aptitude tests."
            elif profile_score< 50:
                recommendation="The profile score suggests limited industry exposure or skills. " \
                     "<<Intervention>>: Advise internships, industry projects, hackathons, and online certifications (e.g., technical skills, communication training) to strengthen employability."
            else:
                recommendation="The student’s profile is balanced but still below placement readiness standards. " \
                "<<Intervention>>: Recommend one-on-one counseling to design a tailored career plan, including resume workshops, mock interviews, and soft-skills development"

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
