from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS employee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL NOT NULL
        )
    ''')
    # Only run once for initial admin
    admin = db.execute("SELECT * FROM admin WHERE username = 'admin'").fetchone()
    if not admin:
        hashed_pwd = generate_password_hash("admin123")
        db.execute('INSERT INTO admin (username, password) VALUES (?, ?)', ("admin", hashed_pwd))
    db.commit()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        admin = db.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()
        if admin and check_password_hash(admin['password'], password):
            session['admin'] = username
            return redirect('/dashboard')
        flash("Invalid login credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/login')
    db = get_db()
    employees = db.execute('SELECT * FROM employee').fetchall()
    return render_template('dashboard.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if 'admin' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        salary = request.form['salary']
        db = get_db()
        db.execute('INSERT INTO employee (name, email, position, salary) VALUES (?, ?, ?, ?)',
                   (name, email, position, salary))
        db.commit()
        return redirect('/dashboard')
    return render_template('add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    if 'admin' not in session:
        return redirect('/login')
    db = get_db()
    employee = db.execute('SELECT * FROM employee WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        salary = request.form['salary']
        db.execute('UPDATE employee SET name=?, email=?, position=?, salary=? WHERE id=?',
                   (name, email, position, salary, id))
        db.commit()
        return redirect('/dashboard')
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<int:id>')
def delete_employee(id):
    if 'admin' not in session:
        return redirect('/login')
    db = get_db()
    db.execute('DELETE FROM employee WHERE id=?', (id,))
    db.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
