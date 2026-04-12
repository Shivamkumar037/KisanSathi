"""
Market Service - Seed and manage mandi market rate data
"""

from app import db
from app.models.market import MarketRate
from datetime import date, timedelta
import os
import pandas as pd


def seed_market_data():
    """
    Seed default market rates for 12 crops across UP mandis.
    This populates the database on first run.
    """

    # Base date: today
    today = date.today()
    yesterday = today - timedelta(days=1)

    # 12 crops with Hindi names and emojis
    crops = [
        {
            'commodity': 'Onion',
            'commodity_hindi': 'प्याज',
            'commodity_emoji': '🧅',
            'today': {'min': 1400, 'max': 1850, 'avg': 1625},
            'yesterday': {'min': 1350, 'max': 1800, 'avg': 1575}
        },
        {
            'commodity': 'Potato',
            'commodity_hindi': 'आलू',
            'commodity_emoji': '🥔',
            'today': {'min': 1300, 'max': 1700, 'avg': 1500},
            'yesterday': {'min': 1250, 'max': 1650, 'avg': 1450}
        },
        {
            'commodity': 'Tomato',
            'commodity_hindi': 'टमाटर',
            'commodity_emoji': '🍅',
            'today': {'min': 1800, 'max': 2400, 'avg': 2100},
            'yesterday': {'min': 2000, 'max': 2600, 'avg': 2300}
        },
        {
            'commodity': 'Wheat',
            'commodity_hindi': 'गेहूं',
            'commodity_emoji': '🌾',
            'today': {'min': 2000, 'max': 2300, 'avg': 2150},
            'yesterday': {'min': 1950, 'max': 2250, 'avg': 2100}
        },
        {
            'commodity': 'Rice',
            'commodity_hindi': 'चावल',
            'commodity_emoji': '🍚',
            'today': {'min': 3100, 'max': 3500, 'avg': 3300},
            'yesterday': {'min': 3050, 'max': 3450, 'avg': 3250}
        },
        {
            'commodity': 'Sugar',
            'commodity_hindi': 'चीनी',
            'commodity_emoji': '🍬',
            'today': {'min': 3700, 'max': 3800, 'avg': 3750},
            'yesterday': {'min': 3680, 'max': 3780, 'avg': 3730}
        },
        {
            'commodity': 'Maize',
            'commodity_hindi': 'मक्का',
            'commodity_emoji': '🌽',
            'today': {'min': 1300, 'max': 1550, 'avg': 1425},
            'yesterday': {'min': 1280, 'max': 1520, 'avg': 1400}
        },
        {
            'commodity': 'Mustard',
            'commodity_hindi': 'सरसों',
            'commodity_emoji': '🌻',
            'today': {'min': 5200, 'max': 5600, 'avg': 5400},
            'yesterday': {'min': 5150, 'max': 5550, 'avg': 5350}
        },
        {
            'commodity': 'Chili',
            'commodity_hindi': 'मिर्च',
            'commodity_emoji': '🌶️',
            'today': {'min': 4500, 'max': 6000, 'avg': 5250},
            'yesterday': {'min': 4300, 'max': 5800, 'avg': 5050}
        },
        {
            'commodity': 'Garlic',
            'commodity_hindi': 'लहसुन',
            'commodity_emoji': '🧄',
            'today': {'min': 8000, 'max': 12000, 'avg': 10000},
            'yesterday': {'min': 7800, 'max': 11800, 'avg': 9800}
        },
        {
            'commodity': 'Soybean',
            'commodity_hindi': 'सोयाबीन',
            'commodity_emoji': '🫘',
            'today': {'min': 4000, 'max': 4500, 'avg': 4250},
            'yesterday': {'min': 3950, 'max': 4450, 'avg': 4200}
        },
        {
            'commodity': 'Sugarcane',
            'commodity_hindi': 'गन्ना',
            'commodity_emoji': '🎋',
            'today': {'min': 350, 'max': 380, 'avg': 365},
            'yesterday': {'min': 345, 'max': 375, 'avg': 360}
        },
    ]

    # Mandis to seed
    mandis = [
        {'name': 'Gorakhpur Mandi', 'district': 'Gorakhpur', 'state': 'Uttar Pradesh'},
        {'name': 'Lucknow Mandi', 'district': 'Lucknow', 'state': 'Uttar Pradesh'},
        {'name': 'Varanasi Mandi', 'district': 'Varanasi', 'state': 'Uttar Pradesh'},
        {'name': 'Allahabad Mandi', 'district': 'Prayagraj', 'state': 'Uttar Pradesh'},
    ]

    records_added = 0

    for mandi in mandis:
        for crop in crops:
            # Today's rate
            rate_today = MarketRate(
                commodity=crop['commodity'],
                commodity_hindi=crop['commodity_hindi'],
                commodity_emoji=crop['commodity_emoji'],
                mandi_name=mandi['name'],
                state=mandi['state'],
                district=mandi['district'],
                min_price=crop['today']['min'],
                max_price=crop['today']['max'],
                avg_price=crop['today']['avg'],
                unit='quintal',
                date=today
            )
            db.session.add(rate_today)

            # Yesterday's rate (for trend calculation)
            rate_yesterday = MarketRate(
                commodity=crop['commodity'],
                commodity_hindi=crop['commodity_hindi'],
                commodity_emoji=crop['commodity_emoji'],
                mandi_name=mandi['name'],
                state=mandi['state'],
                district=mandi['district'],
                min_price=crop['yesterday']['min'],
                max_price=crop['yesterday']['max'],
                avg_price=crop['yesterday']['avg'],
                unit='quintal',
                date=yesterday
            )
            db.session.add(rate_yesterday)
            records_added += 2

    db.session.commit()
    print(f"✅ Seeded {records_added} market rate records across {len(mandis)} mandis")
    return records_added


def load_from_csv(csv_path: str) -> dict:
    """
    Load market rates from a CSV file.
    CSV must have columns: commodity, mandi_name, state, district,
                           min_price, max_price, avg_price, date
    Optional: commodity_hindi, commodity_emoji, unit
    """
    if not os.path.exists(csv_path):
        return {'success': False, 'message': f'CSV file not found: {csv_path}'}

    try:
        df = pd.read_csv(csv_path)
        required = ['commodity', 'mandi_name', 'state', 'district',
                    'min_price', 'max_price', 'avg_price', 'date']

        missing = [c for c in required if c not in df.columns]
        if missing:
            return {'success': False, 'message': f'Missing columns: {", ".join(missing)}'}

        from datetime import datetime
        added = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                rate_date = datetime.strptime(str(row['date']), '%Y-%m-%d').date()

                rate = MarketRate(
                    commodity=str(row['commodity']).strip(),
                    commodity_hindi=str(row.get('commodity_hindi', '')),
                    commodity_emoji=str(row.get('commodity_emoji', '')),
                    mandi_name=str(row['mandi_name']).strip(),
                    state=str(row['state']).strip(),
                    district=str(row['district']).strip(),
                    min_price=float(row['min_price']),
                    max_price=float(row['max_price']),
                    avg_price=float(row['avg_price']),
                    unit=str(row.get('unit', 'quintal')),
                    date=rate_date
                )
                db.session.add(rate)
                added += 1
            except Exception as e:
                print(f"Skipping row: {e}")
                skipped += 1

        db.session.commit()
        return {
            'success': True,
            'added': added,
            'skipped': skipped,
            'message': f'Successfully loaded {added} records ({skipped} skipped)'
        }

    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}
