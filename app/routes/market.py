"""
Market Rates Routes (Mandi Bhav)
- GET /api/market/rates          - Get all rates (filterable)
- GET /api/market/mandis         - List available mandis
- GET /api/market/commodity/<n>  - Get specific commodity rates
- POST /api/market/rates         - Admin: add rate
- PUT  /api/market/rates/<id>    - Admin: update rate
- GET /api/market/trending       - Top movers today
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.market import MarketRate
from datetime import date, datetime, timedelta
import pandas as pd
import os

market_bp = Blueprint('market', __name__)


@market_bp.route('/rates', methods=['GET'])
def get_rates():
    """
    Get market rates with optional filters.
    Query params: mandi, state, district, commodity, date
    """
    query = MarketRate.query

    # Filters
    if request.args.get('state'):
        query = query.filter(MarketRate.state.ilike(f"%{request.args['state']}%"))
    if request.args.get('district'):
        query = query.filter(MarketRate.district.ilike(f"%{request.args['district']}%"))
    if request.args.get('mandi'):
        query = query.filter(MarketRate.mandi_name.ilike(f"%{request.args['mandi']}%"))
    if request.args.get('commodity'):
        query = query.filter(MarketRate.commodity.ilike(f"%{request.args['commodity']}%"))
    if request.args.get('date'):
        try:
            filter_date = datetime.strptime(request.args['date'], '%Y-%m-%d').date()
            query = query.filter(MarketRate.date == filter_date)
        except ValueError:
            pass

    # Default: latest date
    latest_date = db.session.query(db.func.max(MarketRate.date)).scalar()
    if latest_date and not request.args.get('date'):
        query = query.filter(MarketRate.date == latest_date)

    rates = query.order_by(MarketRate.commodity).all()

    return jsonify({
        'success': True,
        'count': len(rates),
        'date': latest_date.isoformat() if latest_date else None,
        'rates': [r.to_dict() for r in rates]
    }), 200


@market_bp.route('/rates/gorakhpur', methods=['GET'])
def get_gorakhpur_rates():
    """Get default Gorakhpur Mandi rates - homepage shortcut"""
    latest_date = db.session.query(db.func.max(MarketRate.date)).scalar()

    rates = MarketRate.query\
        .filter_by(district='Gorakhpur', date=latest_date)\
        .order_by(MarketRate.commodity)\
        .all()

    if not rates:
        # Fallback: any UP mandi
        rates = MarketRate.query\
            .filter_by(state='Uttar Pradesh', date=latest_date)\
            .order_by(MarketRate.commodity)\
            .all()

    return jsonify({
        'success': True,
        'mandi': 'Gorakhpur Mandi, UP',
        'date': latest_date.isoformat() if latest_date else None,
        'rates': [r.to_dict() for r in rates]
    }), 200


@market_bp.route('/mandis', methods=['GET'])
def get_mandis():
    """Get list of all available mandis"""
    mandis = db.session.query(
        MarketRate.mandi_name,
        MarketRate.district,
        MarketRate.state
    ).distinct().all()

    return jsonify({
        'success': True,
        'mandis': [
            {'name': m.mandi_name, 'district': m.district, 'state': m.state}
            for m in mandis
        ]
    }), 200


@market_bp.route('/commodity/<string:name>', methods=['GET'])
def get_commodity_rates(name):
    """Get price history for a specific commodity"""
    # Last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)

    rates = MarketRate.query\
        .filter(MarketRate.commodity.ilike(f"%{name}%"))\
        .filter(MarketRate.date >= thirty_days_ago)\
        .order_by(MarketRate.date.desc())\
        .all()

    if not rates:
        return jsonify({'success': False, 'message': f'No data found for {name}'}), 404

    return jsonify({
        'success': True,
        'commodity': name,
        'history': [r.to_dict() for r in rates]
    }), 200


@market_bp.route('/trending', methods=['GET'])
def get_trending():
    """Get commodities with biggest price changes"""
    latest_date = db.session.query(db.func.max(MarketRate.date)).scalar()
    if not latest_date:
        return jsonify({'success': True, 'trending': []}), 200

    prev_date = latest_date - timedelta(days=1)

    latest = {r.commodity: r for r in MarketRate.query.filter_by(date=latest_date).all()}
    prev = {r.commodity: r for r in MarketRate.query.filter_by(date=prev_date).all()}

    trending = []
    for commodity, curr in latest.items():
        if commodity in prev:
            old_price = prev[commodity].avg_price
            new_price = curr.avg_price
            if old_price > 0:
                change_pct = ((new_price - old_price) / old_price) * 100
                trending.append({
                    'commodity': commodity,
                    'commodity_hindi': curr.commodity_hindi,
                    'commodity_emoji': curr.commodity_emoji,
                    'current_price': new_price,
                    'change_pct': round(change_pct, 2),
                    'direction': 'up' if change_pct > 0 else 'down'
                })

    trending.sort(key=lambda x: abs(x['change_pct']), reverse=True)

    return jsonify({
        'success': True,
        'trending': trending[:10]
    }), 200


@market_bp.route('/upload-csv', methods=['POST'])
@jwt_required()
def upload_market_csv():
    """
    Upload a CSV file to bulk update market rates.
    CSV format: commodity,mandi_name,state,district,min_price,max_price,avg_price,date
    (Admin use or data import)
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No CSV file uploaded'}), 400

    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Only CSV files allowed'}), 400

    try:
        df = pd.read_csv(file)
        required_cols = ['commodity', 'mandi_name', 'state', 'district',
                         'min_price', 'max_price', 'avg_price', 'date']

        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return jsonify({
                'success': False,
                'message': f'Missing columns: {", ".join(missing)}'
            }), 400

        added = 0
        for _, row in df.iterrows():
            rate = MarketRate(
                commodity=str(row['commodity']).strip(),
                commodity_hindi=row.get('commodity_hindi', ''),
                commodity_emoji=row.get('commodity_emoji', ''),
                mandi_name=str(row['mandi_name']).strip(),
                state=str(row['state']).strip(),
                district=str(row['district']).strip(),
                min_price=float(row['min_price']),
                max_price=float(row['max_price']),
                avg_price=float(row['avg_price']),
                unit=row.get('unit', 'quintal'),
                date=datetime.strptime(str(row['date']), '%Y-%m-%d').date()
            )
            db.session.add(rate)
            added += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Successfully imported {added} market rate records'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
