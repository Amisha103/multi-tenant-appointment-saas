from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.business import Business

landing_bp = Blueprint(
    "landing",
    __name__,
    template_folder="../templates"
)

@landing_bp.route("/")
def home():
    businesses = Business.query.filter_by(is_active=True).all()
    return render_template(
        "landingpage/home.html",
        businesses=businesses
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

       
        existing_gst = Business.query.filter_by(gst_number=gst_number).first()
        if existing_gst:
            flash("GST number already registered.", "error")
            return redirect(url_for("landing.register_business"))

       
        existing_email = Business.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered.", "error")
            return redirect(url_for("landing.register_business"))

        new_business = Business(
            name=name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            gst_number=gst_number,
            category=category,
            address=address
        )

        db.session.add(new_business)
        db.session.commit()

        flash("Business registered successfully! Await verification.", "success")
        return redirect(url_for("landing.home"))

    return render_template("landingpage/register_business.html")



@landing_bp.route("/services")
def services():
    return render_template("landingpage/services.html")




