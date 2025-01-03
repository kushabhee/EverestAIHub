from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('everestaihub.db')
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    role TEXT CHECK(role IN ('Student', 'Parent', 'Faculty')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    query TEXT,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Utility function to log actions
def log_action(action):
    conn = sqlite3.connect('everestaihub.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs (action) VALUES (?)", (action,))
    conn.commit()
    conn.close()

# FIX: Added Home Route for '/' to avoid 404 error
@app.route('/')
def home():
    return "Welcome to EverestAIHub API!"

# FIX: Added Favicon Route to handle '/favicon.ico'
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Empty response with status code 204 (No Content)

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    role = data.get('role')

    if not name or role not in ['Student', 'Parent', 'Faculty']:
        return jsonify({'error': 'Invalid input'}), 400

    conn = sqlite3.connect('everestaihub.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, role) VALUES (?, ?)", (name, role))
    user_id = c.lastrowid
    conn.commit()
    conn.close()

    log_action(f"User registered: {name} ({role})")

    return jsonify({'message': 'User registered successfully', 'user_id': user_id})

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    user_id = data.get('user_id')
    query = data.get('query')

    if not user_id or not query:
        return jsonify({'error': 'Invalid input'}), 400

    # Example: Simple query processing
    response = "Sorry, I don’t have an answer for that right now."
    if 'admission' in query.lower():
        response = "Admissions are open from January to March."
    elif 'scholarship' in query.lower():
        response = "Scholarships are available for students with a GPA of 3.5 and above."

    conn = sqlite3.connect('everestaihub.db')
    c = conn.cursor()
    c.execute("INSERT INTO queries (user_id, query, response) VALUES (?, ?, ?)", (user_id, query, response))
    conn.commit()
    conn.close()

    log_action(f"Query processed for user_id {user_id}: {query}")

    return jsonify({'response': response})

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    user_id = data.get('user_id')
    feedback = data.get('feedback')

    if not user_id or not feedback:
        return jsonify({'error': 'Invalid input'}), 400

    conn = sqlite3.connect('everestaihub.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback (user_id, feedback) VALUES (?, ?)", (user_id, feedback))
    conn.commit()
    conn.close()

    log_action(f"Feedback submitted by user_id {user_id}: {feedback}")

    return jsonify({'message': 'Feedback submitted successfully'})

@app.route('/logs', methods=['GET'])
def get_logs():
    conn = sqlite3.connect('everestaihub.db')
    c = conn.cursor()
    c.execute("SELECT * FROM logs")
    logs = c.fetchall()
    conn.close()

    return jsonify({'logs': logs})

if __name__ == '__main__':
    app.run(debug=True)
