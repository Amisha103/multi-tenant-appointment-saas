from flask import request, g
from app.models.business import Business

def load_current_business():
    """
    This middleware loads the current business (tenant)
    based on slug in URL and attaches it to g.current_business
    """

    # Only apply for routes that contain <slug>
    view_args = request.view_args

    if view_args and "slug" in view_args:
        slug = view_args.get("slug")

        business = Business.query.filter_by(slug=slug).first()

        if not business:
            return "Business not found", 404

        g.current_business = business