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
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    unset_jwt_cookies,
    set_access_cookies
)
from datetime import datetime
from app.models.appointment import Appointment
from app.models.business import Business
from app.models.service import Service
from app.models.user import User
from app.models.staff import Staff
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



@business_bp.url_value_preprocessor
def get_business(endpoint, values):

    slug = values.get("slug")

    if slug:

        business = Business.query.filter_by(
            slug=slug
        ).first_or_404()

        g.current_business = business


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

@business_bp.route("/<slug>/admin/staff", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def admin_staff(slug):
    business = g.current_business
    tenant_id = business.id

    if request.method == "POST":
        email = request.form.get("email")

        
        sequence_name = f"staff_id_seq_{tenant_id}"

        db.session.execute(db.text(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class WHERE relname = '{sequence_name}'
            ) THEN
                CREATE SEQUENCE {sequence_name} START 100;
            END IF;
        END
        $$;
        """))

        result = db.session.execute(
            db.text(f"SELECT nextval('{sequence_name}')")
        )
        staff_id = result.scalar()

        new_staff = Staff(
            email=email,
            staff_id=staff_id,
            tenant_id=tenant_id
        )

        db.session.add(new_staff)
        db.session.commit()

        flash("Staff added successfully", "success")
        return redirect(url_for("business.admin_staff", slug=slug))

    
    staff_list = Staff.query.filter_by(tenant_id=tenant_id).all()

    return render_template(
        "business/admin/admin_staff.html",
        business=business,
        staff_list=staff_list
    )

@business_bp.route("/<slug>/staff/login", methods=["GET", "POST"])
def staff_login(slug):
    business = Business.query.filter_by(slug=slug).first()

    if not business:
        return "Business not found", 404

    if request.method == "POST":
        email = request.form.get("email")
        staff_id = request.form.get("staff_id")
        password = request.form.get("password")

        staff = Staff.query.filter_by(
            email=email,
            staff_id=staff_id,
            tenant_id=business.id
        ).first()

        if not staff:
            flash("Invalid credentials", "danger")
            return redirect(request.url)

        # First-time login
        if not staff.password:
            return redirect(url_for(
                "business.set_staff_password",
                id=staff.id,
                slug=slug
            ))

        if not password:
            flash("Please enter password", "danger")
            return redirect(request.url)

        if check_password_hash(staff.password, password):

            # ✅ FIXED HERE
            access_token = create_access_token(
                identity=str(staff.id),
                additional_claims={
                    "tenant_id": business.id,
                    "role": "staff"
                }
            )

            response = make_response(
                redirect(url_for("business.staff_dashboard", slug=slug))
            )

            set_access_cookies(response, access_token)

            flash("Login successful", "success")
            return response

        else:
            flash("Wrong password", "danger")
            return redirect(request.url)

    return render_template(
        "business/staff/staff_login.html",
        business=business
    )


@business_bp.route("/<slug>/staff/check", methods=["GET", "POST"])
def check_staff(slug):
    business = Business.query.filter_by(slug=slug).first()

    if request.method == "POST":
        email = request.form.get("email")
        staff_id = request.form.get("staff_id")

        staff = Staff.query.filter_by(
            email=email,
            staff_id=staff_id,
            tenant_id=business.id
        ).first()

        if not staff:
            flash("Invalid details", "danger")
            return redirect(request.url)

        return redirect(url_for(
            "business.set_staff_password",
            slug=slug,
            id=staff.id
        ))

    return render_template(
        "business/staff/check_staff.html",
        business=business
    )



@business_bp.route("/<slug>/staff/setup/<int:id>", methods=["GET", "POST"])
def set_staff_password(slug, id):
    business = Business.query.filter_by(slug=slug).first()

    if not business:
        return "Business not found", 404

    # 🔥 IMPORTANT: Tenant isolation
    staff = Staff.query.filter_by(
        id=id,
        tenant_id=business.id
    ).first_or_404()

    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(request.url)

        staff.name = name
        staff.password = generate_password_hash(password)

        db.session.commit()

        flash("Account setup complete. Please login.", "success")
        return redirect(url_for("business.staff_login", slug=slug))

    return render_template("business/staff/staff_set_password.html", staff=staff)


@business_bp.route("/<slug>/staff/dashboard", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def staff_dashboard(slug):
    business = g.current_business
    staff_id = get_jwt_identity()
    claims = get_jwt()

    if claims.get("role") != "staff":
        abort(403)

    staff = Staff.query.filter_by(id=staff_id, tenant_id=business.id).first_or_404()

    services = Service.query.filter_by(
    tenant_id=business.id
).all()

  
    if request.method == "POST":
        time_str = request.form.get("appointment_time")
        service_id = request.form.get("service_id")

        
        time_obj = datetime.fromisoformat(time_str)

        slot = Appointment(
            time=time_obj,
            service_id=service_id,
            staff_id=staff.id,
            tenant_id=business.id,
            is_booked=False
        )

        db.session.add(slot)
        db.session.commit()

        flash("Slot created", "success")
        return redirect(url_for("business.staff_dashboard", slug=slug))

    # 🔥 GET ALL SLOTS
    now = datetime.now()

    appointments = Appointment.query.filter(
    Appointment.tenant_id == business.id,
    Appointment.time >= now
).order_by(Appointment.time).all()

    return render_template(
        "business/staff/staff_dashboard.html",
        staff=staff,
        business=business,
        services=services,
        appointments=appointments
        
    )


@business_bp.route("/<slug>/admin/add-appointment", methods=["GET", "POST"])
def add_appointment(slug):
    business = g.current_business

    services = (
        db.session.query(Service, MasterService)
        .join(MasterService, Service.master_service_id == MasterService.id)
        .filter(Service.tenant_id == business.id)
        .all()
    )

    if request.method == "POST":
        time_str = request.form.get("appointment_time")
        service_id = int(request.form.get("service_id"))  # ✅ FIX TYPE

        appointment_time = datetime.fromisoformat(time_str)

        # 🔥 CHECK FOR DUPLICATE SLOT (IMPORTANT)
        existing_slot = Appointment.query.filter_by(
            tenant_id=business.id,
            service_id=service_id,
            staff_id=staff.id,    
            time=appointment_time
        ).first()

        if existing_slot:
            flash("Slot already exists for this service at this time", "error")
            return redirect(url_for("business.add_appointment", slug=slug))

        # ✅ CREATE SLOT
        new_appt = Appointment(
            time=appointment_time,
            service_id=service_id,
            tenant_id=business.id,
            is_booked=False
        )

        db.session.add(new_appt)
        db.session.commit()

        flash("Appointment slot added", "success")
        return redirect(url_for("business.admin_dashboard", slug=slug))

    return render_template(
        "business/admin/add_appointment.html",
        services=services,
        business=business
    )
@business_bp.route("/<slug>/book/<int:id>", methods=["POST"])
@jwt_required(locations=["cookies"])
def book_slot(slug, id):

    business = g.current_business
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    slot = Appointment.query.filter_by(
        id=id,
        tenant_id=business.id
    ).first_or_404()

    if slot.is_booked:
        flash("Slot already booked", "error")
        return redirect(url_for("business.user_dashboard", slug=slug))

    slot.customer_name = user.name
    slot.customer_email = user.email
    slot.is_booked = True

    db.session.commit()

    flash("Appointment booked successfully!", "success")
    return redirect(url_for("business.user_dashboard", slug=slug))

@business_bp.route("/<slug>/staff/delete-slot/<int:id>", methods=["POST"])
@jwt_required(locations=["cookies"])
def delete_slot(slug, id):
    business = g.current_business
    staff_id = get_jwt_identity()

    slot = Appointment.query.filter_by(
        id=id,
        tenant_id=business.id,
        staff_id=staff_id
    ).first_or_404()

    # ❌ Prevent deleting booked slots (important)
    if slot.is_booked:
        flash("Cannot delete a booked slot", "error")
        return redirect(url_for("business.staff_dashboard", slug=slug))

    db.session.delete(slot)
    db.session.commit()

    flash("Slot deleted successfully", "success")
    return redirect(url_for("business.staff_dashboard", slug=slug))

@business_bp.route("/<slug>/staff/update-slot/<int:id>", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def update_slot(slug, id):
    business = g.current_business
    staff_id = get_jwt_identity()

    slot = Appointment.query.filter_by(
        id=id,
        tenant_id=business.id,
        staff_id=staff_id
    ).first_or_404()

    if request.method == "POST":
        from datetime import datetime

        time_str = request.form.get("appointment_time")
        new_time = datetime.fromisoformat(time_str)

        # 🔥 CHECK OVERLAP (same service + same staff)
        existing = Appointment.query.filter_by(
            tenant_id=business.id,
            staff_id=staff_id,
            service_id=slot.service_id,
            time=new_time
        ).first()

        if existing and existing.id != slot.id:
            flash("Time slot overlaps with another slot", "error")
            return redirect(url_for("business.staff_dashboard", slug=slug))

        slot.time = new_time
        db.session.commit()

        flash("Slot updated successfully", "success")
        return redirect(url_for("business.staff_dashboard", slug=slug))

    return render_template(
        "business/staff/update_slot.html",
        slot=slot,
        business=business
    )

@business_bp.route("/<slug>/cancel/<int:id>", methods=["POST"])
@jwt_required(locations=["cookies"])
def cancel_appointment(slug, id):

    business = g.current_business
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    slot = Appointment.query.filter_by(
        id=id,
        tenant_id=business.id,
        customer_email=user.email
    ).first_or_404()

    # Reset slot
    slot.is_booked = False
    slot.customer_name = None
    slot.customer_email = None

    db.session.commit()

    flash("Appointment cancelled", "success")
    return redirect(url_for("business.user_dashboard", slug=slug))

@business_bp.route("/<slug>/user/dashboard")
@jwt_required(locations=["cookies"])
def user_dashboard(slug):

    business = g.current_business

    user_id = get_jwt_identity()
    claims = get_jwt()

    if claims.get("role") != "customer":
        abort(403)

    user = User.query.get(user_id)

    # ✅ AVAILABLE SLOTS (only not booked)
    available_slots = Appointment.query.filter_by(
        tenant_id=business.id,
        is_booked=False
    ).order_by(Appointment.time).all()

    # ✅ USER BOOKINGS
    my_appointments = Appointment.query.filter_by(
        tenant_id=business.id,
        customer_email=user.email,
        is_booked=True
    ).order_by(Appointment.time).all()

    return render_template(
        "business/user/user_dashboard.html",
        business=business,
        user=user,
        available_slots=available_slots,
        my_appointments=my_appointments
    )