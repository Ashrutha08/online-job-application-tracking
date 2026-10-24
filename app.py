import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = os.environ.get("DATABASE_PATH", str(BASE_DIR / "job_portal.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-before-deployment")
app.config["DATABASE"] = DATABASE


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))
    count = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    if count == 0:
        db.executemany(
            "INSERT INTO jobs (title, company, location, description) VALUES (?, ?, ?, ?)",
            [
                ("Junior Python Developer", "BrightByte Technologies", "Hyderabad", "Work with Python, Flask, REST APIs, and relational databases."),
                ("DevOps Intern", "CloudSpring Labs", "Remote", "Learn CI/CD, Git, Jenkins, Docker, and deployment automation."),
                ("Frontend Developer Intern", "PixelCraft Studio", "Bengaluru", "Build responsive web interfaces with HTML, CSS, and JavaScript."),
                ("QA Automation Trainee", "QualityWorks", "Remote", "Create automated tests and help improve software quality."),
            ],
        )
    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.before_request
def ensure_database():
    if not getattr(app, "_database_initialized", False):
        init_db()
        app._database_initialized = True


@app.route("/")
def index():
    db = get_db()
    jobs = db.execute("SELECT * FROM jobs ORDER BY created_at DESC, id DESC LIMIT 3").fetchall()
    return render_template("index.html", jobs=jobs)


@app.route("/jobs")
def jobs():
    db = get_db()
    search = request.args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        rows = db.execute(
            "SELECT * FROM jobs WHERE title LIKE ? OR company LIKE ? OR location LIKE ? ORDER BY id DESC",
            (like, like, like),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    return render_template("jobs.html", jobs=rows, search=search)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password with at least 8 characters.", "danger")
            return render_template("register.html")
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("An account with that email already exists.", "danger")
            return render_template("register.html")
        flash("Account created. You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["is_admin"] = bool(user["is_admin"])
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("admin") if user["is_admin"] else url_for("jobs"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
@login_required
def apply(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if job is None:
        flash("That job could not be found.", "danger")
        return redirect(url_for("jobs"))
    existing = db.execute(
        "SELECT id FROM applications WHERE user_id = ? AND job_id = ?",
        (session["user_id"], job_id),
    ).fetchone()
    if existing:
        flash("You have already applied for this job.", "info")
        return redirect(url_for("my_applications"))
    if request.method == "POST":
        cover_letter = request.form.get("cover_letter", "").strip()
        if len(cover_letter) < 20:
            flash("Please enter a cover letter of at least 20 characters.", "danger")
            return render_template("apply.html", job=job)
        db.execute(
            "INSERT INTO applications (user_id, job_id, cover_letter) VALUES (?, ?, ?)",
            (session["user_id"], job_id, cover_letter),
        )
        db.commit()
        flash("Your application has been submitted.", "success")
        return redirect(url_for("my_applications"))
    return render_template("apply.html", job=job)


@app.route("/my-applications")
@login_required
def my_applications():
    rows = get_db().execute(
        """SELECT applications.id, applications.status, applications.applied_at,
                  jobs.title, jobs.company, jobs.location
           FROM applications JOIN jobs ON jobs.id = applications.job_id
           WHERE applications.user_id = ? ORDER BY applications.applied_at DESC""",
        (session["user_id"],),
    ).fetchall()
    return render_template("applications.html", applications=rows, is_admin=False)


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if not session.get("is_admin"):
        flash("Admin access is required for that page.", "danger")
        return redirect(url_for("jobs"))
    db = get_db()
    if request.method == "POST":
        application_id = request.form.get("application_id", type=int)
        status = request.form.get("status", "")
        allowed = {"Applied", "Under Review", "Shortlisted", "Rejected", "Hired"}
        if status not in allowed:
            flash("Invalid application status.", "danger")
        else:
            db.execute("UPDATE applications SET status = ? WHERE id = ?", (status, application_id))
            db.commit()
            flash("Application status updated.", "success")
        return redirect(url_for("admin"))
    rows = db.execute(
        """SELECT applications.id, applications.status, applications.applied_at,
                  users.name AS applicant_name, users.email AS applicant_email,
                  jobs.title, jobs.company
           FROM applications
           JOIN users ON users.id = applications.user_id
           JOIN jobs ON jobs.id = applications.job_id
           ORDER BY applications.applied_at DESC"""
    ).fetchall()
    return render_template("admin.html", applications=rows)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.cli.command("create-admin")
def create_admin():
    """Create an admin account using ADMIN_NAME, ADMIN_EMAIL, and ADMIN_PASSWORD env vars."""
    name = os.environ.get("ADMIN_NAME", "Portal Admin")
    email = os.environ.get("ADMIN_EMAIL", "admin@example.com").lower()
    password = os.environ.get("ADMIN_PASSWORD")
    if not password or len(password) < 8:
        raise SystemExit("Set ADMIN_PASSWORD to a value with at least 8 characters.")
    db = get_db()
    db.execute(
        "INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, 1) "
        "ON CONFLICT(email) DO UPDATE SET name=excluded.name, password_hash=excluded.password_hash, is_admin=1",
        (name, email, generate_password_hash(password)),
    )
    db.commit()
    print(f"Admin account ready for {email}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=os.environ.get("FLASK_DEBUG") == "1")
