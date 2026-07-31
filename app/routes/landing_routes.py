import traceback

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.extensions import db
from app.models.business import Business
from app.models.user import User
from app.models.business_user import BusinessUser
from werkzeug.security import generate_password_hash
import os
from flask import jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

landing_bp = Blueprint(
    "landing",
    __name__,
    template_folder="../templates"
)



@landing_bp.route("/")
def home():
    businesses = Business.query.filter_by(is_active=True).all()

    category_images = {}

    for business in businesses:
        folder_path = os.path.join(
            current_app.static_folder,
            "images",
            business.category
        )

        images = []
        if os.path.exists(folder_path):
            images = os.listdir(folder_path)

        category_images[business.id] = images

    return render_template(
        "landingpage/home.html",
        businesses=businesses,
        category_images=category_images
    )

    
@landing_bp.route("/register-business", methods=["GET", "POST"])
def register_business():

    if request.method == "POST":

        # -------------------------
        # Form Data
        # -------------------------
        name = request.form.get("business_name")
        owner_name = request.form.get("owner_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        gst_number = request.form.get("gst_number")
        address = request.form.get("address")
        category = request.form.get("category")

        password = request.form.get("password")

        google_id = request.form.get("google_id")
        auth_provider = request.form.get("auth_provider", "local")
        profile_picture = request.form.get("profile_picture")

        # -------------------------
        # Validation Checks
        # -------------------------

        if Business.query.filter_by(gst_number=gst_number).first():
            flash("GST number already registered.", "error")
            return redirect(url_for("landing.register_business"))

        if Business.query.filter_by(email=email).first():
            flash("Business email already registered.", "error")
            return redirect(url_for("landing.register_business"))

        if User.query.filter_by(email=email).first():
            flash("User with this email already exists.", "error")
            return redirect(url_for("landing.register_business"))

        try:

            # ==================================================
            # 1️⃣ Create Business
            # ==================================================
            new_business = Business(
                name=name,
                owner_name=owner_name,
                email=email,
                phone=phone,
                gst_number=gst_number,
                category=category,
                address=address,
                is_active=True
            )

            db.session.add(new_business)

            # Generate Business ID
            db.session.flush()

            # ==================================================
            # 2️⃣ Create Owner User
            # ==================================================

            owner_user = User(
                name=owner_name,
                email=email,
                google_id=google_id if auth_provider == "google" else None,
                auth_provider=auth_provider,
                email_verified=True if auth_provider == "google" else False,
                profile_picture=profile_picture
            )

            # Set password ONLY for local signup
            if auth_provider == "local":
                owner_user.set_password(password)

            db.session.add(owner_user)

            # Generate User ID
            db.session.flush()

            # ==================================================
            # 3️⃣ Link User & Business
            # ==================================================

            business_user = BusinessUser(
                user_id=owner_user.id,
                business_id=new_business.id,
                role="admin"
            )

            db.session.add(business_user)

            # ==================================================
            # 4️⃣ Save Everything
            # ==================================================

            db.session.commit()

            flash(
                "Business registered successfully! Owner account created.",
                "success"
            )

            return redirect(url_for("landing.home"))

        except Exception as e:

            db.session.rollback()

            print(e)

            flash(
                "Something went wrong. Please try again.",
                "error"
            )

            return redirect(url_for("landing.register_business"))

    print(current_app.config["GOOGLE_CLIENT_ID"])

    return render_template(
        "landingpage/register_business.html",
        google_client_id=current_app.config["GOOGLE_CLIENT_ID"]
    )
@landing_bp.route("/auth/google/verify", methods=["POST"])
def verify_google():

    data = request.get_json()

    if not data or "credential" not in data:
        return jsonify({
            "success": False,
            "message": "Google credential is missing."
        }), 400

    credential = data.get("credential")

    try:

        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            current_app.config["GOOGLE_CLIENT_ID"]
        )

        return jsonify({

            "success": True,

            "name": idinfo.get("name"),

            "email": idinfo.get("email"),

            "google_id": idinfo.get("sub"),

            "picture": idinfo.get("picture"),

            "email_verified": idinfo.get("email_verified", False)

        })

    except ValueError:

        return jsonify({
            "success": False,
            "message": "Invalid Google token."
        }), 401
    
    except Exception as e:

       traceback.print_exc()

       return jsonify({
        "success": False,
        "message": str(e)
    }), 500

@landing_bp.route("/services")
def services():
    return render_template("landingpage/services.html")