from flask import Blueprint, render_template
from app.extensions import db
from app.models.business import Business
from app.models.service import Service
from app.models.business_image import BusinessImage

business_bp = Blueprint(
    "business",
    __name__,
    template_folder="../templates/business"
)

@business_bp.route("/<slug>")
def business_home(slug):
    
    business = Business.query.filter_by(slug=slug).first_or_404()

    
    services = Service.query.filter_by(business_id=business.id).all()
    images = BusinessImage.query.filter_by(business_id=business.id).all()

    return render_template(
        "business_home.html",
        business=business,
        services=services,
        images=images
    )

@business_bp.route('/<int:business_id>/admin/login', methods=['GET', 'POST'])
def admin_login(business_id):
    business = Business.query.get_or_404(business_id)
    return render_template('admin_login.html', business=business)

@business_bp.route('/<int:business_id>/staff/login', methods=['GET', 'POST'])
def staff_login(business_id):
    business = Business.query.get_or_404(business_id)
    return render_template('staff_login.html', business=business)

@business_bp.route('/<int:business_id>/user/login', methods=['GET', 'POST'])
def user_login(business_id):
    business = Business.query.get_or_404(business_id)
    return render_template('user_login.html', business=business)


