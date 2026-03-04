from flask import Blueprint, current_app, request, redirect, url_for, flash, render_template, g
from app.models.business import Business
from app.models.service import Service
from flask_login import login_user
from app.models.user import User
from app.models.business_user import BusinessUser
import os

business_bp = Blueprint(
    "business",
    __name__,
    template_folder="../templates/business",
    url_prefix="/business"
)
@business_bp.route("/<slug>")
def business_home(slug):
    business = g.current_business

    services = Service.query.filter_by(business_id=business.id).all()

    # Get business category
    category = business.category.lower()

    # Build folder path
    image_folder = os.path.join(
        current_app.root_path,
        "static",
        "images",
        "business",
        category
    )

    image_files = []

    if os.path.exists(image_folder):
        for file in os.listdir(image_folder):
            if file.endswith((".jpg", ".jpeg", ".png", ".webp")):
                image_files.append(f"images/business/{category}/{file}")

    return render_template(
        "business_home.html",
        business=business,
        services=services,
        images=image_files
    )

@business_bp.route("/<slug>/admin/login", methods=["GET", "POST"])
def admin_login(slug):

    business = g.current_business

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            business_user = BusinessUser.query.filter_by(
                user_id=user.id,
                business_id=business.id,
                role="admin"
            ).first()

            if business_user:
                login_user(user)
                return redirect(
                    url_for("business.admin_dashboard", slug=slug)
                )

        flash("Invalid credentials or unauthorized access", "error")
        return render_template(
        "business/admin/admin_login.html",
        business=business
    )



@business_bp.route("/<slug>/staff/login", methods=["GET", "POST"])
def staff_login(slug):
    business = g.current_business
    return render_template("staff_login.html", business=business)


@business_bp.route("/<slug>/user/login", methods=["GET", "POST"])
def user_login(slug):
    business = g.current_business
    return render_template("user_login.html", business=business)
 
@business_bp.url_value_preprocessor
def get_business(endpoint, values):
    slug = values.get("slug")
    if slug:
        business = Business.query.filter_by(slug=slug).first_or_404()
        g.current_business = business

from flask_login import login_required, current_user
from flask import abort

@business_bp.route("/<slug>/admin/dashboard")
@login_required
def admin_dashboard(slug):

    business = g.current_business

    business_user = BusinessUser.query.filter_by(
        user_id=current_user.id,
        business_id=business.id,
        role="admin"
    ).first()

    if not business_user:
        abort(403)

    return render_template(
        "business/admin/admin_dashboard.html",
        business=business
    )