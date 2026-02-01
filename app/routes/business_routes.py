from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.business import Business
from app.models.service import Service        
from app.models.business_image import BusinessImage 

business_bp = Blueprint(
    "business",
    __name__,
    template_folder="../templates/business"
)

@business_bp.route('/<int:business_id>')
def business_home(business_id):
    
    business = Business.query.get_or_404(business_id)
    services = Service.query.filter_by(business_id=business.id).all()
    images = BusinessImage.query.filter_by(business_id=business.id).all()

    return render_template(
        'business_home.html',
        business=business,
        services=services,
        images=images
    )