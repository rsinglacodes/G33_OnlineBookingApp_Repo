from flask import Flask, flash, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Access denied!", "danger")
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "website.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

# User class definition
class User(db.Model, UserMixin):
    __tablename__ ="user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable =True)
    gender = db.Column(db.String(150), nullable = True)
    password_hash = db.Column(db.String(256), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.id}', '{self.name}', '{self.email}', '{self.age}', '{self.gender}', '{self.mobile}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

    # Check if an admin user already exists
    if not User.query.filter_by(role="admin").first():
        admin_user = User(name="Admin", email="admin@gmail.com", mobile="1234567890", role="admin")
        admin_user.set_password("admin123")  # Set a default password
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created with email: admin@gmail.com and password: admin123")


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        age = request.form.get("age")
        gender = request.form.get("gender")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        mobile = request.form.get("mobile")


        print("name",name)

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email, mobile=mobile, age=age, gender=gender, role='user')  # Set role to 'user'
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    

    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("homepage"))  # Redirect to homepage, or desired location
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")  # Assuming you have a login.html template

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    user = db.session.get(User, id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")
    else:
        flash("User not found!", "danger")
    return redirect(url_for("register"))

@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    user = db.session.get(User, id)
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("homepage"))
    
    if request.method == "POST":
        user.name = request.form.get("name")
        user.age = request.form.get("age")
        user.email = request.form.get("email")
        user.gender = request.form.get("gender")
        user.mobile = request.form.get("mobile")

        db.session.add(user)
        db.session.commit()
        flash("User details updated!", "success")
        return redirect(url_for("amazing"))

    return render_template("update.html", user=user)


@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template("data.html")

@app.route("/homepage")
@login_required
def homepage():
    return render_template("homepage.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/contact")
@login_required
def contact():
    return render_template("contact.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/amazing")
@login_required
def amazing():
    return render_template("amazing.html")

@app.route("/beach")
@login_required
def beach():
    return render_template("beach.html")

@app.route("/luxury")
@login_required
def luxury():
    return render_template("luxury.html")

@app.route("/feedback")
@login_required
def feedback():
    return render_template("feedback.html")

@app.route("/setting")
@login_required
def setting():
    return render_template("setting.html")

@app.route("/term")
def term():
    return render_template("term.html")

if __name__ == "__main__":
    app.run(debug=True)
