from datetime import datetime
import os
import sqlite3

import joblib
import pandas as pd

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "smartfinance.db",
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "loan_model.pkl",
)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SMARTFINANCE_SECRET",
    "change-this-secret-in-production",
)

model = joblib.load(MODEL_PATH)


FEATURES = [
    "no_of_dependents",
    "education",
    "self_employed",
    "income_annum",
    "loan_amount",
    "loan_term",
    "cibil_score",
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
]


def db():
    """Create and return a SQLite connection."""
    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """Create the required database tables."""
    connection = db()

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS loan_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dependents INTEGER,
            education TEXT,
            self_employed TEXT,
            income_annum REAL,
            loan_amount REAL,
            loan_term INTEGER,
            cibil_score INTEGER,
            residential_assets_value REAL,
            commercial_assets_value REAL,
            luxury_assets_value REAL,
            bank_asset_value REAL,
            prediction TEXT,
            probability REAL,
            risk_score REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

    connection.commit()
    connection.close()


def login_required():
    """Return True when a user is logged in."""
    return "user_id" in session



def financial_risk_score(
    cibil,
    income,
    loan_amount,
    assets,
):
    """
    Calculate a project-specific financial risk score.

    This is NOT an official CIBIL score.
    """
    credit_component = max(
        0,
        min(
            100,
            (float(cibil) - 300) / 6,
        ),
    )

    debt_component = max(
        0,
        min(
            100,
            100
            - (
                float(loan_amount)
                / max(float(income), 1)
            )
            * 100,
        ),
    )

    asset_component = max(
        0,
        min(
            100,
            float(assets)
            / max(float(loan_amount), 1)
            * 50,
        ),
    )

    score = round(
        (
            0.60 * credit_component
            + 0.25 * debt_component
            + 0.15 * asset_component
        ),
        1,
    )

    return score



@app.context_processor
def inject_globals():
    return {
        "logged_in": login_required(),
        "user_name": session.get("user_name"),
    }




@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or len(password) < 6:
            flash(
                "Enter your name and a password of at least 6 characters.",
                "error",
            )

            return render_template("register.html")

        try:
            connection = db()

            connection.execute(
                """
                INSERT INTO users (
                    name,
                    email,
                    password,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    generate_password_hash(password),
                    datetime.now().isoformat(),
                ),
            )

            connection.commit()
            connection.close()

            flash(
                "Registration successful. Please log in.",
                "success",
            )

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash(
                "That email is already registered.",
                "error",
            )

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        connection = db()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password,
        ):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("dashboard"))

        flash(
            "Invalid email or password.",
            "error",
        )

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("home"))


# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    connection = db()

    applications = connection.execute(
        """
        SELECT *
        FROM loan_applications
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],),
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        applications=applications,
    )


@app.route("/loan", methods=["GET", "POST"])
def loan():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        form = request.form

        data = {
            "no_of_dependents": int(
                form["no_of_dependents"]
            ),
            "education": form["education"].strip(),
            "self_employed": form["self_employed"].strip(),
            "income_annum": float(
                form["income_annum"]
            ),
            "loan_amount": float(
                form["loan_amount"]
            ),
            "loan_term": int(
                form["loan_term"]
            ),
            "cibil_score": int(
                form["cibil_score"]
            ),
            "residential_assets_value": float(
                form["residential_assets_value"]
            ),
            "commercial_assets_value": float(
                form["commercial_assets_value"]
            ),
            "luxury_assets_value": float(
                form["luxury_assets_value"]
            ),
            "bank_asset_value": float(
                form["bank_asset_value"]
            ),
        }

        input_data = pd.DataFrame(
            [data],
            columns=FEATURES,
        )

        prediction_value = int(
            model.predict(input_data)[0]
        )

        probabilities = model.predict_proba(
            input_data
        )[0]

        probability = float(
            probabilities[prediction_value]
        )

        total_assets = (
            data["residential_assets_value"]
            + data["commercial_assets_value"]
            + data["luxury_assets_value"]
            + data["bank_asset_value"]
        )

        risk = financial_risk_score(
            data["cibil_score"],
            data["income_annum"],
            data["loan_amount"],
            total_assets,
        )

        prediction = (
            "Approved"
            if prediction_value == 1
            else "Rejected"
        )

        connection = db()

        connection.execute(
            """
            INSERT INTO loan_applications (
                user_id,
                dependents,
                education,
                self_employed,
                income_annum,
                loan_amount,
                loan_term,
                cibil_score,
                residential_assets_value,
                commercial_assets_value,
                luxury_assets_value,
                bank_asset_value,
                prediction,
                probability,
                risk_score,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                session["user_id"],
                data["no_of_dependents"],
                data["education"],
                data["self_employed"],
                data["income_annum"],
                data["loan_amount"],
                data["loan_term"],
                data["cibil_score"],
                data["residential_assets_value"],
                data["commercial_assets_value"],
                data["luxury_assets_value"],
                data["bank_asset_value"],
                prediction,
                round(probability * 100, 2),
                risk,
                datetime.now().isoformat(),
            ),
        )

        connection.commit()
        connection.close()

        return render_template(
            "loan_result.html",
            prediction=prediction,
            probability=round(
                probability * 100,
                2,
            ),
            risk=risk,
            cibil=data["cibil_score"],
            loan_amount=data["loan_amount"],
        )

    return render_template("loan.html")


@app.route("/emi")
def emi():
    return render_template("emi.html")



@app.route(
    "/vehicle-insurance",
    methods=["GET", "POST"],
)
def vehicle_insurance():
    result = None

    if request.method == "POST":
        age = float(request.form["age"])
        value = float(request.form["value"])
        claims = int(request.form["claims"])
        vehicle_age = float(
            request.form["vehicle_age"]
        )

        base = max(
            2500,
            value * 0.025,
        )

        risk_factor = (
            1
            + min(0.50, claims * 0.08)
            + min(0.25, vehicle_age * 0.03)
            + (0.10 if age < 23 else 0)
        )

        result = round(
            base * risk_factor,
            2,
        )

    return render_template(
        "vehicle.html",
        result=result,
    )


@app.route(
    "/medical-insurance",
    methods=["GET", "POST"],
)
def medical_insurance():
    result = None

    if request.method == "POST":
        age = int(request.form["age"])
        dependents = int(
            request.form["dependents"]
        )
        bmi = float(request.form["bmi"])

        smoker = (
            request.form["smoker"] == "Yes"
        )

        base = (
            6000
            + age * 120
            + dependents * 900
        )

        if bmi >= 30:
            base *= 1.20

        if smoker:
            base *= 1.30

        result = round(base, 2)

    return render_template(
        "medical.html",
        result=result,
    )



@app.route(
    "/contact",
    methods=["GET", "POST"],
)
def contact():
    if request.method == "POST":
        connection = db()

        connection.execute(
            """
            INSERT INTO contact_messages (
                name,
                email,
                subject,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.form["name"],
                request.form["email"],
                request.form.get(
                    "subject",
                    "",
                ),
                request.form["message"],
                datetime.now().isoformat(),
            ),
        )

        connection.commit()
        connection.close()

        flash(
            "Your message has been received.",
            "success",
        )

        return redirect(
            url_for("contact")
        )

    return render_template("contact.html")


@app.route("/admin")
def admin():
    """
    Simple demo admin view.

    For production use, add proper role-based
    authentication and access control.
    """
    connection = db()

    users = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM users
        """
    ).fetchone()["count"]

    applications = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM loan_applications
        """
    ).fetchone()["count"]

    approved = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM loan_applications
        WHERE prediction = 'Approved'
        """
    ).fetchone()["count"]

    rejected = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM loan_applications
        WHERE prediction = 'Rejected'
        """
    ).fetchone()["count"]

    recent = connection.execute(
        """
        SELECT
            loan_applications.*,
            users.name,
            users.email
        FROM loan_applications
        JOIN users
            ON users.id = loan_applications.user_id
        ORDER BY loan_applications.id DESC
        LIMIT 20
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        users=users,
        apps=applications,
        approved=approved,
        rejected=rejected,
        recent=recent,
    )



if __name__ == "__main__":
    init_db()

    app.run(
        debug=True
    )
