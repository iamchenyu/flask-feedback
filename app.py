from sqlalchemy.exc import IntegrityError, NoResultFound
from flask import Flask, render_template, redirect, flash, session, request, url_for
from models import connect_db, db, User, Feedback
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserRegisterForm, UserLoginForm, UserEditForm, FeedbackForm
from decouple import config
from werkzeug.exceptions import Unauthorized, NotFound
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = config("SECRET_KEY")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404&405.html"), 404


@app.errorhandler(401)
def not_authorized(e):
    return render_template("401.html"), 401


@app.errorhandler(405)
def not_authorized(e):
    return render_template("404&405.html"), 405


@app.route("/")
def homepage():
    feedback = Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template("homepage.html", feedback=feedback)


@app.route("/register", methods=["GET", "POST"])
def register_user():
    if "user" in session:
        flash("Please log out first", "alert-warning")
        return redirect(f"/users/{session['user']}")

    form = UserRegisterForm()

    if form.validate_on_submit():
        data = {key: value for key, value in form.data.items(
        ) if key is not "confirm" and key is not "csrf_token"}
        new_user = User.register(**data)

        db.session.add(new_user)
        try:
            db.session.commit()

            session["user"] = new_user.username
            session["is_admin"] = False

            flash(f"Welcome, {new_user.username}!", "alert-success")
            return redirect(f"/users/{new_user.username}")

        except IntegrityError as e:
            db.session.rollback()
            if "users_username_key" in str(e):
                form.username.errors = ["username already exists"]
            if "users_email_key" in str(e):
                form.email.errors = ["email address already exists"]

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    if "user" in session:
        flash("You already logged in", "alert-warning")
        return redirect(f"/users/{session['user']}")

    form = UserLoginForm()

    if form.validate_on_submit():
        username = form.data["username"]
        password = form.data["password"]

        try:
            user = User.authenticate(username, password)

            if user:
                session["user"] = user.username
                session["is_admin"] = user.is_admin
                flash(f"Welcome, {username}!", "alert-success")
                return redirect(f"/users/{username}")

        except ValueError:
            form.password.errors = [
                "Invalid password. Please try again."]

        except NameError:
            form.username.errors = [
                "Invalid username. Please try again."]

    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout_user():
    if "user" not in session:
        flash("Please log in first", "alert-danger")
        return redirect("/login")

    flash(f"Goodbye, {session['user']}!", "alert-success")
    session.pop("user")
    session.pop("is_admin")
    return redirect("/login")


@app.route("/users/<username>")
def show_user(username):
    if "user" not in session:
        flash("Please log in first", "alert-danger")
        return redirect("/login")

    user = User.query.filter_by(username=username).first()

    if not user:
        raise NotFound

    return render_template("user_page.html", user=user)


@app.route("/users/<username>/update", methods=["GET", "POST"])
def update_user(username):
    if "user" not in session:
        flash("Please log in first", "alert-danger")
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    form = UserEditForm(obj=user)

    if not user:
        raise NotFound

    if session["user"] == username or session["is_admin"]:
        if form.validate_on_submit():
            user.username = form.data["username"]
            user.email = form.data["email"]
            user.first_name = form.data["first_name"]
            user.last_name = form.data["last_name"]
            db.session.add(user)

            try:
                db.session.commit()
                return redirect(f"/users/{user.username}")

            except IntegrityError as e:
                db.session.rollback()
                if "users_username_key" in str(e):
                    form.username.errors = ["username already exists"]
                if "users_email_key" in str(e):
                    form.email.errors = ["email address already exists"]
    else:
        raise Unauthorized

    return render_template("update_user_page.html", form=form, user=user)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    if "user" not in session:
        flash("Please log in first", "alert-danger")
        return redirect("/login")

    if session["user"] == username or session["is_admin"]:
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()

        if session["user"] == username:
            session.pop("user")
            session.pop("is_admin")
        flash(f"User {user.username} has been deleted",
              "alert-success")
        return redirect("/")

    else:
        raise Unauthorized


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    if "user" not in session:
        flash("Please log in first", "alert-danger")
        return redirect("/login")

    user = User.query.filter_by(username=username).first()
    form = FeedbackForm()

    if session["user"] == username or session["is_admin"]:
        if form.validate_on_submit():
            feedback = Feedback(
                title=form.data["title"], content=form.data["content"], user_id=user.id)

            db.session.add(feedback)
            db.session.commit()

            flash(f"Feedback has been added", "alert-success")
            return redirect(f"/users/{username}")
    else:
        raise Unauthorized

    return render_template("add_feedback.html", form=form, user=user)


@app.route("/feedback/<int:id>/update", methods=["GET", "POST"])
def update_feedback(id):
    if "user" not in session:
        flash("Please log in first", "alert-danger")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(id)
    form = FeedbackForm(obj=feedback)

    if session["user"] == feedback.user.username or session["is_admin"]:
        if form.validate_on_submit():
            feedback.title = form.data["title"]
            feedback.content = form.data["content"]

            db.session.commit()

            flash(f"Feedback has been updated", "alert-success")
            return redirect(f"/users/{feedback.user.username}")
    else:
        raise Unauthorized

    return render_template("update_feedback.html", form=form)


@app.route("/feedback/<int:id>/delete", methods=["POST"])
def delete_post(id):
    if "user" not in session:
        flash("Please log in first", "alert-danger")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(id)
    user = feedback.user

    if session["user"] == feedback.user.username or session["is_admin"]:
        db.session.delete(feedback)
        db.session.commit()

        flash("Feedback has been deleted", "alert-success")
        return redirect(f"/users/{user.username}")

    else:
        raise Unauthorized
