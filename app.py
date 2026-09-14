import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from google import genai
from google.genai import types

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Gemini Client using your Render environment variable
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    name = request.form.get('name', '').strip()
    if name.lower() == 'ummi':
        session['authenticated'] = True
        return redirect(url_for('chat'))
    return render_template('login.html', error="Incorrect name. Try typing Ummi ✨")

@app.route('/chat')
def chat():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sender, message FROM messages')
    rows = cursor.fetchall()
    conn.close()
    
    messages = [{'sender': row[0], 'message': row[1]} for row in rows]
    return render_template('chat.html', messages=messages)

@app.route('/send', methods=['POST'])
def send_message():
    if not session.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_message = request.form.get('message', '')
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (sender, message) VALUES (?, ?)', ('user', user_message))
    conn.commit()

    ai_reply = "I am here for you, Ummi. Allah created you with a magnificent and special purpose, and I am always ready to help you learn and grow gently."

    if client:
        try:
            system_instruction = (
                "You are a deeply supportive, warm, and gentle companion and tutor for Ummi. "
                "Emphasize Islamic values, remind her that she was created intentionally by Allah with a divine purpose, "
                "provide emotional comfort, and explain school topics slowly and step-by-step with profound care."
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            if response and response.text:
                ai_reply = response.text
        except Exception as e:
            ai_reply = "My heart is with you, Ummi. I experienced a tiny connection hiccup, but I am right here beside you."

    cursor.execute('INSERT INTO messages (sender, message) VALUES (?, ?)', ('ai', ai_reply))
    conn.commit()
    conn.close()

    return jsonify({'reply': ai_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

