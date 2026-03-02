from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.extensions import db
from app.models.business import Business
from app.models.user import User
from app.models.business_user import BusinessUser
from werkzeug.security import generate_password_hash
import os

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
        name = request.form.get("business_name")
        owner_name = request.form.get("owner_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        gst_number = request.form.get("gst_number")
        address = request.form.get("address")
        category = request.form.get("category")

        password = "temporary123"

        
        existing_gst = Business.query.filter_by(gst_number=gst_number).first()
        if existing_gst:
            flash("GST number already registered.", "error")
            return redirect(url_for("landing.register_business"))

        existing_business_email = Business.query.filter_by(email=email).first()
        if existing_business_email:
            flash("Business email already registered.", "error")
            return redirect(url_for("landing.register_business"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User with this email already exists.", "error")
            return redirect(url_for("landing.register_business"))

        try:
            
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
            db.session.commit()

           
            owner_user = User(
                name=owner_name,
                email=email,
                password=generate_password_hash(password)
            )

            db.session.add(owner_user)
            db.session.commit()

            
            business_user = BusinessUser(
                user_id=owner_user.id,
                business_id=new_business.id,
                role="admin"
            )

            db.session.add(business_user)
            db.session.commit()

            flash("Business registered successfully! Owner account created.", "success")
            return redirect(url_for("landing.home"))

        except Exception as e:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "error")
            print(e)
            return redirect(url_for("landing.register_business"))

    return render_template("landingpage/register_business.html")



@landing_bp.route("/services")
def services():
    return render_template("landingpage/services.html")