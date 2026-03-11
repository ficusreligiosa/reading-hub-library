import random
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify,json
from flask_mysqldb import MySQL
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import MySQLdb.cursors
from flask import send_file
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
import io
import os
import re
import MySQLdb.cursors
from MySQLdb.cursors import DictCursor 
import base64
from functools import wraps
import traceback
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

with open('config.json', 'r') as c:
    params = json.load(c)["params"]
   

app = Flask(__name__)
app.secret_key = "secret123"
# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'the_reading_hub'

UPLOAD_FOLDER_USER = 'static/uploads/'
UPLOAD_FOLDER_RECEIPTS = 'static/uploads/payment_reciepts'

app.config['UPLOAD_FOLDER_USER'] = UPLOAD_FOLDER_USER
app.config['UPLOAD_FOLDER_RECEIPTS'] = UPLOAD_FOLDER_RECEIPTS


# Allowed file extensions for photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

mysql = MySQL(app)

def login_required(f):
    """Decorator to require login for any route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("Please login first to access this page!", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to require specific role(s) for a route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash("Please login first!", "danger")
                return redirect(url_for('login'))
            
            if session.get('role') not in roles:
                flash("You don't have permission to access this page!", "danger")
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.context_processor
def inject_user():
    return dict(
        user_logged_in='username' in session,
        username=session.get('username'),
        user_role=session.get('role')
    )

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('index'))

@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        
        # Step 1: Find the user by username
        cur.execute("SELECT * FROM all_user_data WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()

        # Step 2: Validate user and password
        if user and user[2] == password:
            role = user[3] 
            
            # Store user info in the session
            session['username'] = username
            session['role'] = role
            session['id'] = user[0]

            # Step 3: Redirect based on the role we just fetched
            if role == "Admin":
                return redirect(url_for('select_admin'))
            elif role == "Owner":
                return redirect(url_for('select_owner'))
            elif role == "User":
                return redirect(url_for('user_dashboard'))
            else:
                flash("Login successful, but role is undefined.", "warning")
                return redirect(url_for('login'))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        phone = request.form.get('phone')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Add DictCursor here
        cur.execute("SELECT * FROM members WHERE phone=%s", [phone])
        user = cur.fetchone()
        
        if user:  # Check if user exists
            email = user['email']
            ran = random.randint(1000, 9999)
            message = "Your One time Password is : " + str(ran)
            params = {
                'sendermail': 'palakthakur1309@gmail.com',
                'recievermail': email,
                'subject': 'OTP Verification',
                'message': message
            }
            response = requests.get('http://healtrail.link/mailapi/sendmail.php', params=params)
            session['phone'] = phone
            session['otp'] = ran
            cur.close()
            return redirect(url_for('forgot_password'))  # Redirect to OTP verification page
        else:
            cur.close()
            flash('Phone number not found', 'error')
            return render_template('forgot_password.html')
    
    return render_template('forgot_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO all_user_data (username, password, role) VALUES (%s, %s, %s)',
                       (username, password, role))
        mysql.connection.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Add these imports at the top of your Flask app
from datetime import datetime, timedelta
import traceback

# ============================================
# DASHBOARD STATS API - Already Working
# ============================================
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Total Books
        cur.execute("SELECT COALESCE(SUM(copies), 0) AS total_books FROM books;")
        result = cur.fetchone()
        total_books = result['total_books'] if result else 0

        # Checked Out
        cur.execute("SELECT COUNT(*) AS checked_out FROM borrowers WHERE return_date IS NULL;")
        result = cur.fetchone()
        checked_out = result['checked_out'] if result else 0

        # Overdue Books
        cur.execute("""
            SELECT COUNT(*) AS overdue_books
            FROM borrowers
            WHERE return_date IS NULL AND due_date < CURDATE();
        """)
        result = cur.fetchone()
        overdue_books = result['overdue_books'] if result else 0

        # New Users This Month
        cur.execute("""
            SELECT COUNT(*) AS new_users_this_month
            FROM members
            WHERE MONTH(created_at) = MONTH(CURDATE())
              AND YEAR(created_at) = YEAR(CURDATE());
        """)
        result = cur.fetchone()
        new_users_this_month = result['new_users_this_month'] if result else 0

        cur.close()

        stats = {
            'totalBooks': int(total_books) if total_books else 0,
            'checkedOut': int(checked_out) if checked_out else 0,
            'overdueBooks': int(overdue_books) if overdue_books else 0,
            'newUsersThisMonth': int(new_users_this_month) if new_users_this_month else 0
        }

        return jsonify(stats), 200

    except Exception as e:
        print("❌ Error in get_dashboard_stats:", str(e))
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            'totalBooks': 0,
            'checkedOut': 0,
            'overdueBooks': 0,
            'newUsersThisMonth': 0
        }), 200  # Return 200 with zeros instead of 500


# ============================================
# DASHBOARD ACTIVITY API - NEW
# ============================================
@app.route('/api/dashboard/activity', methods=['GET'])
def get_dashboard_activity():
    """API endpoint to fetch recent activity for admin dashboard"""
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        activities = []

        # Get recent checkouts and returns (last 7 days)
        try:
            cur.execute("""
                SELECT 
                    bk.title,
                    m.name AS member_name,
                    b.borrow_date,
                    b.return_date
                FROM borrowers b
                JOIN books bk ON b.book_id = bk.book_id
                JOIN members m ON b.member_id = m.member_id
                WHERE b.borrow_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                ORDER BY COALESCE(b.return_date, b.borrow_date) DESC
                LIMIT 10
            """)
            borrowing_records = cur.fetchall()
            
            if borrowing_records:
                for record in borrowing_records:
                    try:
                        if record.get('return_date'):
                            # Book was returned
                            time_ago = format_time_ago(record['return_date'])
                            activities.append({
                                'description': f'Book "{record["title"]}" returned by {record["member_name"]}',
                                'timestamp': time_ago,
                                'type': 'return'
                            })
                        else:
                            # Book was checked out
                            time_ago = format_time_ago(record['borrow_date'])
                            activities.append({
                                'description': f'Book "{record["title"]}" checked out by {record["member_name"]}',
                                'timestamp': time_ago,
                                'type': 'checkout'
                            })
                    except Exception as e:
                        print(f"Error processing borrowing record: {e}")
                        continue
        except Exception as e:
            print(f"Error fetching borrowing records: {e}")

        # Get recently registered members
        try:
            cur.execute("""
                SELECT name, created_at
                FROM members
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                ORDER BY created_at DESC
                LIMIT 5
            """)
            recent_members = cur.fetchall()
            
            if recent_members:
                for member in recent_members:
                    try:
                        if member and member.get('created_at'):
                            time_ago = format_time_ago(member['created_at'])
                            activities.append({
                                'description': f'New member {member["name"]} registered',
                                'timestamp': time_ago,
                                'type': 'member_added'
                            })
                    except Exception as e:
                        print(f"Error processing member record: {e}")
                        continue
        except Exception as e:
            print(f"Error fetching member records: {e}")

        cur.close()

        # If no activities found, return empty but successful response
        return jsonify({
            'success': True,
            'activity': activities
        }), 200

    except Exception as e:
        print("❌ Error in get_dashboard_activity:", str(e))
        traceback.print_exc()
        # Return empty activities instead of error
        return jsonify({
            'success': True,
            'activity': []
        }), 200


# ============================================
# HELPER FUNCTION
# ============================================
def format_time_ago(dt):
    """Helper function to format datetime as 'X minutes/hours/days ago'"""
    try:
        if not dt:
            return 'Recently'
        
        # If dt is a string, convert to datetime
        if isinstance(dt, str):
            try:
                dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    dt = datetime.strptime(dt, '%Y-%m-%d')
                except:
                    return 'Recently'
        
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} hour{"s" if hours > 1 else ""} ago'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'{days} day{"s" if days > 1 else ""} ago'
        else:
            return dt.strftime('%b %d, %Y')
    except Exception as e:
        print(f"Error formatting time: {e}")
        return 'Recently'

# Admin dashboard route
@app.route('/admin_dashboard')
@role_required('Admin', 'Owner')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# ... (all your other imports and routes) ...

@app.route('/admin/checked_out')
@role_required('Admin', 'Owner')
def view_checked_out():
    """
    This new function has the endpoint name 'view_checked_out',
    which fixes the BuildError.
    """
    return render_template('view_checked_out.html')




# ... (the rest of your app.py file) ...

@app.route('/user')
@role_required('User')
def user_dashboard():
    """User Dashboard - Shows borrowed books, stats, and quick actions"""
    
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cur = mysql.connection.cursor(DictCursor)
    
    # Get user information
    cur.execute("""
        SELECT name, email, phone, created_at 
        FROM members 
        WHERE member_id = %s
    """, (user_id,))
    user_info = cur.fetchone()
    
    # Get currently borrowed books (Active + Overdue)
    cur.execute("""
        SELECT 
            br.borrow_id,
            br.book_id,
            br.borrow_date,
            br.due_date,
            br.status,
            b.title,
            b.author,
            s.shelf_code,
            DATEDIFF(br.due_date, CURDATE()) as days_remaining,
            CASE 
                WHEN CURDATE() > br.due_date THEN DATEDIFF(CURDATE(), br.due_date)
                ELSE 0 
            END as days_overdue
        FROM borrowers br
        JOIN books b ON br.book_id = b.book_id
        LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
        WHERE br.user_id = %s AND br.status IN ('Borrowed', 'Overdue')
        ORDER BY br.due_date ASC
    """, (user_id,))
    borrowed_books = cur.fetchall()
    
    # Get stats
    cur.execute("""
        SELECT COUNT(*) as total 
        FROM borrowers 
        WHERE user_id = %s
    """, (user_id,))
    total_borrowed = cur.fetchone()['total']
    
    currently_borrowed = len(borrowed_books)
    
    books_due_soon = sum(1 for book in borrowed_books 
                        if 0 <= book['days_remaining'] <= 3 
                        and book['status'] != 'Overdue')
    
    overdue_count = sum(1 for book in borrowed_books if book['status'] == 'Overdue')
    
    fine_per_day = 15
    total_fines = sum(book['days_overdue'] * fine_per_day for book in borrowed_books)
    
    # Get recent borrowing history
    cur.execute("""
        SELECT 
            br.borrow_id,
            br.book_id,
            br.borrow_date,
            br.due_date,
            br.return_date,
            br.status,
            b.title,
            b.author
        FROM borrowers br
        JOIN books b ON br.book_id = b.book_id
        WHERE br.user_id = %s AND br.status = 'Returned'
        ORDER BY br.return_date DESC
        LIMIT 5
    """, (user_id,))
    recent_history = cur.fetchall()
    
    cur.close()
    
    stats = {
        'currently_borrowed': currently_borrowed,
        'books_due_soon': books_due_soon,
        'total_borrowed': total_borrowed,
        'overdue_count': overdue_count,
        'total_fines': total_fines
    }
    
    return render_template('user_dashboard.html',
                         user_info=user_info,
                         borrowed_books=borrowed_books,
                         recent_history=recent_history,
                         stats=stats)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash("New passwords don't match!", "danger")
            return render_template('change_password.html')
        
        user_id = session.get('id')
        cur = mysql.connection.cursor()
        
        # Verify old password
        cur.execute("SELECT password FROM all_user_data WHERE id = %s", (user_id,))
        result = cur.fetchone()
        
        if result[0] != old_password:
            flash("Old password is incorrect!", "danger")
            return render_template('change_password.html')
        
        # Update to new password
        cur.execute("UPDATE all_user_data SET password = %s WHERE id = %s", (new_password, user_id))
        mysql.connection.commit()
        cur.close()
        
        flash("Password changed successfully!", "success")
        return redirect(url_for('user_dashboard'))
    
    return render_template('change_password.html')

@app.route('/add_book', methods=['GET', 'POST'])
@role_required('Admin', 'Owner')
def add_book():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Adding a new genre
        if 'add_genre' in request.form:
            genre_name = request.form['genre_name'].strip().title()
            if genre_name:
                try:
                    cur.execute("INSERT INTO genres (genre_name) VALUES (%s)", (genre_name,))
                    mysql.connection.commit()
                    flash(f"Genre '{genre_name}' added successfully!", "success")
                except Exception:
                    flash(f"Error: Genre '{genre_name}' may already exist!", "danger")
            else:
                flash("Please enter a genre name!", "danger")

        # NEW: Adding a new shelf
        elif 'add_shelf' in request.form:
            shelf_code = request.form['shelf_code'].strip().upper()
            shelf_section = request.form['shelf_section'].strip().title()
            shelf_description = request.form['shelf_description'].strip()
            
            try:
                floor_level = int(request.form['floor_level'])
            except ValueError:
                flash("Invalid floor level!", "danger")
                return redirect(url_for('add_book'))
            
            if shelf_code and shelf_section and shelf_description and floor_level:
                # Validate floor level
                if floor_level < 1 or floor_level > 10:
                    flash("Floor level must be between 1 and 10!", "danger")
                    return redirect(url_for('add_book'))
                
                try:
                    cur.execute(
                        """INSERT INTO shelves (shelf_code, section, description, floor_level) 
                           VALUES (%s, %s, %s, %s)""", 
                        (shelf_code, shelf_section, shelf_description, floor_level)
                    )
                    mysql.connection.commit()
                    flash(f"Shelf '{shelf_code}' added successfully on Floor {floor_level}!", "success")
                except Exception as e:
                    if 'Duplicate entry' in str(e):
                        flash(f"Error: Shelf code '{shelf_code}' already exists!", "danger")
                    else:
                        flash(f"Error adding shelf: {str(e)}", "danger")
            else:
                flash("Please fill all shelf fields!", "danger")

        # Adding a new book
        elif 'add_book' in request.form:
            title = request.form['title'].strip().title()
            author = request.form['author'].strip().title()
            publication = request.form['publication'].strip().title()
            
            # Validate author (no numbers)
            if any(char.isdigit() for char in author):
                flash("Author name cannot contain numbers!", "danger")
                return redirect(url_for('add_book'))
            
            # Validate publication (no numbers)
            if any(char.isdigit() for char in publication):
                flash("Publication name cannot contain numbers!", "danger")
                return redirect(url_for('add_book'))
            
            # Validate minimum length
            if len(title) < 2:
                flash("Title must be at least 2 characters long!", "danger")
                return redirect(url_for('add_book'))
            
            if len(author) < 2:
                flash("Author name must be at least 2 characters long!", "danger")
                return redirect(url_for('add_book'))
            
            if len(publication) < 2:
                flash("Publication name must be at least 2 characters long!", "danger")
                return redirect(url_for('add_book'))
            
            try:
                year = int(request.form['year'])
                price = float(request.form['price']) 
            except ValueError:
                flash("Invalid year or price entered! Please use numbers.", "danger")
                return redirect(url_for('add_book'))

            try:
                copies = int(request.form['copies'])
            except ValueError:
                flash("Invalid number of copies!", "danger")
                return redirect(url_for('add_book'))

            genres = request.form.getlist('genres')
            shelf_id = request.form['shelf_id']
            staff_id = session.get('id')

            # Backend validation
            if not all([title, author, publication, shelf_id, genres]) or copies < 1 or price < 0:
                flash("All fields are required and must be valid!", "danger")
                return redirect(url_for('add_book'))

            # Additional validation for year
            if year < 1500 or year > 2025:
                flash("Year must be between 1500 and 2025!", "danger")
                return redirect(url_for('add_book'))

            # Additional validation for copies and price
            if copies > 100:
                flash("Number of copies cannot exceed 100!", "danger")
                return redirect(url_for('add_book'))
            
            if price > 9999:
                flash("Price cannot exceed ₹9999!", "danger")
                return redirect(url_for('add_book'))

            # Insert into books
            try:
                cur.execute(
                    "INSERT INTO books (title, author, publication, year, price, shelf_id, copies, staff_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (title, author, publication, year, price, shelf_id, copies, staff_id)
                )
                book_id = cur.lastrowid

                # Link genres
                for genre_id in genres:
                    cur.execute(
                        "INSERT INTO book_genres (book_id, genre_id) VALUES (%s, %s)",
                        (book_id, genre_id)
                    )

                mysql.connection.commit()
                flash("Book added successfully with genres!", "success")
                return redirect(url_for('add_book'))
            except Exception as e:
                mysql.connection.rollback()
                flash("Error adding book: " + str(e), "danger")

    # Fetch genres and shelves (including floor_level)
    cur.execute("SELECT genre_id, genre_name FROM genres ORDER BY genre_name")
    all_genres = cur.fetchall()

    cur.execute("SELECT shelf_id, shelf_code, section, description, floor_level FROM shelves ORDER BY shelf_code")
    all_shelves = cur.fetchall()

    cur.close()
    return render_template('add_book.html', genres=all_genres, shelves=all_shelves)

@app.route('/delete_book_page')
@role_required('Admin', 'Owner')
def delete_book_page():
    """Renders the delete book page with optional pre-filled book info."""
    book_id = request.args.get('book_id')

    if book_id:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        book = cur.fetchone()
        cur.close()
        if book:
            # Pass book details to template for pre-fill
            return render_template('delete_book.html', prefill_book=book)
        else:
            flash(f"No book found with ID {book_id}.", "error")
    
    return render_template('delete_book.html', prefill_book=None)


@app.route('/delete_book', methods=['POST'])
@role_required('Admin', 'Owner')
def delete_book():
    """Handles the permanent deletion of a book, with a detailed check for active loans."""
    book_id = request.form.get('book_id')
    if not book_id:
        flash("Invalid request. Book ID was not provided.", "error")
        return redirect(url_for('delete_book_page'))

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = """
            SELECT T2.name 
            FROM borrowers AS T1
            JOIN members AS T2 ON T1.user_id = T2.member_id
            WHERE T1.book_id = %s AND T1.return_date IS NULL
        """
        cur.execute(query, (book_id,))
        active_borrowers = cur.fetchall()

        if active_borrowers:
            borrower_names = [borrower['name'] for borrower in active_borrowers]
            names_str = ", ".join(borrower_names)
            
            cur.execute("SELECT title FROM books WHERE book_id = %s", (book_id,))
            book = cur.fetchone()
            book_title = book['title'] if book else f"Book ID {book_id}"

            flash(f"Cannot delete '{book_title}'. It is on loan to: {names_str}.", "error")
            return redirect(url_for('delete_book_page'))
        
        cur.execute("SELECT title FROM books WHERE book_id = %s", (book_id,))
        book = cur.fetchone()

        if book:
            cur_delete = mysql.connection.cursor()
            cur_delete.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            mysql.connection.commit()
            flash(f"Book '{book['title']}' has been permanently deleted.", "success")
        else:
            flash(f"Error: A book with ID {book_id} could not be found.", "error")
        
        cur.close()
    except Exception as e:
        flash(f"A database error occurred: {e}", "error")

    return redirect(url_for('delete_book_page'))

@app.route('/api/search_books')
@role_required('Admin', 'Owner')
def api_search_books():
    """Provides JSON data for the live book search."""
    query = request.args.get('q', '').strip()

    if len(query) < 2:
        return jsonify([])

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        search_term = f"%{query}%"
        cur.execute(
            "SELECT book_id, title, author FROM books WHERE title LIKE %s OR author LIKE %s LIMIT 10",
            (search_term, search_term)
        )
        books = cur.fetchall()
        cur.close()
        return jsonify(books)
    except Exception as e:
        print(f"Error in API search: {e}")
        return jsonify({"error": "Failed to fetch search results"}), 500

@app.route('/api/book_loan_status/<int:book_id>')
@role_required('Admin', 'Owner')
def api_book_loan_status(book_id):
    """Returns loan status and detailed borrower info for a given book_id."""
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = """
            SELECT 
                T1.borrow_id,
                T2.name, 
                T1.borrow_date, 
                T1.due_date,
                DATEDIFF(CURDATE(), T1.borrow_date) AS days_borrowed
            FROM borrowers AS T1
            JOIN members AS T2 ON T1.user_id = T2.member_id
            WHERE T1.book_id = %s AND T1.return_date IS NULL
        """
        cur.execute(query, (book_id,))
        borrowers = cur.fetchall()

        if borrowers:
            from datetime import date
            today = date.today()
            for borrower in borrowers:
                if borrower['due_date'] and borrower['due_date'] < today:
                    borrower['loan_status'] = 'Overdue'
                else:
                    borrower['loan_status'] = 'Borrowed'
            
            return jsonify({'on_loan': True, 'borrowers': borrowers})
        else:
            return jsonify({'on_loan': False})

    except Exception as e:
        print(f"Error in loan status API: {e}")
        return jsonify({"error": "Failed to fetch loan status"}), 500

@app.route('/update_book', methods=['GET', 'POST'])
@role_required('Admin', 'Owner')
def update_book():
    search_results = None
    book_to_update = None
    cur = mysql.connection.cursor(DictCursor)

    if request.method == 'GET':
        book_id_from_url = request.args.get('book_id')
        if book_id_from_url:
            query = """
                SELECT b.*, s.shelf_code, GROUP_CONCAT(g.genre_name SEPARATOR ', ') as genres
                FROM books b
                LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
                LEFT JOIN book_genres bg ON b.book_id = bg.book_id
                LEFT JOIN genres g ON bg.genre_id = g.genre_id
                WHERE b.book_id = %s
                GROUP BY b.book_id
            """
            cur.execute(query, (book_id_from_url,))
            book_to_update = cur.fetchone()

    if request.method == 'POST':
        if 'search' in request.form:
            search_query = request.form.get('search_query', '').strip()
            if search_query:
                query = """
                    SELECT b.book_id, b.title, b.author, b.copies, b.publication, b.year, b.price, b.shelf_id, s.shelf_code 
                    FROM books b
                    LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
                    WHERE b.title LIKE %s OR b.author LIKE %s OR b.book_id = %s
                """
                search_pattern = f"%{search_query}%"
                try:
                    cur.execute(query, (search_pattern, search_pattern, int(search_query)))
                except ValueError:
                    cur.execute(query, (search_pattern, search_pattern, -1))
                search_results = cur.fetchall()
        
        elif 'book_id' in request.form and request.form['book_id']:
            book_id = request.form['book_id']
            
            update_fields = []
            values = []
            updatable_fields = ['title', 'author', 'publication', 'year', 'copies', 'price', 'shelf_id']
            
            for field in updatable_fields:
                if request.form.get(field):
                    update_fields.append(f"{field} = %s")
                    
                    value = request.form.get(field).strip()
                    if field in ['title', 'author', 'publication']:
                        value = value.title()
                    
                    values.append(value)

            if update_fields:
                values.append(book_id)
                query = f"UPDATE books SET {', '.join(update_fields)} WHERE book_id = %s"
                cur.execute(query, tuple(values))

            genres_to_update = request.form.getlist('genres')
            if genres_to_update:
                cur.execute("DELETE FROM book_genres WHERE book_id = %s", (book_id,))
                genre_values = [(book_id, genre_id) for genre_id in genres_to_update]
                cur.executemany("INSERT INTO book_genres (book_id, genre_id) VALUES (%s, %s)", genre_values)
            
            if update_fields or genres_to_update:
                mysql.connection.commit()
                flash(f"Book ID {book_id} updated successfully!", "success")
                return redirect(url_for('update_book', book_id=book_id))
            else:
                flash("No new information was provided to update.", "warning")

    cur.execute("SELECT shelf_id, shelf_code, section FROM shelves ORDER BY shelf_code")
    all_shelves = cur.fetchall()
    
    cur.execute("SELECT genre_id, genre_name FROM genres ORDER BY genre_name")
    all_genres = cur.fetchall()

    cur.close()
    
    return render_template('update_book.html', 
                            search_results=search_results, 
                            book_to_update=book_to_update,
                            shelves=all_shelves,
                            all_genres=all_genres)

@app.route('/view_all_books')
@role_required('Admin', 'Owner')
def view_all_books():
    """
    Fetches and displays a list of all books in the library.
    """
    cur = mysql.connection.cursor(DictCursor)
    try:
        # MODIFIED QUERY: Added a JOIN to all_user_data to get the username
        query = """
            SELECT 
                b.book_id,
                b.title,
                b.author,
                b.copies,
                b.price,
                s.shelf_code,
                GROUP_CONCAT(DISTINCT g.genre_name SEPARATOR ', ') as genres,
                u.username as added_by_username 
            FROM books b
            LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
            LEFT JOIN book_genres bg ON b.book_id = bg.book_id
            LEFT JOIN genres g ON bg.genre_id = g.genre_id
            LEFT JOIN all_user_data u ON b.staff_id = u.id
            GROUP BY b.book_id, u.username
            ORDER BY b.created_at DESC -- CHANGED: Was b.title
        """
        cur.execute(query)
        all_books = cur.fetchall()
    except Exception as e:
        flash(f"An error occurred while fetching books: {e}", "danger")
        all_books = []
    finally:
        cur.close()

    return render_template('view_all_books.html', books=all_books)

@app.route('/book_detail/<int:book_id>')
def book_detail(book_id):
    """
    Displays detailed information about a specific book.
    Shows different views based on user role (Admin/Owner vs Public).
    """
    cur = mysql.connection.cursor(DictCursor)

    try:
        query_book_details = """
            SELECT 
                b.*, 
                s.shelf_code, 
                s.section,
                GROUP_CONCAT(g.genre_name SEPARATOR ', ') as genres
            FROM books b
            LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
            LEFT JOIN book_genres bg ON b.book_id = bg.book_id
            LEFT JOIN genres g ON bg.genre_id = g.genre_id
            WHERE b.book_id = %s
            GROUP BY b.book_id;
        """
        cur.execute(query_book_details, (book_id,))
        book = cur.fetchone()

        if not book:
            flash(f"Book with ID {book_id} not found.", "error")
            if 'loggedin' in session and session.get('role') in ['Admin', 'Owner']:
                return redirect(url_for('view_all_books'))
            else:
                return redirect(url_for('index'))

        borrowing_history = []
        
        if 'loggedin' in session and session.get('role') in ['Admin', 'Owner']:
            query_history = """
                SELECT
                    m.member_id,
                    m.name,
                    m.email,
                    br.borrow_date,
                    br.due_date,
                    br.status
                FROM borrowers br
                JOIN members m ON br.user_id = m.member_id
                WHERE br.book_id = %s AND br.status IN ('Borrowed', 'Overdue')
                ORDER BY br.due_date;
            """
            cur.execute(query_history, (book_id,))
            borrowing_history = cur.fetchall()

            return render_template("book_detail.html", book=book, borrowing_history=borrowing_history)
        else:
            return render_template("book_detail_public.html", book=book)

    except Exception as e:
        flash(f"An error occurred while fetching book details: {e}", "danger")
        if 'loggedin' in session and session.get('role') in ['Admin', 'Owner']:
            return redirect(url_for('view_all_books'))
        else:
            return redirect(url_for('index'))
    finally:
        cur.close()

@app.route('/browse/genres')
def browse_genres():
    """Display all genres with book counts"""
    cur = mysql.connection.cursor(DictCursor)
    
    query_genres = """
        SELECT 
            g.genre_id,
            g.genre_name,
            COUNT(DISTINCT bg.book_id) as book_count
        FROM genres g
        LEFT JOIN book_genres bg ON g.genre_id = bg.genre_id
        LEFT JOIN books b ON bg.book_id = b.book_id
        GROUP BY g.genre_id, g.genre_name
        HAVING book_count > 0
        ORDER BY g.genre_name;
    """
    cur.execute(query_genres)
    genres = cur.fetchall()
    
    query_sections = """
        SELECT 
            s.section,
            COUNT(DISTINCT b.book_id) as book_count
        FROM shelves s
        LEFT JOIN books b ON s.shelf_id = b.shelf_id
        WHERE s.section IS NOT NULL AND s.section != ''
        GROUP BY s.section
        HAVING book_count > 0
        ORDER BY s.section;
    """
    cur.execute(query_sections)
    sections = cur.fetchall()
    
    cur.close()
    
    return render_template('browse_genres.html', genres=genres, sections=sections)

@app.route('/browse/section/<section_name>')
def browse_by_section(section_name):
    """Display all books in a specific section"""
    cur = mysql.connection.cursor(DictCursor)
    
    query_books = """
        SELECT DISTINCT
            b.book_id,
            b.title,
            b.author,
            b.publication,
            b.year,
            b.copies,
            s.shelf_code,
            s.section,
            GROUP_CONCAT(DISTINCT g.genre_name ORDER BY g.genre_name SEPARATOR ', ') as genres
        FROM books b
        LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
        LEFT JOIN book_genres bg ON b.book_id = bg.book_id
        LEFT JOIN genres g ON bg.genre_id = g.genre_id
        WHERE s.section = %s
        GROUP BY b.book_id
        ORDER BY b.title;
    """
    cur.execute(query_books, (section_name,))
    books = cur.fetchall()
    
    cur.close()
    
    return render_template('browse_by_section.html', 
                         section_name=section_name, 
                         books=books)


@app.route('/browse/genre/<int:genre_id>')
def browse_by_genre(genre_id):
    """Display all books in a specific genre with sorting"""
    sort_by = request.args.get('sort', 'title')  # Get sort parameter from URL
    
    cur = mysql.connection.cursor(DictCursor)
    
    # Get genre name
    cur.execute("SELECT genre_name FROM genres WHERE genre_id = %s", (genre_id,))
    genre = cur.fetchone()
    
    if not genre:
        flash('Genre not found', 'error')
        return redirect(url_for('browse_genres'))
    
    # Determine ORDER BY clause based on sort parameter
    if sort_by == 'author':
        order_clause = "ORDER BY b.author, b.title"
    elif sort_by == 'year':
        order_clause = "ORDER BY b.year DESC, b.title"
    elif sort_by == 'available':
        order_clause = "ORDER BY b.copies DESC, b.title"
    else:  # default: title
        order_clause = "ORDER BY b.title"
    
    # Query with dynamic sorting
    query_books = f"""
        SELECT 
            b.book_id,
            b.title,
            b.author,
            b.publication,
            b.year,
            b.copies,
            s.shelf_code,
            s.section
        FROM books b
        INNER JOIN book_genres bg ON b.book_id = bg.book_id
        LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
        WHERE bg.genre_id = %s
        {order_clause}
    """
    cur.execute(query_books, (genre_id,))
    books = cur.fetchall()
    
    # Add genres for each book
    for book in books:
        cur.execute("""
            SELECT GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') as genres
            FROM book_genres bg
            JOIN genres g ON bg.genre_id = g.genre_id
            WHERE bg.book_id = %s
        """, (book['book_id'],))
        genre_result = cur.fetchone()
        book['genres'] = genre_result['genres'] if genre_result else None
    
    cur.close()
    
    return render_template('browse_by_genre.html', 
                         genre_name=genre['genre_name'], 
                         books=books,
                         genre_id=genre_id,
                         current_sort=sort_by)  





@app.route('/search_books', methods=['GET', 'POST'])
def search_books():
    books = []
    search_term = ""
    search_by = "title"  

    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        search_by = request.form.get('search_by', 'title')

        if search_term:
            query = """
                SELECT b.book_id, b.title, b.author, b.publication, b.year, b.copies,
                       s.shelf_code, s.section, s.description,
                       GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') as genres
                FROM books b
                LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
                LEFT JOIN book_genres bg ON b.book_id = bg.book_id
                LEFT JOIN genres g ON bg.genre_id = g.genre_id
            """
            if search_by == 'author':
                where_clause = "WHERE b.author LIKE %s"
            elif search_by == 'shelf_code':
                where_clause = "WHERE s.shelf_code LIKE %s"
            else:
                where_clause = "WHERE b.title LIKE %s"
            
            final_query = f"{query} {where_clause} GROUP BY b.book_id"
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(final_query, (f'%{search_term}%',))
            books = cur.fetchall()
            cur.close()

    # Check if user is logged in and their role is either 'admin' or 'owner'
    if 'loggedin' in session and session.get('role') in ['admin', 'owner']:
        # If user is an Admin or Owner, show the full-featured admin template
        return render_template('search_books.html', books=books, search_term=search_term, search_by=search_by)
    else:
        # For regular users and non-logged-in visitors, show the public template
        return render_template('search_books_public.html', books=books, search_term=search_term, search_by=search_by)


@app.route('/select_owner', methods=['GET', 'POST'])
def select_owner():
    if request.method == 'POST':
        choice = request.form['choice']
        if choice == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif choice == 'User':
            return redirect(url_for('user_dashboard'))
        elif choice == 'Owner':
            return redirect(url_for('owner_dashboard'))   
    return render_template('select_owner.html')



@app.route('/owner_dashboard')
def owner_dashboard():
    return render_template('owner_dashboard.html')



@app.route('/select_admin', methods=['GET', 'POST'])
def select_admin():
    if request.method == 'POST':
        choice = request.form['choice']
        if choice == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif choice == 'User':
            return redirect(url_for('user_dashboard'))
    return render_template('select_Admin.html')


@app.route('/issue_book', methods=['GET', 'POST'])
@role_required('Admin', 'Owner')
def issue_book():
    cur = mysql.connection.cursor()

    # --- POST request logic (This part is UNCHANGED) ---
    if request.method == 'POST':
        user_id = request.form['user_id']
        borrow_date = request.form['borrow_date']
        due_date = request.form['due_date']
        status = request.form['status']
        amount = request.form['amount'] 
        book_ids = request.form.getlist('book_ids')

        member_search = request.form.get('member_search_query_hidden', '')
        book_search = request.form.get('book_search_query_hidden', '')

        if not book_ids:
            flash("You must select at least one book to issue.", "error")
            return redirect(url_for('issue_book', member_search_query=member_search, book_search_query=book_search))

        success_count = 0
        error_messages = []

        for book_id in book_ids:
            cur.execute("SELECT copies, title FROM books WHERE book_id = %s", [book_id])
            book = cur.fetchone() 
            
            if book and book[0] > 0: 
                cur.execute(
                    "INSERT INTO borrowers (user_id, book_id, borrow_date, due_date, status, amount) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_id, book_id, borrow_date, due_date, status, amount)
                )
                cur.execute("UPDATE books SET copies = copies - 1 WHERE book_id = %s", [book_id])
                success_count += 1
            else:
                title = book[1] if book else f"Unknown Book ID {book_id}" 
                error_messages.append(f"Failed to issue '{title}': Out of stock.")
        
        mysql.connection.commit()
        cur.close()

        if success_count > 0:
            flash(f"Successfully issued {success_count} book(s)!", "success")
        for error in error_messages:
            flash(error, "error")

        return redirect(url_for('issue_book', member_search_query=member_search, book_search_query=book_search))

    # --- GET request logic (THIS PART IS MODIFIED) ---
    members = []
    books = []
    
    member_search_query = request.args.get('member_search_query', '')
    book_search_query = request.args.get('book_search_query', '')
    
    # 1. Search for members (Unchanged)
    if member_search_query:
        query_members = "SELECT member_id, name, email FROM members WHERE name LIKE %s OR email LIKE %s OR member_id LIKE %s"
        search_term_member = f"%{member_search_query}%"
        cur.execute(query_members, (search_term_member, search_term_member, search_term_member))
        members = cur.fetchall()

    # 2. Search for books (THIS IS THE NEW LOGIC)
    if book_search_query:
        # If user IS searching, filter the books
        query_books = "SELECT book_id, title, author FROM books WHERE (title LIKE %s OR author LIKE %s) AND copies > 0"
        search_term_book = f"%{book_search_query}%"
        cur.execute(query_books, (search_term_book, search_term_book))
        books = cur.fetchall()
    else:
        # If user IS NOT searching (initial page load), get ALL available books
        query_all_books = "SELECT book_id, title, author FROM books WHERE copies > 0 ORDER BY title"
        cur.execute(query_all_books)
        books = cur.fetchall()

    cur.close()
    
    return render_template('issue_book.html', 
                           members=members, 
                           books=books, # This list will now be full on page load
                           member_search_query=member_search_query, 
                           book_search_query=book_search_query)


@app.route('/search_active_borrowers')
@role_required('Admin', 'Owner')
def search_active_borrowers():
    query = request.args.get('query', '')
    if len(query) < 2:
        return jsonify([])

    cur = mysql.connection.cursor(DictCursor)
    search_pattern = f'%{query}%'
    
    # This query JOINS members and borrowers and filters by status
    cur.execute("""
        SELECT DISTINCT
            m.member_id,
            m.name,
            m.email
        FROM members m
        JOIN borrowers b ON m.member_id = b.user_id
        WHERE
            (b.status = 'Borrowed' OR b.status = 'Overdue')
            AND m.name LIKE %s
        LIMIT 10
    """, (search_pattern,))
    
    members = cur.fetchall()
    cur.close()
    return jsonify(members)
# Add this import at the top of your file if it's not there
import json
from datetime import datetime
from MySQLdb.cursors import DictCursor

@app.route('/return_book', methods=['GET', 'POST'])
@role_required('Admin', 'Owner')
def return_book():
    # --- POST Request handling (HEAVILY CHANGED) ---
    if request.method == 'POST':
        # Get data that applies to all books
        user_id = request.form['user_id']
        member_name = request.form.get('user_search')
        return_date = request.form['return_date']
        status = request.form['status']
        
        # This is now a list of book IDs from the checkboxes
        book_ids = request.form.getlist('book_ids') 

        if not book_ids:
            flash("Error: You didn't select any books to return.", "error")
            return redirect(url_for('return_book'))

        processing_list = []
        grand_total = 0.0
        cur = mysql.connection.cursor(DictCursor)

        # Loop through every book ID that was checked
        for book_id in book_ids:
            cur.execute("""
                SELECT br.due_date, br.amount, b.title, b.price
                FROM borrowers br
                JOIN books b ON br.book_id = b.book_id
                WHERE br.user_id = %s AND br.book_id = %s AND (br.status = 'Borrowed' OR br.status = 'Overdue')
                ORDER BY br.borrow_date DESC LIMIT 1
            """, (user_id, book_id))
            borrow_record = cur.fetchone()

            if not borrow_record:
                # This book might have been returned in another tab, skip it
                continue 

            due_date_obj = borrow_record['due_date']
            book_title = borrow_record['title']
            initial_borrow_fee = float(borrow_record.get('amount') or 0.0)
            return_date_obj = datetime.strptime(return_date, "%Y-%m-%d")
            
            new_fine = 0
            update_stock = False
            fine_message_part = ""
            days_late = max(0, (return_date_obj.date() - due_date_obj).days)

            if status == 'Returned':
                new_fine = days_late * 15
                update_stock = True
                fine_message_part = f"Late Fine: ₹{new_fine}"
            elif status == 'Damaged':
                # Note: The damage fine is applied PER BOOK
                new_fine = float(request.form.get('damage_fine', 0))
                update_stock = True
                fine_message_part = f"Damage Fine Assessed: ₹{new_fine}"
            elif status == 'Lost':
                book_price = float(borrow_record['price']) if borrow_record['price'] else 0.0
                late_fine = days_late * 15
                new_fine = book_price + late_fine
                update_stock = False
                fine_message_part = f"Fine (Book Price + Late Fee): ₹{new_fine}"

            total_amount_for_this_book = initial_borrow_fee + new_fine
            grand_total += total_amount_for_this_book

            # Add this book's calculated details to our list
            processing_list.append({
                "book_id": book_id,
                "book_title": book_title,
                "total_amount": total_amount_for_this_book,
                "update_stock": update_stock,
                "fine_message_part": fine_message_part
            })
        
        cur.close() # Done reading from DB

        # --- Save the ENTIRE list to the session ---
        session['return_processing_details'] = {
            "user_id": user_id,
            "member_name": member_name,
            "return_date": return_date,
            "status": status, # The single status for all books
            "items": processing_list, # This is our list of books
            "grand_total": grand_total,
            "final_flash_message": f"Processed {len(processing_list)} books. Total Transaction: ₹{grand_total}"
        }

        return redirect(url_for('process_return_payment'))

    # --- GET Request handling (remains unchanged) ---
    prefilled_data = None
    borrow_id = request.args.get('borrow_id')
    
    if borrow_id:
        try:
            cur = mysql.connection.cursor(DictCursor)
            query = """
                SELECT 
                    b.user_id, b.book_id,
                    m.name AS member_name, bk.title AS book_title
                FROM borrowers b
                JOIN members m ON b.user_id = m.member_id
                JOIN books bk ON b.book_id = bk.book_id
                WHERE b.borrow_id = %s
            """
            cur.execute(query, (borrow_id,))
            prefilled_data = cur.fetchone()
            cur.close()
        except Exception as e:
            flash(f"Error fetching loan details: {e}", "error")
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    prefilled_data_json = json.dumps(prefilled_data) if prefilled_data else 'null'
    
    return render_template('return_book.html', 
                           today_date=today_date, 
                           prefilled_data_json=prefilled_data_json)

@app.route('/process_return_payment', methods=['GET', 'POST'])
@role_required('Admin', 'Owner')
def process_return_payment():
    details = session.get('return_processing_details')

    if not details:
        flash("No payment details found. Please start the return process again.", "error")
        return redirect(url_for('return_book'))

    if request.method == 'POST':
        details = session.pop('return_processing_details', None)
        if not details:
            flash("An error occurred (session expired). Please try again.", "error")
            return redirect(url_for('return_book'))

        # --- This is the DB logic, now LOOPED ---
        try:
            cur = mysql.connection.cursor(DictCursor)
            
            # Loop through each item stored in the session
            for item in details['items']:
                cur.execute("""
                    INSERT INTO book_returned_data (user_id, book_id, return_date, status, fine_amount) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (details['user_id'], item['book_id'], details['return_date'], details['status'], item['total_amount']))

                cur.execute("""
                    UPDATE borrowers SET status = %s, return_date = %s, amount = %s 
                    WHERE user_id = %s AND book_id = %s AND (status = 'Borrowed' OR status = 'Overdue')
                """, (details['status'], details['return_date'], item['total_amount'], details['user_id'], item['book_id']))

                if item['update_stock']:
                    cur.execute("UPDATE books SET copies = copies + 1 WHERE book_id = %s", [item['book_id']])
            
            # Commit ONCE after all loops are successful
            mysql.connection.commit()
            cur.close()
            
            flash(details['final_flash_message'], "success")
            return redirect(url_for('borrowed_books'))

        except Exception as e:
            mysql.connection.rollback() # Rollback ALL changes if one fails
            if cur:
                cur.close()
            flash(f"A database error occurred: {e}", "error")
            session['return_processing_details'] = details # Put details back
            return redirect(url_for('process_return_payment'))
        # --- End of looped DB logic ---

    # --- GET request renders the payment page ---
    # No change needed to the render line, but the HTML template will be different
    return render_template('payment_page.html', details=details)

@app.route('/get_user_borrowed_books_details')
@role_required('Admin', 'Owner')
def get_user_borrowed_books_details():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "No user ID provided"}), 400

    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
        SELECT
            b.book_id,
            bk.title,
            b.due_date
        FROM borrowers b
        JOIN books bk ON b.book_id = bk.book_id
        WHERE
            b.user_id = %s
            AND (b.status = 'Borrowed' OR b.status = 'Overdue')
    """, (user_id,))
    books = cur.fetchall()
    cur.close()

    today = datetime.now().date()
    books_with_details = []
    
    for book in books:
        due_date = book['due_date']
        days_overdue = (today - due_date).days
        is_overdue = days_overdue > 0
        book['due_date_str'] = due_date.strftime('%Y-%m-%d')
        book['is_overdue'] = is_overdue
        book['days_overdue'] = max(0, days_overdue)
        books_with_details.append(book)

    return jsonify(books_with_details)


@app.route('/get_borrow_details')
@role_required('Admin', 'Owner')
def get_borrow_details():
    # Get IDs from the URL query parameters
    user_id = request.args.get('user_id')
    book_id = request.args.get('book_id')

    if not user_id or not book_id:
        return jsonify({'error': 'User ID and Book ID are required.'}), 400

    cur = mysql.connection.cursor(DictCursor)

    # Query to get all the details we need for the UI
    query = """
        SELECT 
            m.name AS user_name,
            b.title AS book_title,
            br.due_date
        FROM borrowers br
        JOIN members m ON br.user_id = m.member_id
        JOIN books b ON br.book_id = b.book_id
        WHERE 
            br.user_id = %s 
            AND br.book_id = %s 
            AND (br.status = 'Borrowed' OR br.status = 'Overdue');
    """
    cur.execute(query, (user_id, book_id))
    record = cur.fetchone()
    cur.close()

    if record:
        # Calculate if the book is overdue
        today = datetime.now().date()
        is_overdue = record['due_date'] < today
        days_overdue = (today - record['due_date']).days if is_overdue else 0
        
        # Add overdue info to the response
        record['is_overdue'] = is_overdue
        record['days_overdue'] = days_overdue
        
        return jsonify(record)
    else:
        # If no record is found, return an error
        return jsonify({'error': 'No active borrow record found for this user and book.'}), 404


@app.route('/search_members')
@role_required('Admin', 'Owner')
def search_members():
    query = request.args.get('query', '')
    if len(query) < 2:
        return jsonify([])
    
    cur = mysql.connection.cursor(DictCursor)
    search_pattern = f'%{query}%'
    # This query now ALSO gets the email
    cur.execute("SELECT member_id, name, email FROM members WHERE name LIKE %s LIMIT 10", (search_pattern,))
    members = cur.fetchall()
    cur.close()
    return jsonify(members)

# Endpoint to get books borrowed by a specific user
@app.route('/get_user_borrowed_books')
@role_required('Admin', 'Owner')
def get_user_borrowed_books():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required.'}), 400
        
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
        SELECT b.book_id, b.title 
        FROM borrowers br
        JOIN books b ON br.book_id = b.book_id
        WHERE br.user_id = %s AND (br.status = 'Borrowed' OR br.status = 'Overdue')
    """, (user_id,))
    books = cur.fetchall()
    cur.close()
    return jsonify(books)


@app.route('/out_of_stock', methods=['GET'])
@role_required('Admin', 'Owner')
def out_of_stock():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT b.book_id, b.title, b.author, b.publication, b.year, 
               s.shelf_code, s.section,
               GROUP_CONCAT(g.genre_name ORDER BY g.genre_name SEPARATOR ', ') as genres
        FROM books b
        LEFT JOIN shelves s ON b.shelf_id = s.shelf_id
        LEFT JOIN book_genres bg ON b.book_id = bg.book_id
        LEFT JOIN genres g ON bg.genre_id = g.genre_id
        WHERE b.copies = 0
        GROUP BY b.book_id
    """)
    out_of_stock_books = cur.fetchall()
    cur.close()
    return render_template('out_of_stock.html', books=out_of_stock_books)




@app.route('/add_expense', methods=['GET', 'POST'])
@role_required('Admin', 'Owner')
def add_expense():
    if request.method == 'POST':
        staff_id = session.get('id')
        expense_name = request.form['expense_name']
        amount = request.form['amount']
        date = request.form['date']
        photo = request.files['photo']
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER_RECEIPTS'], filename)
            photo.save(photo_path)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO expenses ( staff_id, expense_name, date, amount, photo_path) VALUES ( %s, %s, %s,%s, %s)", (staff_id, expense_name, date, amount, photo_path))
        mysql.connection.commit()
        flash("Expense added successfully!", "success")
    return render_template('add_expense.html')


@app.route('/overdue', methods=['GET'])
@role_required('Admin', 'Owner')
def overdue():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        UPDATE borrowers 
        SET status = 'Overdue' 
        WHERE due_date < CURDATE() AND status = 'Borrowed'
    """)
    mysql.connection.commit()
    cur.execute("""
        SELECT 
            br.borrow_id, 
            m.member_id AS user_id, 
            m.name AS user_name, 
            b.book_id,
            b.title AS book_title,
            br.due_date,
            DATEDIFF(CURDATE(), br.due_date) AS days_overdue
        FROM borrowers br
        JOIN members m ON br.user_id = m.member_id
        JOIN books b ON br.book_id = b.book_id
        WHERE br.status = 'Overdue'
    """)
    
    overdue_records = cur.fetchall()
    cur.close()

    return render_template('overdue.html', overdue_list=overdue_records)


from flask import jsonify # Make sure to import jsonify at the top of your app.py

# ... your other routes ...

@app.route('/add_members', methods=['GET', 'POST'])
@role_required('Admin', 'Owner')
def add_members():
    if request.method == 'POST':
        # --- MODIFIED: Added .title() ---
        name = request.form['name'].strip().title()
        phone = request.form['phone'].strip()
        house_no = request.form['house_no'].strip()
        locality = request.form['locality'].strip().title()
        city = request.form['city'].strip().title()
        state = request.form['state'].strip().title()
        # --- END MODIFICATION ---
        
        pincode = request.form['pincode'].strip()
        membership_type = request.form['membership_type'].strip()
        email = request.form['email'].strip()
        date_of_birth = request.form['date_of_birth']
        photo = request.files['photo']
        
        # --- NEW: DUPLICATION CHECK ---
        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT email, phone FROM members WHERE email = %s OR phone = %s", (email, phone))
        existing_member = cur.fetchone()
        if existing_member:
            error_message = "A member with this "
            if existing_member['email'] == email:
                error_message += f"email ({email}) "
            if existing_member['phone'] == phone:
                error_message += f"phone number ({phone}) "
            error_message += "already exists."
            flash(error_message, "error")
            return redirect(url_for('add_members'))
        # --- END OF NEW CHECK ---

        # --- REFACTORED PHOTO HANDLING for better paths ---
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            
            photo_save_path = os.path.join(app.config['UPLOAD_FOLDER_USER'], unique_filename)
            photo.save(photo_save_path)

            photo_db_path = f'uploads/{unique_filename}' 
        else:
            flash("Invalid file format or no photo uploaded. Please upload a valid image.", "error")
            return redirect(url_for('add_members'))
        # --- END REFACTOR ---

        address = f"{house_no}, {locality}, {city}, {state} - {pincode}"

        cur.execute(
            "INSERT INTO members (name, phone, address, membership_type, email, date_of_birth, photo_path) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (name, phone, address, membership_type, email, date_of_birth, photo_db_path)
        )
        mysql.connection.commit()
        member_id = cur.lastrowid
        
        # --- FIXED: Added back the credential generation logic ---
        username = str(member_id)
        birth_year = datetime.strptime(date_of_birth, '%Y-%m-%d').year
        first_three = name[:3].capitalize() # Uses the .title() version of name
        password = f"{first_three}{birth_year}"
        
        # Insert into all_user_data for login access
        cur.execute(
            "INSERT INTO all_user_data (username, password, role) VALUES (%s, %s, %s)",
            (username, password, 'User')
        )
        mysql.connection.commit()
        # --- END OF FIX ---
        
        # --- ENHANCED PDF GENERATION ---
        pdf_filename = f"{name.replace(' ', '_')}_ID_{member_id:04d}.pdf"
        pdf_filepath = os.path.join(app.config['UPLOAD_FOLDER_USER'], pdf_filename)

        # Generate the PDF ID card (credit card size: 3.375" x 2.125")
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Create canvas with credit card dimensions
        card_width = 3.375 * inch
        card_height = 2.125 * inch
        c = canvas.Canvas(pdf_filepath, pagesize=(card_width, card_height))

        # Draw card background with gradient effect (using rectangles)
        c.setFillColorRGB(0.1, 0.4, 0.6)  # Dark blue
        c.rect(0, 0, card_width, card_height, fill=1, stroke=0)

        # Add a decorative header bar
        c.setFillColorRGB(0.95, 0.95, 0.95)  # Light gray
        c.rect(0, card_height - 0.6*inch, card_width, 0.6*inch, fill=1, stroke=0)

        # Add organization name and logo area
        c.setFillColorRGB(0.1, 0.2, 0.4)  # Dark blue text
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(card_width/2, card_height - 0.25*inch, "THE READING HUB")
        c.setFont("Helvetica", 8)
        c.drawCentredString(card_width/2, card_height - 0.42*inch, "MEMBER IDENTIFICATION CARD")

        # Add member photo with border
        photo_size = 0.75 * inch
        photo_x = 0.2 * inch
        photo_y = card_height - 1.45 * inch

        try:
            # Draw white background for photo
            c.setFillColorRGB(1, 1, 1)
            c.rect(photo_x - 2, photo_y - 2, photo_size + 4, photo_size + 4, fill=1, stroke=0)
            
            # Add the photo
            img = ImageReader(photo_save_path)
            c.drawImage(img, photo_x, photo_y, width=photo_size, height=photo_size, mask='auto')
            
            # Draw border around photo
            c.setStrokeColorRGB(0.2, 0.2, 0.2)
            c.setLineWidth(1)
            c.rect(photo_x, photo_y, photo_size, photo_size, fill=0, stroke=1)
        except Exception as e:
            print(f"Error adding photo to PDF: {e}")

        # Add member details section - RIGHT AFTER THE PHOTO
        details_x = photo_x + photo_size + 0.15 * inch
        details_y = card_height - 0.85 * inch

        c.setFillColorRGB(1, 1, 1)  # White text
        c.setFont("Helvetica-Bold", 10)
        c.drawString(details_x, details_y, name.upper())

        c.setFont("Helvetica", 7)
        c.drawString(details_x, details_y - 0.15*inch, f"ID: {member_id:04d}")
        c.drawString(details_x, details_y - 0.28*inch, f"Type: {membership_type}")
        c.drawString(details_x, details_y - 0.41*inch, f"Phone: {phone}")
        c.drawString(details_x, details_y - 0.54*inch, f"Email: {email}")
        c.drawString(details_x, details_y - 0.67*inch, f"DOB: {date_of_birth}")

        # Add login credentials in a box at the bottom
        c.setStrokeColorRGB(1, 1, 1)
        c.setLineWidth(0.5)
        c.rect(0.1*inch, 0.05*inch, card_width - 0.2*inch, 0.15*inch, fill=0, stroke=1)

        c.setFont("Helvetica-Bold", 6)
        c.drawString(0.15*inch, 0.12*inch, f"Login: {username}")
        c.drawString(card_width/2 + 0.1*inch, 0.12*inch, f"Pass: {password}")

        c.save()
        # --- END ENHANCED PDF GENERATION ---
        
        # Store details in session to pass to the success page
        new_member_details = {
            'member_id': member_id,
            'name': name,
            'photo_path': photo_db_path, # Pass the web-accessible path
            'username': username,
            'password': password,
            'pdf_filename': pdf_filename
        }
        session['new_member_details'] = new_member_details
        cur.close()
        return redirect(url_for('add_member_success'))

    return render_template('add_members.html')



# --- NEW: SUCCESS PAGE ROUTE ---
@app.route('/add_member_success')
@role_required('Admin', 'Owner')
def add_member_success():
    if 'new_member_details' not in session:
        flash("No member details found. Please add a member first.", "info")
        return redirect(url_for('add_members'))
    
    details = session.pop('new_member_details', None)
    # Set the PDF filename in the session for the download route to find
    if details:
        session['pdf_file'] = details['pdf_filename']
    
    return render_template('add_member_success.html', member=details)

# --- NEW: REAL-TIME VALIDATION API ENDPOINTS ---
@app.route('/check_email')
@role_required('Admin', 'Owner')
def check_email():
    email = request.args.get('email', '')
    if not email:
        return jsonify({'taken': False})
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM members WHERE email = %s", (email,))
    is_taken = cur.fetchone()
    cur.close()
    return jsonify({'taken': bool(is_taken)})

@app.route('/check_phone')
@role_required('Admin', 'Owner')
def check_phone():
    phone = request.args.get('phone', '')
    if not phone:
        return jsonify({'taken': False})
    cur = mysql.connection.cursor()
    cur.execute("SELECT phone FROM members WHERE phone = %s", (phone,))
    is_taken = cur.fetchone()
    cur.close()
    return jsonify({'taken': bool(is_taken)})




@app.route('/download_id_card')
@role_required('Admin', 'Owner')
def download_id_card():
    if 'pdf_file' not in session:
        flash("No ID card available to download.", "error")
        return redirect(url_for('add_members'))
    
    pdf_filename = session.get('pdf_file')
    pdf_filepath = os.path.join(app.config['UPLOAD_FOLDER_USER'], pdf_filename)
    
    if not os.path.exists(pdf_filepath):
        flash("ID card file not found.", "error")
        return redirect(url_for('add_members'))
    
    return send_file(pdf_filepath, as_attachment=True, download_name=pdf_filename)




# Add this new route to your existing app.py file

@app.route('/view_members')
@role_required('Admin', 'Owner')
def view_members():
    search_query = request.args.get('search_query', '')
    
    cur = mysql.connection.cursor(DictCursor)
    
    # FIXED: Added 'address' to the SELECT query
    query = "SELECT member_id, name, phone, email, address, membership_type, created_at FROM members"
    params = []

    if search_query:
        query += " WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s"
        search_pattern = f'%{search_query}%'
        params.extend([search_pattern, search_pattern, search_pattern])
        
    query += " ORDER BY member_id DESC"
    
    cur.execute(query, params)
    members = cur.fetchall()
    cur.close()
    
    # FIXED: Using a more consistent variable name for the template
    return render_template('view_members.html', members=members)



@app.route('/borrowed_books', methods=['GET'])
@role_required('Admin', 'Owner')
def borrowed_books():
    cur = mysql.connection.cursor(DictCursor)
    search_query = request.args.get('search_query', '')
    
    # Updated query to fetch books that are either 'Borrowed' or 'Overdue'.
    # These are all the books currently out of the library.
    query = """
    SELECT br.borrow_id, 
           m.member_id AS user_id, 
           m.name AS user_name, 
           b.book_id,
           b.title AS book_title,
           br.borrow_date, 
           br.due_date, 
           br.status,
           br.amount, 
           DATEDIFF(br.due_date, CURDATE()) AS days_to_go
    FROM borrowers br
    JOIN members m ON br.user_id = m.member_id
    JOIN books b ON br.book_id = b.book_id
"""
    params = []

    # The WHERE clause now checks for both statuses.
    if search_query:
        query += """
        WHERE br.status IN ('Borrowed', 'Overdue')
        AND (br.borrow_id LIKE %s OR m.name LIKE %s OR b.title LIKE %s)
    """
        search_pattern = f'%{search_query}%'
        params.extend([search_pattern, search_pattern, search_pattern])
    else:
        query += " WHERE br.status IN ('Borrowed', 'Overdue')"
        
    cur.execute(query, params)
    data = cur.fetchall()
    cur.close()
    
    return render_template('borrowed_books.html', borrowed_books=data)

@app.route('/member/<int:member_id>')
@role_required('Admin', 'Owner')
def member_detail(member_id):
    cur = mysql.connection.cursor(DictCursor)
    
    # Get member's main details
    cur.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    member = cur.fetchone()
    
    # Get member's borrowing history
    cur.execute("""
        SELECT b.title, br.borrow_date, br.due_date, br.status, br.return_date
        FROM borrowers br
        JOIN books b ON br.book_id = b.book_id
        WHERE br.user_id = %s
        ORDER BY br.borrow_date DESC
    """, (member_id,))
    history = cur.fetchall()
    
    cur.close()
    
    if not member:
        flash("Member not found.", "error")
        return redirect(url_for('view_members'))
        
    return render_template('member_detail.html', member=member, history=history)

# --- NEW: Edit Member Page (Handles GET and POST) ---
@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@role_required('Admin', 'Owner')
def edit_member(member_id):
    cur = mysql.connection.cursor(DictCursor)
    
    # Fetch the member's current data for the form
    cur.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    member = cur.fetchone()
    
    if not member:
        flash("Member not found.", "error")
        return redirect(url_for('view_members'))

    if request.method == 'POST':
        # --- Handle the form submission ---
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        address = request.form['address'].strip()
        membership_type = request.form['membership_type'].strip()
        email = request.form['email'].strip()

        # Basic Validation
        if not name or not phone or not address or not email:
            flash("All fields are required.", "error")
            return render_template('edit_member.html', member=member)
        
        # Check for duplicates (excluding the current member)
        cur.execute("SELECT member_id FROM members WHERE (email = %s OR phone = %s) AND member_id != %s", (email, phone, member_id))
        existing = cur.fetchone()
        if existing:
            flash("Another member with this email or phone number already exists.", "error")
            return render_template('edit_member.html', member=member)

        # Update the database
        cur.execute("""
            UPDATE members
            SET name = %s, phone = %s, address = %s, membership_type = %s, email = %s
            WHERE member_id = %s
        """, (name, phone, address, membership_type, email, member_id))
        
        mysql.connection.commit()
        cur.close()
        
        flash(f"Member '{name}' has been updated successfully.", "success")
        return redirect(url_for('view_members'))

    # --- Handle the initial page load (GET request) ---
    cur.close()
    return render_template('edit_member.html', member=member)




@app.route('/add_stock', methods=['POST'])
@role_required('Admin', 'Owner')
def add_stock():
    book_id = request.form['book_id']
    copies = request.form['copies']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE books SET copies = copies + %s WHERE book_id = %s", (copies, book_id))
    mysql.connection.commit()
    cur.close()
    flash("Stock added successfully!", "success")
    return redirect(url_for('out_of_stock'))




#User routes starts









if __name__ == '__main__':
    app.run(debug=True)
