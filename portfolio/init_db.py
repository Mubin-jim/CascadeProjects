from app import db, app

with app.app_context():
    # Create all database tables
    db.create_all()
    print("Database initialized successfully!")
