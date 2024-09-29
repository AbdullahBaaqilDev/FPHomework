from flask import Flask, render_template, request , redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from random import choices, randint, choice
import re


def create_project_path() -> str:
    support_path = __file__
    project_path_list = support_path.split("\\")[:-1]
    return "\\".join(project_path_list)
PROJECT_PATH = create_project_path()

app = Flask(__name__)

# Configure the database URI for both databases
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/database/users.db"
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), nullable = False)
    birthday = db.Column(db.Date)
    registration_date = db.Column(db.Date)
    username = db.Column(db.String(50), nullable = False)
    password_hash = db.Column(db.String(50), nullable = False)
    
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class ManagedUser(db.Model):
    __tablename__ = "managed_users"
    
    id = db.Column(db.Integer, primary_key = True)
    manager_id = db.Column(db.Integer)
    full_name = db.Column(db.String(50), nullable = False)
    birthday = db.Column(db.Date)
    phone_number = db.Column(db.String(15))

def get_dummy_names(amount: int) -> list[str]:

    full_names = []

    with open(f"{PROJECT_PATH}\\static\\names\\MaleNamesEnglish.txt") as file:
        names = file.read().split("\n")

        for _ in range(amount):
            full_names.append(" ".join(choices(names, k = 3)))

    return full_names

def get_dummy_birthdays(amount: int) -> list[str]:

    birthdays = []

    for _ in range(amount):
        current_year = datetime.now().year
        date = datetime(current_year - randint(18, 100), randint(1, 12), randint(1, 28))
        birthdays.append(date)
    
    return birthdays

def get_dummy_phone_numbers(amount: int) -> list[str]:

    country_code = "+966"
    network_prefixes = ["50", "55", "56", "57", "58"]
    phone_numbers: list[str] = []

    for _ in range(amount):
        prefix = choice(network_prefixes)
        rest_digits = [randint(0, 9) for _ in range(7)]
        
        phone_numbers.append(f"{country_code}{prefix}{''.join(map(str, rest_digits))}")

    return phone_numbers

def create_dummy_info():

    amount = randint(30, 50)
    names = get_dummy_names(amount)
    birthdays = get_dummy_birthdays(amount)
    phone_numbers = get_dummy_phone_numbers(amount)


    for user_data_index in range(amount):

        managed_user = ManagedUser(
            manager_id = randint(1, User.query.count()),
            full_name = names[user_data_index],
            birthday = birthdays[user_data_index],
            phone_number = phone_numbers[user_data_index])
            
        try:
            db.session.add(managed_user)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            print(error)

# with app.app_context(): db.create_all()
# with app.app_context(): create_dummy_info()


user_id = None
user_messages = [("assistant", "إسالني اي سؤال تريد"), ("user", "يعمي انتو مين واحنا مين هل نحن وحدنا؟")]
signing_up_info = {}
sign_up_successful = False


def email_valid(email: str) -> bool:
    """ validates an email address using a regular expression. returns True if valid, False otherwise. """

    # Regular expression pattern for a basic email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def get_managed_users_dict(id: int) -> dict:
    """ return a dict and each element in the dict is another dict that contains manager_id, full_name, birthday and phone_number """
    
    user_dict = {}
    managed_users = ManagedUser.query.filter_by(manager_id = id)
    if not managed_users: return {}

    for user in managed_users:
        user_dict[user.id] = {
            "manager_id": user.manager_id,
            "full_name": user.full_name,
            "birthday": user.birthday,
            "phone_number": user.phone_number
        }

    return user_dict

def render_page(html_name: str, page_name: str, **kwargs) -> str:
    """ like render_template but always passes active_page and user_id parameters """

    return render_template(html_name, active_page = page_name, user_id = user_id, **kwargs)


@app.route("/")
def index():
    return redirect("/log-in")

@app.route("/home")
def home():
    if user_id:
        return render_page("home.html", "home")
    return redirect("/")

@app.route("/log-in", methods = ["POST", "GET"])
def log_in():
    global user_id, sign_up_successful
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username = username).first()
        
        if not user:
            return render_page("log_in.html", "log_in", msg = "User not found. Please check your username.")

        if not user.check_password(password):
            return render_page("log_in.html", "log_in", msg = "Incorrect password. Please try again.")
        
        user_id = user.id
        return redirect("/home")
            
    else:
        if sign_up_successful:
            sign_up_successful = False
            return render_page("log_in.html", "log_in", msg = "Signed up successfully")
        return render_page("log_in.html", "log_in", msg = False)

@app.route("/log-out")
def log_out():
    global user_id, signing_up_info, user_messages
    
    user_id = None
    signing_up_info = {}
    user_messages = []
    return redirect("/")

@app.route("/sign-up")
def sign_up():
    global sign_up_successful, signing_up_info

    required_keys = {"email", "username", "password"}
    if not required_keys.issubset(signing_up_info.keys()):
        return redirect("/sign-up/step1")

    new_user = User(email = signing_up_info["email"], username = signing_up_info["username"], registration_date = datetime.now(), birthday = signing_up_info.get("birthday", None))
    new_user.set_password(signing_up_info["password"])

    try:
        db.session.add(new_user)
        db.session.commit()
        sign_up_successful = True
        signing_up_info = {}
        return redirect("/log-in")
    except Exception as e:
        db.session.rollback()
        return f"Error creating user: {str(e)}"
    
@app.route("/sign-up/step1", methods = ["POST", "GET"])
def sign_up_step1():
    global signing_up_info

    if request.method == "POST":
        new_email = request.form["email"]
        new_password = request.form["password"]
        new_confirmed_password = request.form["confirm_password"]


        if not email_valid(new_email):
            return render_page("sign_up_1.html", "sign_up_1", msg = "Email isn't valid. Example: user@example.com")
        
        if User.query.filter_by(email = new_email).first():
            return render_page("sign_up_1.html", "sign_up_1", msg = "Email already registered. You can directly log in.")

        if not new_password == new_confirmed_password:
            return render_page("sign_up_1.html", "sign_up_1", msg = "You didn't repeat the password correctly. Make sure that thay are the same")

        if len(new_password) < 8:
            return render_page("sign_up_1.html", "sign_up_1", msg = "Your password length must be 8 characters or more")

        signing_up_info["email"] = new_email
        signing_up_info["password"] = new_password

        return redirect("/sign-up/step2")
    else:
        if signing_up_info:
            return render_page("sign_up_1.html", "sign_up", infos = signing_up_info)
        return render_page("sign_up_1.html", "sign_up")
    
@app.route("/sign-up/step2", methods = ["POST", "GET"])
def sign_up_step2():
    global signing_up_info

    if request.method == "POST":
        new_username = request.form.get("username")
        new_birth_year = request.form.get("year")
        new_birth_month = request.form.get("month")
        new_birth_day = request.form.get("day")


        if User.query.filter_by(username = new_username).first():
            return render_page("sign_up_2.html", "sign_up_2", date_now = datetime.now(), msg = "Username already registered. Try another one.")

        if len(new_username) < 8:
            return render_page("sign_up_2.html", "sign_up_2", date_now = datetime.now(), msg = "Your username length must be 8 characters or more")

        signing_up_info["username"] = new_username
        if new_birth_year and new_birth_month and new_birth_day:
            signing_up_info["birthday"] = datetime(int(new_birth_year), int(new_birth_month), int(new_birth_day))

        return redirect("/sign-up")
    else:
        return render_page("sign_up_2.html", "sign_up", date_now = datetime.now())

@app.route("/profile/<int:id>")
def profile(id: int = None):
    if user_id == id:
        user = User.query.get(id)
        if user.birthday: birthday = user.birthday.strftime("%Y/%m/%d")
        else: birthday = "Unknown"
        return render_page("profile.html", "profile", name = user.username, birthday = birthday, registration_date = user.registration_date.strftime("%Y/%m/%d"), users_count = ManagedUser.query.filter_by(manager_id = id).count())
    else: return redirect("/")

@app.route("/users-database/<int:id>")
def users_database(id: int = None):
    if user_id == id:
        return render_page("users_database.html", "users_database", maneged_users = get_managed_users_dict(id))
    else: return redirect("/")

@app.route("/about")
def about():
    if user_id:
        return render_page("about.html", "about")
    else: return redirect("/")

@app.route("/contact-us")
def contact_us():
    if user_id:
        return render_page("contact_us.html", "contact_us", messages = user_messages)
    else: return redirect("/")

@app.route("/error-page")
def error_page():
    if user_id:
        return render_page("error_page.html", "error")
    else: return redirect("/")


if __name__ == "__main__":
    app.run(debug = True)