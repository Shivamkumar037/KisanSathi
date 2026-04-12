"""
KrishiVani Database Management Script
Run: python manage.py <command>

Commands:
  init_db       - Initialize database and seed data
  seed_market   - Re-seed market rate data
  seed_schemes  - Re-seed government schemes
  load_csv      - Load market rates from CSV file
  reset_db      - Drop and recreate all tables (DANGER!)
  create_admin  - Create an admin user
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db


def init_db():
    """Initialize database with all tables and seed data"""
    app = create_app()
    with app.app_context():
        print("🔨 Creating all tables...")
        db.create_all()
        print("✅ Tables created")

        from app.services.market_service import seed_market_data
        from app.services.scheme_service import seed_scheme_data

        print("📊 Seeding market data...")
        seed_market_data()

        print("📋 Seeding government schemes...")
        seed_scheme_data()

        print("\n✅ Database initialized successfully!")
        print("🚀 Run: python run.py to start the server")


def seed_market():
    """Re-seed market data"""
    app = create_app()
    with app.app_context():
        from app.models.market import MarketRate
        from app.services.market_service import seed_market_data

        count = MarketRate.query.count()
        print(f"Current records: {count}")

        seed_market_data()
        print(f"New total: {MarketRate.query.count()} records")


def seed_schemes():
    """Re-seed government schemes"""
    app = create_app()
    with app.app_context():
        from app.models.scheme import GovernmentScheme
        from app.services.scheme_service import seed_scheme_data

        # Clear existing
        GovernmentScheme.query.delete()
        db.session.commit()

        seed_scheme_data()
        print(f"Total schemes: {GovernmentScheme.query.count()}")


def load_csv(csv_path: str):
    """Load market rates from CSV file"""
    app = create_app()
    with app.app_context():
        from app.services.market_service import load_from_csv
        result = load_from_csv(csv_path)
        print(result['message'] if result['success'] else f"Error: {result['message']}")


def reset_db():
    """DANGER: Drop and recreate all tables"""
    confirm = input("⚠️  This will DELETE all data! Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("Cancelled.")
        return

    app = create_app()
    with app.app_context():
        print("🗑️  Dropping all tables...")
        db.drop_all()
        print("🔨 Creating tables...")
        db.create_all()
        print("✅ Database reset complete")


def create_admin():
    """Create an admin/test user"""
    app = create_app()
    with app.app_context():
        from app.models.user import User

        phone = input("Phone number: ").strip()
        name = input("Name: ").strip()
        password = input("Password: ").strip()

        if User.query.filter_by(phone=phone).first():
            print(f"User with phone {phone} already exists")
            return

        user = User(
            name=name,
            phone=phone,
            state='Uttar Pradesh',
            district='Gorakhpur'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"✅ Admin user created: {name} ({phone})")


def show_stats():
    """Show database statistics"""
    app = create_app()
    with app.app_context():
        from app.models.user import User
        from app.models.market import MarketRate
        from app.models.scheme import GovernmentScheme
        from app.models.community import CommunityPost, Comment
        from app.models.crop import CropScan
        from app.models.chat import ChatMessage

        print("\n📊 KrishiVani Database Stats")
        print("=" * 40)
        print(f"👥 Users:           {User.query.count()}")
        print(f"🌾 Crop Scans:      {CropScan.query.count()}")
        print(f"📈 Market Rates:    {MarketRate.query.count()}")
        print(f"📋 Schemes:         {GovernmentScheme.query.count()}")
        print(f"📝 Community Posts: {CommunityPost.query.count()}")
        print(f"💬 Comments:        {Comment.query.count()}")
        print(f"🤖 Chat Messages:   {ChatMessage.query.count()}")
        print("=" * 40)


if __name__ == '__main__':
    commands = {
        'init_db': init_db,
        'seed_market': seed_market,
        'seed_schemes': seed_schemes,
        'reset_db': reset_db,
        'create_admin': create_admin,
        'stats': show_stats,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("KrishiVani Management Tool")
        print("\nUsage: python manage.py <command>")
        print("\nAvailable commands:")
        for cmd, func in commands.items():
            print(f"  {cmd:<20} - {func.__doc__.strip().split(chr(10))[0]}")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'load_csv':
        if len(sys.argv) < 3:
            print("Usage: python manage.py load_csv <path_to_csv>")
            sys.exit(1)
        load_csv(sys.argv[2])
    else:
        commands[command]()
