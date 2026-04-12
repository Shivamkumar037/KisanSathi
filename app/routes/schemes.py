"""
Government Schemes Routes
- GET /api/schemes               - List all schemes
- GET /api/schemes/<id>          - Get scheme details
- GET /api/schemes/category/<c>  - Filter by category
- GET /api/schemes/search        - Search schemes
"""

from flask import Blueprint, request, jsonify
from app.models.scheme import GovernmentScheme

schemes_bp = Blueprint('schemes', __name__)


@schemes_bp.route('/', methods=['GET'])
def get_all_schemes():
    """Get all active government schemes"""
    schemes = GovernmentScheme.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'count': len(schemes),
        'schemes': [s.to_dict() for s in schemes]
    }), 200


@schemes_bp.route('/<int:scheme_id>', methods=['GET'])
def get_scheme(scheme_id):
    """Get full details of a single scheme"""
    scheme = GovernmentScheme.query.get(scheme_id)
    if not scheme:
        return jsonify({'success': False, 'message': 'Scheme not found'}), 404

    return jsonify({'success': True, 'scheme': scheme.to_dict()}), 200


@schemes_bp.route('/category/<string:category>', methods=['GET'])
def get_by_category(category):
    """Filter schemes by category"""
    valid_categories = ['financial', 'insurance', 'irrigation', 'credit', 'market', 'all']
    if category not in valid_categories:
        return jsonify({
            'success': False,
            'message': f'Invalid category. Choose from: {", ".join(valid_categories)}'
        }), 400

    if category == 'all':
        schemes = GovernmentScheme.query.filter_by(is_active=True).all()
    else:
        schemes = GovernmentScheme.query.filter_by(category=category, is_active=True).all()

    return jsonify({
        'success': True,
        'category': category,
        'schemes': [s.to_dict() for s in schemes]
    }), 200


@schemes_bp.route('/search', methods=['GET'])
def search_schemes():
    """Search schemes by keyword"""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'success': False, 'message': 'Search query required'}), 400

    schemes = GovernmentScheme.query.filter(
        GovernmentScheme.is_active == True,
        db.or_(
            GovernmentScheme.name.ilike(f'%{q}%'),
            GovernmentScheme.description.ilike(f'%{q}%'),
            GovernmentScheme.short_name.ilike(f'%{q}%')
        )
    ).all()

    from app import db
    return jsonify({
        'success': True,
        'query': q,
        'results': [s.to_dict() for s in schemes]
    }), 200
