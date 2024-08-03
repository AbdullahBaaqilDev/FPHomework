from flask import Flask, render_template, request , redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from random import randint
from re import match


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
    __bind_key__ = "users"
    __abstract__ = True
    
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

    def create_user_table(user_table_id: int) -> object:

        class UserTable(db.Table):
            __tablename__ = f"user_table_{user_table_id}"

            id = db.Column(db.Integer, primary_key = True)
            name = db.Column(db.String(100), nullable = False)
            birthday = db.Column(db.Date)
            phone_number = db.Column(db.String(10))

        inspector = inspect(db.engine)
        existing_table = inspector.has_table(UserTable.__tablename__)
        if not existing_table:
            db.create_all()

        return UserTable
    
    def get_user_table(user_table_id: int) -> object:
        return User.create_user_table(user_table_id)

def create_dummy_info():

    for user_data_index in range(randint(30, 50)):
        
        UserTable = User.create_user_table(user_data_index)
        table = UserTable(name = "Abdullah Mohammed Hussain", birthday = "2008/12/27", phone_number = "+966532364335")
            
        try:
            db.session.add(table)
            db.session.commit()
        except Exception:
            db.session.rollback()
# with app.app_context(): create_dummy_info()


user_id = None
signing_up_info = {}
sign_up_successful = False


def email_valid(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return match(pattern, email) is not None

def get_users_dict(id: int) -> dict:
    user_dict = {}
    for user in User.get_user_table(id).query.all():
        user_dict[user.id] = {
            'name': user.name,
            'birthday': user.birthday,
            'phone_number': user.phone_number
        }
    return user_dict

def render_page(html_name: str, page_name: str, **kwargs) -> str:
    return render_template(html_name, active_page = page_name, user_id = user_id, **kwargs)


@app.route("/")
def index():
    return redirect("/sign-up/step1")

@app.route("/sign-up", methods = ["POST"])
def sign_up():
    global sign_up_successful

    if request.method == "POST":

        required_keys = {"email", "username", "password"}
        if not required_keys.issubset(signing_up_info.keys()):
            return redirect("/sign-up/step1")

        # Create a new user
        new_user = User(email = signing_up_info["email"], username = signing_up_info["username"], registration_date = datetime.now(), birthday = signing_up_info.get("birthday", None))
        new_user.set_password(signing_up_info["password"])

        try:
            db.session.add(new_user)
            db.session.commit()
            sign_up_successful = True
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
            return render_page("sign_up_1.html", "sign_up_1", failed = "Email isn't valid. Example: user@example.com")
        
        if User.query.filter_by(email = new_email).first():
            return render_page("sign_up_1.html", "sign_up_1", failed = "Email already registered. You can directly log in.")

        if not new_password == new_confirmed_password:
            return render_page("sign_up_1.html", "sign_up_1", failed = "You didn't repeat the password correctly. Make sure that thay are the same")

        if len(new_password) < 8:
            return render_page("sign_up_1.html", "sign_up_1", failed = "Your password length must be 8 characters or more")

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
            return render_page("sign_up_2.html", "sign_up_2", failed = "Username already registered. Try another one.")

        if len(new_username) < 8:
            return render_page("sign_up_2.html", "sign_up_2", failed = "Your username length must be 8 characters or more")

        signing_up_info["username"] = new_username
        if new_birth_year and new_birth_month and new_birth_day:
            signing_up_info["birthday"] = datetime(int(new_birth_year), int(new_birth_month), int(new_birth_day))

        return redirect("/sign-up")
    else:
        return render_page("sign_up_2.html", "sign_up", date_now = datetime.now())
    

if __name__ == "__main__":
    app.run(debug = True)