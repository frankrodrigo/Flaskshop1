import app
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from database import db
from models.user import User
from models.cart import Cart
from models.product import Product
from forms import RegisterForm, LoginForm, ProductForm, EditProductForm
from functools import wraps
import os

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

app = Flask(__name__)

# PostgreSQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ecommerce_user:strongpassword@localhost/ecommerce_db'
app.config['SECRET_KEY'] = 'Secret123'

# Initialize Bootstrap
Bootstrap5(app)

# Initialize SQLAlchemy and Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Database table creation
with app.app_context():
    db.create_all()


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        elif not current_user.is_admin:
            flash("You're not authorized to view this page")
            return redirect(url_for('index')), 403
        return func(*args, **kwargs)

    return decorated_view


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('display_products'))
    return render_template('index.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user:
            flash("You've already signed up with this email, login instead.", "success")
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(
            form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=email,
            name=form.name.data,
            password=hashed_password,
        )

        if email == "example_email@email.com":
            new_user.is_admin = True

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Registered successfully!", "success")
        return redirect(url_for('display_products'))

    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        password = form.password.data

        if not user:
            flash("Email does not exist. Please try again.", "success")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect. Please try again.", "success")
            return redirect(url_for('login'))

        login_user(user)
        flash("Logged in successfully!", "success")
        return redirect(url_for('display_products'))

    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('index'))


@app.route('/products')
def display_products():
    all_products = Product.query.all()
    return render_template('products.html', all_products=all_products)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
