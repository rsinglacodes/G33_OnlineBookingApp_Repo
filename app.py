from flask import Flask, flash, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
import random

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
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(150), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

# Room class definition
class Room(db.Model):
    __tablename__ = "room"

    id = db.Column(db.Integer, primary_key=True)
    hotel_name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image1 = db.Column(db.String(500), nullable=False)
    image2 = db.Column(db.String(500), nullable=False)
    image3 = db.Column(db.String(500), nullable=False)
    image4 = db.Column(db.String(500), nullable=False)
    image5 = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    guests = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Room('{self.hotel_name}', '{self.price}', '{self.location}')"

# Define the user_loader function
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

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email, mobile=mobile, age=age, gender=gender, role='user')
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
            next_page = request.args.get('next')
            return redirect(next_page or url_for("amazing"))
        else:
            if user and user.role == 'admin':
                flash("Invalid admin credentials!", "danger")
            else:
                flash("Invalid credentials!", "danger")

    return render_template("index.html")

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
    return render_template("register.html")

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
    # Fetch all rooms from the database
    rooms = Room.query.all()
    # Generate random ratings and review counts for each room
    room_data = []
    for room in rooms:
        room_data.append({
            'room': room,
            'rating': generate_random_rating(),
            'review_count': generate_review_count()
        })
    return render_template("amazing.html", rooms=room_data)

def generate_random_rating():
    """Generate a random rating between 4.0 and 5.0"""
    return round(random.uniform(4.0, 5.0), 1)

def generate_review_count():
    """Generate a random number of reviews between 5 and 50"""
    return random.randint(5, 50)


@app.route("/rooms/<int:room_id>")
def rooms(room_id):
    room = Room.query.get(room_id)
    if not room:
        flash("Room not found!", "danger")
        return redirect(url_for("amazing"))
    
    # Generate random rating and review count
    rating = generate_random_rating()
    review_count = generate_review_count()
    
    return render_template("rooms.html", room=room, rating=rating, review_count=review_count)


@app.route("/confirm")
@login_required
def confirm():
    # Get query parameters
    room_id = request.args.get('room_id')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    guests = request.args.get('guests')

    # Fetch the room data from the database
    room = Room.query.get(room_id)
    if not room:
        flash("Room not found!", "danger")
        return redirect(url_for("amazing"))

    # Pass the data to the confirm.html template
    return render_template("confirm.html", room=room, check_in=check_in, check_out=check_out, guests=guests)

@app.route("/book", methods=["POST"])
@login_required
def book():
    room_id = request.form.get("room_id")
    room = Room.query.get(room_id)
    if not room:
        flash("Room not found!", "danger")
        return redirect(url_for("amazing"))

    flash("Room booked successfully!", "success")
    return redirect(url_for("amazing"))

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
    return render_template("terms.html")

@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/coming")
@login_required
def coming():
    return render_template("coming.html")

@app.route("/search")
@login_required
def search():
    return render_template("search.html")

@app.route("/data")
@admin_required
@login_required
def data():
    return render_template("data.html")

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    if request.method == "POST":
        current_user.name = request.form.get("name")
        current_user.email = request.form.get("email")
        current_user.mobile = request.form.get("mobile")

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except:
            db.session.rollback()
            flash("Error updating profile. Please try again.", "danger")

    return redirect(url_for("profile"))

@app.route("/delete_profile")
@login_required
def delete_profile():
    try:
        # Store user id before logout
        user_id = current_user.id

        # Log out the user first
        logout_user()

        # Delete user from database
        user = User.query.get(user_id)
        if user:
            # Print for debugging
            print(f"Deleting user: {user.email}")

            # Delete and commit
            db.session.delete(user)
            db.session.commit()

            # Print for debugging
            print("User deleted successfully")
            flash("Your profile has been deleted successfully.", "success")
            return redirect(url_for('home'))
        else:
            flash("User not found.", "danger")
            return redirect(url_for('home'))

    except Exception as e:
        # Print the full error for debugging
        print(f"Error deleting profile: {str(e)}")
        db.session.rollback()
        flash("Error deleting profile. Please try again.", "danger")
        return redirect(url_for('home'))

@app.route("/check_user/<int:user_id>")
def check_user(user_id):
    user = User.query.get(user_id)
    if user:
        return f"User exists: {user.email}"
    return "User not found"

if __name__ == "__main__":
    app.run(debug=True)