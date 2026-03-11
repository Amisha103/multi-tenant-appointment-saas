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
from app.models.master_service import MasterService
from app.extensions import db

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

    services = (
        db.session.query(Service, MasterService)
        .join(MasterService, Service.master_service_id == MasterService.id)
        .filter(Service.tenant_id == business.id)
        .all()
    )

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
# ADMIN SERVICES PAGE
# -----------------------------
@business_bp.route("/<slug>/admin/services", methods=["GET","POST"])
@jwt_required(locations=["cookies"])
def admin_services(slug):

    business = g.current_business

    existing_services = (
        db.session.query(Service, MasterService)
        .join(MasterService, Service.master_service_id == MasterService.id)
        .filter(Service.tenant_id == business.id)
        .all()
    )

    existing_master_ids = [
        s.master_service_id for s,_ in existing_services
    ]

    master_services = MasterService.query.filter(
        MasterService.category == business.category,
        ~MasterService.id.in_(existing_master_ids)
    ).all()

    if request.method == "POST":

        selected_services = request.form.getlist("services")
        other_service = request.form.get("other_service")

        if other_service and other_service.strip():

            new_master = MasterService(
                name=other_service.strip(),
                category=business.category
            )

            db.session.add(new_master)
            db.session.commit()

            selected_services.append(str(new_master.id))

        for service_id in selected_services:

            existing_service = Service.query.filter_by(
                tenant_id=business.id,
                master_service_id=service_id
            ).first()

            if not existing_service:

                service = Service(
                    tenant_id=business.id,
                    master_service_id=service_id
                )

                db.session.add(service)

        db.session.commit()

        flash("Services saved successfully", "success")

        return redirect(url_for(
            "business.admin_services",
            slug=business.slug
        ))

    return render_template(
        "business/admin/admin_services.html",
        business=business,
        services=existing_services,
        master_services=master_services
    )


# -----------------------------
# UPDATE SERVICE
# -----------------------------
@business_bp.route("/<slug>/admin/service/update/<int:id>", methods=["POST"])
@jwt_required(locations=["cookies"])
def update_service(slug, id):

    service = Service.query.get_or_404(id)

    service.price = request.form.get("price")
    service.duration = request.form.get("duration")

    db.session.commit()

    flash("Service updated", "success")

    return redirect(url_for(
        "business.admin_services",
        slug=slug
    ))


# -----------------------------
# DELETE SERVICE
# -----------------------------
@business_bp.route("/<slug>/admin/service/delete/<int:id>")
@jwt_required(locations=["cookies"])
def delete_service(slug, id):

    service = Service.query.get_or_404(id)

    db.session.delete(service)
    db.session.commit()

    flash("Service deleted", "success")

    return redirect(url_for(
        "business.admin_services",
        slug=slug
    ))


# -----------------------------
# BOOK APPOINTMENT
# -----------------------------
@business_bp.route("/<slug>/book")
def book_appointment(slug):

    business = Business.query.filter_by(slug=slug).first_or_404()

    services = (
        db.session.query(Service, MasterService)
        .join(MasterService, Service.master_service_id == MasterService.id)
        .filter(Service.tenant_id == business.id)
        .all()
    )

    return render_template(
        "business/book_appointment.html",
        business=business,
        services=services
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
# -----------------------------
# STAFF LOGIN
# -----------------------------
@business_bp.route("/<slug>/staff/login", methods=["GET", "POST"])
def staff_login(slug):
    business = g.current_business

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            business_user = BusinessUser.query.filter_by(
                user_id=user.id,
                business_id=business.id,
                role="staff"
            ).first()

            if not business_user:
                flash("You are not registered as staff for this business", "error")
                return redirect(url_for("business.staff_login", slug=slug))

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    "business_id": business.id,
                    "role": "staff"
                }
            )

            response = make_response(
                redirect(url_for("business.staff_dashboard", slug=slug))
            )
            set_access_cookies(response, access_token)
            return response

        flash("Invalid credentials", "error")

    return render_template(
        "business/staff/staff_login.html",
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
        "business/user/user_login.html",
        business=business
    )

# -----------------------------
# SAVE NEW SERVICES (from checkboxes)
# -----------------------------
@business_bp.route("/<slug>/admin/services/save", methods=["POST"])
@jwt_required(locations=["cookies"])
def save_service(slug):
    business = g.current_business

    # Get selected services from checkboxes
    selected_services = request.form.getlist("services")

    # Get "Other Service" input if provided
    other_service = request.form.get("other_service")

    if other_service and other_service.strip():
        new_master = MasterService(
            name=other_service.strip(),
            category=business.category
        )
        db.session.add(new_master)
        db.session.commit()
        selected_services.append(str(new_master.id))

    # Add selected services to this business
    for service_id in selected_services:
        existing_service = Service.query.filter_by(
            tenant_id=business.id,
            master_service_id=service_id
        ).first()

        if not existing_service:
            service = Service(
                tenant_id=business.id,
                master_service_id=service_id
            )
            db.session.add(service)

    db.session.commit()

    flash("Services saved successfully", "success")
    return redirect(url_for("business.admin_services", slug=business.slug))