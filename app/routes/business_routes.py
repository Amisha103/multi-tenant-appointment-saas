from flask import Blueprint, render_template, g, current_app
from app.models.business import Business
from app.models.service import Service
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
    return render_template("admin_login.html", business=business)


@business_bp.route("/<slug>/staff/login", methods=["GET", "POST"])
def staff_login(slug):
    business = g.current_business
    return render_template("staff_login.html", business=business)


@business_bp.route("/<slug>/user/login", methods=["GET", "POST"])
def user_login(slug):
    business = g.current_business
    return render_template("user_login.html", business=business)