from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    UserMixin,
    current_user,
    login_required,
)

base_dir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)

# initialize app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "blog.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "3hjdunhe87fh4nf98"

db = SQLAlchemy(app)

login_manager = LoginManager(app)

# creating the user database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)

    def __repr__(self) -> str:
        return f" <User : {self.username} >"


# creating the database for the article
class Blog(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.Integer(), unique=True)
    article = db.Column(db.Text(), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"author - {self.author}, content-{self.content} "


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


@app.route("/")
def index():
    # user = User.query.filter_by("username").all()
    return render_template("index.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/home")
def home():
    users_blog = Blog.query.all()
    return render_template("home.html", users_blog=users_blog)


# creating a route for editing the article
@app.route("/update/<int:id>/", methods=["POST", "GET"])
def update_blog(id):
    blog_to_update = Blog.query.get_or_404(id)
    if request.method == "POST":
        blog_to_update.title = request.form.get("title")
        blog_to_update.article = request.form.get("article")

        db.session.commit()
        # coming back to this
        return redirect(url_for("home"))
    return render_template("edit.html")


@app.route("/blog/<int:id>/")
def blog_post(id):
    blog_post = Blog.query.filter_by(id=id).first()
    return render_template("blog.html", blog_post=blog_post)


@app.route("/about")
def about_page():
    return "<h2> about the home page </h2>"


@app.route("/delete/<int:id>/", methods=["GET", "POST"])
def delete_post(id):
    blog_to_delete = Blog.query.get_or_404(id)
    db.session.delete(blog_to_delete)
    db.session.commit()


# creating route for a user login
@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for("create_post"))
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        email_exist = User.query.filter_by(email=email).first()
        if email_exist:
            return redirect(url_for("register"))
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for("register"))
        password_hash = generate_password_hash(password)

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password_hash=password_hash,
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get("title")
        article = request.form.get("article")
        author = current_user.get_id()
        author_int = int(author)
        blog = Blog(title=title, article=article, author=author_int)
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)
