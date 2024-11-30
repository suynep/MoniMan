from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from models import db, User, Entry
from werkzeug.security import check_password_hash, generate_password_hash
from weasyprint import HTML
import io


app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcd1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        
        # Query the user from the database
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):  # Verify hashed password
            # Log the user in
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard after successful login
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # Get form data
        source = request.form.get('source')
        sink = request.form.get('sink')
        entry_type = request.form.get('type')

        # Save entry to the database
        new_entry = Entry(source=source, sink=sink, type=entry_type, user_id=current_user.id)
        db.session.add(new_entry)
        db.session.commit()

        flash('Entry added successfully!', 'success')

    # Query entries for the logged-in user
    user_entries = Entry.query.filter_by(user_id=current_user.id).all()

    # Extract unique "type" values for the sidebar
    unique_types = {entry.type for entry in user_entries}

    return render_template('dashboard.html', entries=user_entries, types=unique_types)

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    # Find the entry by ID
    entry = Entry.query.get_or_404(entry_id)

    # Check if the entry belongs to the current user
    if entry.user_id == current_user.id:
        db.session.delete(entry)  # Delete the entry
        db.session.commit()  # Commit the change to the database
        flash('Entry deleted successfully!', 'success')
    else:
        flash('You cannot delete this entry.', 'danger')

    return redirect(url_for('dashboard'))  # Redirect to the dashboard after deletion

def get_user_entries(user_id):
    entries = Entry.query.filter_by(user_id=user_id).all()
    return entries

@app.route('/download_pdf')
@login_required
def download_pdf():
    # Fetch user entries from the database
    entries = get_user_entries(current_user.id)  # Replace with actual function to fetch entries

    # Render the entries to an HTML template
    rendered = render_template('pdf_template.html', entries=entries, userid=current_user.id, username=current_user.username)

    # Generate PDF from the rendered HTML
    pdf = HTML(string=rendered).write_pdf()

    # Create a BytesIO object to send the PDF as a file
    pdf_io = io.BytesIO(pdf)
    pdf_io.seek(0)

    return send_file(pdf_io, download_name='expense_roster.pdf', as_attachment=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)

