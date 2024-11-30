import os
import random
import string
from werkzeug.security import generate_password_hash
from app import db, app
from models import User, Entry

# List of random emojis for demo entries
EMOJI_LIST = ['😃', '🛠️', '💅', '🎉', '🎬', '🍕', '🚗', '🏥', '📚', '💻']

# File to store the admin credentials in plain text
ADMIN_CREDENTIALS_FILE = 'admin_credentials.txt'

def clean_database():
    """
    Drops all tables and recreates the database schema.
    """
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("[INFO] Dropped all tables.")

        # Recreate all tables
        db.create_all()
        print("[INFO] Recreated all tables.")

def seed_database():
    """
    Seeds the database with a random admin user and demo entries.
    """
    with app.app_context():
        # Generate random admin user
        username = 'admin_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        hashed_password = generate_password_hash(password, method='sha256')
        
        admin_user = User(username=username, password=hashed_password)
        db.session.add(admin_user)
        db.session.commit()

        print(f"[INFO] Added admin user:")
        print(f"       Username: {username}")
        print(f"       Password: {password}")

        # Save admin credentials to a text file
        with open(ADMIN_CREDENTIALS_FILE, 'w') as f:
            f.write(f"Username: {username}\n")
            f.write(f"Password: {password}\n")
        print(f"[INFO] Admin credentials saved to {ADMIN_CREDENTIALS_FILE}.")

        # Add demo entries
        for i in range(5):  # Add 5 random demo entries
            random_emoji = random.choice(EMOJI_LIST)
            demo_entry = Entry(
                source="demo_source",
                sink=f"demo_sink_{i+1}",
                type=f"demo_{random_emoji}",
                user_id=admin_user.id
            )
            db.session.add(demo_entry)

        db.session.commit()
        print("[INFO] Added 5 demo entries to the admin's dashboard.")

if __name__ == "__main__":
    confirmation = input("This will reset the database. Are you sure? (yes/no): ").strip().lower()
    if confirmation == 'yes':
        clean_database()
        
        seed = input("Do you want to seed the database with demo data? (yes/no): ").strip().lower()
        if seed == 'yes':
            seed_database()
        print("[INFO] Database cleanup complete.")
    else:
        print("[INFO] Operation canceled.")

