from flask import (
    Blueprint,
    current_app,
    request,
    redirect,
    url_for,
    flash,
    render_template,
    g,
    abort,
    make_response
)

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    unset_jwt_cookies,
    set_access_cookies
)

from app.models.business import Business
from app.models.service import Service
from app.models.user import User
from app.models.business_user import BusinessUser
from app.extensions import db
from app.models.master_service import MasterService

import os


business_bp = Blueprint(
    "business",
    __name__,
    template_folder="../templates/business",
    url_prefix="/business"
)


# -----------------------------
# BUSINESS HOME
# -----------------------------
@business_bp.route("/<slug>")
def business_home(slug):

    business = g.current_business

    services = Service.query.filter_by(
        business_id=business.id
    ).all()

    category = business.category.lower()

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
                image_files.append(
                    f"images/business/{category}/{file}"
                )

    return render_template(
        "business_home.html",
        business=business,
        services=services,
        images=image_files
    )


# -----------------------------
# ADMIN LOGIN
# -----------------------------
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

                access_token = create_access_token(
                    identity=str(user.id),
                    additional_claims={
                        "business_id": business.id,
                        "role": "admin"
                    }
                )

                response = make_response(
                    redirect(url_for("business.admin_dashboard", slug=slug))
                )

                set_access_cookies(response, access_token)

                return response

        flash("Invalid credentials or unauthorized access", "error")

    return render_template(
        "business/admin/admin_login.html",
        business=business
    )


# -----------------------------
# STAFF LOGIN
# -----------------------------
@business_bp.route("/<slug>/staff/login", methods=["GET", "POST"])
def staff_login(slug):

    business = g.current_business

    return render_template(
        "business/staff_login.html",
        business=business
    )


# -----------------------------
# USER LOGIN
# -----------------------------
@business_bp.route("/<slug>/user/login", methods=["GET", "POST"])
def user_login(slug):

    business = g.current_business

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            business_user = BusinessUser.query.filter_by(
                user_id=user.id,
                business_id=business.id
            ).first()

            if not business_user:
                business_user = BusinessUser(
                    user_id=user.id,
                    business_id=business.id,
                    role="customer"
                )
                db.session.add(business_user)
                db.session.commit()

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    "business_id": business.id,
                    "role": "customer"
                }
            )

            response = make_response(
                redirect(url_for("business.user_dashboard", slug=slug))
            )

            set_access_cookies(response, access_token)

            return response

        flash("Invalid email or password", "error")

    return render_template(
        "user/user_login.html",
        business=business
    )


# -----------------------------
# USER REGISTER
# -----------------------------
@business_bp.route("/<slug>/user/register", methods=["GET", "POST"])
def user_register(slug):

    business = g.current_business

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Please login.", "error")
            return redirect(url_for("business.user_login", slug=slug))

        new_user = User(
            name=name,
            email=email
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        business_user = BusinessUser(
            user_id=new_user.id,
            business_id=business.id,
            role="customer"
        )

        db.session.add(business_user)
        db.session.commit()

        access_token = create_access_token(
            identity=str(new_user.id),
            additional_claims={
                "business_id": business.id,
                "role": "customer"
            }
        )

        response = make_response(
            redirect(url_for("business.user_dashboard", slug=slug))
        )

        set_access_cookies(response, access_token)

        return response

    return render_template(
        "user/user_register.html",
        business=business
    )


# -----------------------------
# USER DASHBOARD
# -----------------------------
@business_bp.route("/<slug>/user/dashboard")
@jwt_required(locations=["cookies"])
def user_dashboard(slug):

    business = g.current_business

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    return render_template(
        "user/user_dashboard.html",
        business=business,
        user=user
    )


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@business_bp.route("/<slug>/admin/dashboard")
@jwt_required(locations=["cookies"])
def admin_dashboard(slug):

    business = g.current_business

    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims["role"] != "admin":
        abort(403)

    user = User.query.get(user_id)

    return render_template(
        "business/admin/admin_dashboard.html",
        business=business,
        user=user
    )


# -----------------------------
# LOGOUT
# -----------------------------
@business_bp.route("/<slug>/logout")
def logout(slug):

    response = make_response(
        redirect(url_for("business.business_home", slug=slug))
    )

    unset_jwt_cookies(response)

    return response


# -----------------------------
# LOAD BUSINESS FROM SLUG
# -----------------------------
@business_bp.url_value_preprocessor
def get_business(endpoint, values):

    slug = values.get("slug")

    if slug:

        business = Business.query.filter_by(
            slug=slug
        ).first_or_404()

        g.current_business = business


@business_bp.route("/<slug>/admin/services", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def admin_services(slug):

    business = g.current_business

    master_services = MasterService.query.filter_by(
        category=business.category
    ).all()

    if request.method == "POST":

        selected_services = request.form.getlist("services")

        for service_id in selected_services:

            service = Service(
                business_id=business.id,
                master_service_id=service_id
            )

            db.session.add(service)

        db.session.commit()

        flash("Services updated successfully")

        return redirect(
            url_for("business.admin_services", slug=slug)
        )

    return render_template(
        "business/admin/admin_services.html",
        business=business,
        master_services=master_services
    )