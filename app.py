from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

def get_db():
    return sqlite3.connect("database.db")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()

        if user:
            session['user'] = user[1]
            session['role'] = user[4]
            return redirect('/dashboard')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/')

    db = get_db()
    cur = db.cursor()

    if request.method == 'POST' and session['role'] == 'admin':
        title = request.form['title']
        assigned = request.form['assigned']
        cur.execute("INSERT INTO tasks (title, status, assigned_to) VALUES (?, 'Pending', ?)", (title, assigned))
        db.commit()

    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()

    return render_template('dashboard.html', tasks=tasks, role=session['role'])

@app.route('/update/<int:id>')
def update(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE tasks SET status='Completed' WHERE id=?", (id,))
    db.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    db = get_db()
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT, role TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT, assigned_to TEXT)")

    cur.execute("INSERT OR IGNORE INTO users VALUES (1, 'Admin', 'admin@test.com', '1234', 'admin')")
    cur.execute("INSERT OR IGNORE INTO users VALUES (2, 'User', 'user@test.com', '1234', 'member')")

    db.commit()
    db.close()

    app.run()
