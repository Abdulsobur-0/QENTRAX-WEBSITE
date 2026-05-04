import os, uuid
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, session, g
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)
app.secret_key = 'Qx9#mK2$pL7@nR4&wV8!jT1^cB6*hF3'

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXT   = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_MB        = 10
ADMIN_PASS    = 'qentrax2025'   # ← Admin password is set to qentrax2025

app.config['MAX_CONTENT_LENGTH'] = MAX_MB * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── MYSQL CONFIG ──────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Stonefufu1@',
    'database': 'qentrax_db',
    'charset':  'utf8mb4',
    'autocommit': False,
    'connection_timeout': 30,
}

# ── DATABASE CONNECTION ───────────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    # Reconnect if connection dropped
    if not g.db.is_connected():
        g.db.reconnect(attempts=3, delay=1)
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db and db.is_connected():
        db.close()

def query(sql, params=None, fetchone=False, fetchall=False, lastrowid=False):
    """Universal query helper."""
    db  = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, params or ())
    result = None
    if fetchone:
        result = cur.fetchone()
    elif fetchall:
        result = cur.fetchall()
    else:
        db.commit()
        if lastrowid:
            result = cur.lastrowid
    cur.close()
    return result

# ── INIT DATABASE ─────────────────────────────────────────────────────────────
def init_db():
    """Create database, all tables, seed defaults."""
    # Connect without DB first to create it
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset='utf8mb4'
    )
    cur = conn.cursor(dictionary=True)
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.execute(f"USE {DB_CONFIG['database']}")

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            title      VARCHAR(255) NOT NULL,
            `desc`     TEXT,
            tag        VARCHAR(100),
            img        TEXT,
            sort_order INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            title      VARCHAR(255) NOT NULL,
            source     VARCHAR(100),
            date_str   VARCHAR(100),
            link       TEXT,
            `desc`     TEXT,
            img        TEXT,
            sort_order INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS sectors (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            name       VARCHAR(100) NOT NULL,
            short_desc VARCHAR(255),
            full_desc  TEXT,
            icon       VARCHAR(100),
            img        TEXT,
            sort_order INT DEFAULT 0
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS about (
            id     INT PRIMARY KEY DEFAULT 1,
            name   VARCHAR(100),
            title  VARCHAR(255),
            bio    TEXT,
            skills VARCHAR(500),
            photo  TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id          INT PRIMARY KEY DEFAULT 1,
            states      INT DEFAULT 36,
            communities INT DEFAULT 200,
            products    INT DEFAULT 15
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id    INT AUTO_INCREMENT PRIMARY KEY,
            label VARCHAR(255),
            val   INT DEFAULT 0
        )
    ''')

    conn.commit()

    # ── SEED DEFAULTS (only if tables are empty) ──────────────────────────────
    cur.execute('SELECT COUNT(*) AS c FROM ads')
    if cur.fetchone()['c'] == 0:
        cur.executemany(
            'INSERT INTO ads (title, `desc`, tag, img) VALUES (%s, %s, %s, %s)',
            [
                ('Qentrax HMS — AI Hospital Management',
                 'NHIS-compliant AI hospital management with smart diagnostics & NAFDAC drug tracking',
                 'HEALTHCARE',
                 'https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=1200&h=500&fit=crop'),
                ('EduSaaS Africa — CBT Platform',
                 'AI proctoring, Paystack payments, USSD access & WhatsApp alerts',
                 'EDTECH',
                 'https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=1200&h=500&fit=crop'),
                ('FraudGuard POS — Multi-Role System',
                 'Cashier, storekeeper & admin dashboards with fraud detection',
                 'COMMERCE',
                 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&h=500&fit=crop'),
            ]
        )

    cur.execute('SELECT COUNT(*) AS c FROM news')
    if cur.fetchone()['c'] == 0:
        cur.executemany(
            'INSERT INTO news (title, source, date_str, link, `desc`) VALUES (%s, %s, %s, %s, %s)',
            [
                ('Qentrax Africa Launches AI Hospital Management System',
                 'Qentrax', 'May 2025', '#',
                 'The new HMS helps Nigerian hospitals digitize patient records and improve care outcomes.'),
                ('Nigerian Government Announces $500M Tech Fund',
                 'BusinessDay', 'May 2025', '#',
                 'The fund supports homegrown tech innovation across all 36 states.'),
                ('AI Adoption in Nigerian Healthcare Growing 38% Annually',
                 'TechCabal', 'Apr 2025', '#',
                 'More hospitals are adopting AI-powered diagnostic tools nationwide.'),
                ('Kwara State Partners with Tech Hubs for 3B Digital Fund',
                 'The Punch', 'Apr 2025', '#',
                 'Kwara State commits funding to attract and retain digital talent.'),
            ]
        )

    cur.execute('SELECT COUNT(*) AS c FROM sectors')
    if cur.fetchone()['c'] == 0:
        cur.executemany(
            'INSERT INTO sectors (name, short_desc, full_desc, icon) VALUES (%s, %s, %s, %s)',
            [
                ('HEALTHCARE', 'AI diagnostics, HMS, NHIS',
                 'Complete healthcare management: NHIS compliance, NAFDAC drug tracking, AI diagnostics, patient records & billing.',
                 'fas fa-hospital'),
                ('EDUCATION', 'School mgmt, CBT, e-learning',
                 'End-to-end education SaaS: CBT with AI proctoring, fee collection, WhatsApp alerts, USSD access.',
                 'fas fa-graduation-cap'),
                ('COMMERCE', 'POS, fraud detection, inventory',
                 'FraudGuard POS with multi-role dashboards, real-time fraud detection and inventory tracking.',
                 'fas fa-shopping-cart'),
                ('GOVERNANCE', 'Citizen portals, e-gov tools',
                 'Digital governance solutions: citizen data platforms and automated workflows.',
                 'fas fa-landmark'),
                ('FINANCE', 'Paystack, lending, wallets',
                 'Fintech integrations: Paystack payments, digital wallets and micro-lending.',
                 'fas fa-chart-line'),
                ('AGRICULTURE', 'Supply chain, farm tracking',
                 'AgriTech solutions: farm management and supply chain digitization.',
                 'fas fa-leaf'),
            ]
        )

    cur.execute('SELECT COUNT(*) AS c FROM about')
    if cur.fetchone()['c'] == 0:
        cur.execute(
            'INSERT INTO about (id, name, title, bio, skills, photo) VALUES (1, %s, %s, %s, %s, %s)',
            (
                'Abdulsobur',
                'Founder & CEO, Qentrax Africa',
                'Qentrax Africa is building the digital infrastructure for a new Nigeria. We specialize in AI-powered SaaS solutions across healthcare, education, governance, and commerce.\n\nFounded in Ilorin, Kwara State, and building for the whole continent.',
                'Flask,FastAPI,React,MySQL,PostgreSQL,AI/ML,Python,SaaS',
                ''
            )
        )

    cur.execute('SELECT COUNT(*) AS c FROM stats')
    if cur.fetchone()['c'] == 0:
        cur.execute('INSERT INTO stats (id, states, communities, products) VALUES (1, 36, 200, 15)')

    cur.execute('SELECT COUNT(*) AS c FROM insights')
    if cur.fetchone()['c'] == 0:
        cur.executemany('INSERT INTO insights (label, val) VALUES (%s, %s)', [
            ('Healthcare Digitalization', 38),
            ('SME Tech Adoption', 45),
            ('E-Gov Readiness', 31),
            ('EdTech Penetration', 52),
        ])

    conn.commit()
    cur.close()
    conn.close()
    print('✓ MySQL database ready')

# ── HELPERS ───────────────────────────────────────────────────────────────────
def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# ── AUTH ──────────────────────────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data and data.get('password') == ADMIN_PASS:
        session['admin'] = True
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': 'Wrong password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@app.route('/api/me')
def me():
    return jsonify({'admin': bool(session.get('admin'))})

# ── FILE UPLOAD ───────────────────────────────────────────────────────────────
@app.route('/api/upload', methods=['POST'])
@admin_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    f = request.files['file']
    if not f.filename or not allowed(f.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    ext  = f.filename.rsplit('.', 1)[1].lower()
    name = str(uuid.uuid4()) + '.' + ext
    f.save(os.path.join(UPLOAD_FOLDER, name))
    return jsonify({'ok': True, 'url': f'/static/uploads/{name}'})

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ── ADS ───────────────────────────────────────────────────────────────────────
@app.route('/api/ads')
def get_ads():
    return jsonify(query('SELECT * FROM ads ORDER BY sort_order, id', fetchall=True) or [])

@app.route('/api/ads', methods=['POST'])
@admin_required
def create_ad():
    d = request.get_json()
    id = query('INSERT INTO ads (title, `desc`, tag, img) VALUES (%s,%s,%s,%s)',
               (d.get('title',''), d.get('desc',''), d.get('tag',''), d.get('img','')), lastrowid=True)
    return jsonify({'ok': True, 'id': id})

@app.route('/api/ads/<int:id>', methods=['PUT'])
@admin_required
def update_ad(id):
    d = request.get_json()
    query('UPDATE ads SET title=%s, `desc`=%s, tag=%s, img=%s WHERE id=%s',
          (d.get('title'), d.get('desc'), d.get('tag'), d.get('img'), id))
    return jsonify({'ok': True})

@app.route('/api/ads/<int:id>', methods=['DELETE'])
@admin_required
def delete_ad(id):
    query('DELETE FROM ads WHERE id=%s', (id,))
    return jsonify({'ok': True})

# ── NEWS ──────────────────────────────────────────────────────────────────────
@app.route('/api/news')
def get_news():
    return jsonify(query('SELECT * FROM news ORDER BY id DESC', fetchall=True) or [])

@app.route('/api/news', methods=['POST'])
@admin_required
def create_news():
    d = request.get_json()
    id = query('INSERT INTO news (title, source, date_str, link, `desc`, img) VALUES (%s,%s,%s,%s,%s,%s)',
               (d.get('title',''), d.get('source',''), d.get('date_str',''),
                d.get('link','#'), d.get('desc',''), d.get('img','')), lastrowid=True)
    return jsonify({'ok': True, 'id': id})

@app.route('/api/news/<int:id>', methods=['PUT'])
@admin_required
def update_news(id):
    d = request.get_json()
    query('UPDATE news SET title=%s, source=%s, date_str=%s, link=%s, `desc`=%s, img=%s WHERE id=%s',
          (d.get('title'), d.get('source'), d.get('date_str'),
           d.get('link'), d.get('desc'), d.get('img'), id))
    return jsonify({'ok': True})

@app.route('/api/news/<int:id>', methods=['DELETE'])
@admin_required
def delete_news(id):
    query('DELETE FROM news WHERE id=%s', (id,))
    return jsonify({'ok': True})

# ── SECTORS ───────────────────────────────────────────────────────────────────
@app.route('/api/sectors')
def get_sectors():
    return jsonify(query('SELECT * FROM sectors ORDER BY sort_order, id', fetchall=True) or [])

@app.route('/api/sectors', methods=['POST'])
@admin_required
def create_sector():
    d = request.get_json()
    id = query('INSERT INTO sectors (name, short_desc, full_desc, icon, img) VALUES (%s,%s,%s,%s,%s)',
               (d.get('name',''), d.get('short_desc',''), d.get('full_desc',''),
                d.get('icon','fas fa-chart-line'), d.get('img','')), lastrowid=True)
    return jsonify({'ok': True, 'id': id})

@app.route('/api/sectors/<int:id>', methods=['PUT'])
@admin_required
def update_sector(id):
    d = request.get_json()
    query('UPDATE sectors SET name=%s, short_desc=%s, full_desc=%s, icon=%s, img=%s WHERE id=%s',
          (d.get('name'), d.get('short_desc'), d.get('full_desc'),
           d.get('icon'), d.get('img'), id))
    return jsonify({'ok': True})

@app.route('/api/sectors/<int:id>', methods=['DELETE'])
@admin_required
def delete_sector(id):
    query('DELETE FROM sectors WHERE id=%s', (id,))
    return jsonify({'ok': True})

# ── ABOUT ─────────────────────────────────────────────────────────────────────
@app.route('/api/about')
def get_about():
    return jsonify(query('SELECT * FROM about WHERE id=1', fetchone=True) or {})

@app.route('/api/about', methods=['PUT'])
@admin_required
def update_about():
    d = request.get_json()
    query('UPDATE about SET name=%s, title=%s, bio=%s, skills=%s WHERE id=1',
          (d.get('name'), d.get('title'), d.get('bio'), d.get('skills')))
    return jsonify({'ok': True})

@app.route('/api/about/photo', methods=['POST'])
@admin_required
def upload_about_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    f = request.files['file']
    if not f.filename or not allowed(f.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    # Delete old file from disk
    old = query('SELECT photo FROM about WHERE id=1', fetchone=True)
    if old and old.get('photo','').startswith('/static/uploads/'):
        old_path = os.path.join(BASE_DIR, old['photo'].lstrip('/'))
        if os.path.exists(old_path):
            os.remove(old_path)
    ext  = f.filename.rsplit('.', 1)[1].lower()
    name = 'profile_' + str(uuid.uuid4()) + '.' + ext
    f.save(os.path.join(UPLOAD_FOLDER, name))
    url = f'/static/uploads/{name}'
    query('UPDATE about SET photo=%s WHERE id=1', (url,))
    return jsonify({'ok': True, 'url': url})

@app.route('/api/about/photo', methods=['DELETE'])
@admin_required
def delete_about_photo():
    old = query('SELECT photo FROM about WHERE id=1', fetchone=True)
    if old and old.get('photo','').startswith('/static/uploads/'):
        old_path = os.path.join(BASE_DIR, old['photo'].lstrip('/'))
        if os.path.exists(old_path):
            os.remove(old_path)
    query('UPDATE about SET photo=%s WHERE id=1', ('',))
    return jsonify({'ok': True})

# ── STATS & INSIGHTS ──────────────────────────────────────────────────────────
@app.route('/api/stats')
def get_stats():
    s   = query('SELECT * FROM stats WHERE id=1', fetchone=True)
    ins = query('SELECT * FROM insights ORDER BY id', fetchall=True)
    return jsonify({'stats': s or {}, 'insights': ins or []})

@app.route('/api/stats', methods=['PUT'])
@admin_required
def update_stats():
    d = request.get_json()
    query('UPDATE stats SET states=%s, communities=%s, products=%s WHERE id=1',
          (d.get('states', 36), d.get('communities', 200), d.get('products', 15)))
    return jsonify({'ok': True})

@app.route('/api/insights', methods=['POST'])
@admin_required
def add_insight():
    d = request.get_json()
    id = query('INSERT INTO insights (label, val) VALUES (%s, %s)',
               (d.get('label',''), d.get('val', 0)), lastrowid=True)
    return jsonify({'ok': True, 'id': id})

@app.route('/api/insights/<int:id>', methods=['PUT'])
@admin_required
def update_insight(id):
    d = request.get_json()
    query('UPDATE insights SET label=%s, val=%s WHERE id=%s',
          (d.get('label'), d.get('val'), id))
    return jsonify({'ok': True})

@app.route('/api/insights/<int:id>', methods=['DELETE'])
@admin_required
def delete_insight(id):
    query('DELETE FROM insights WHERE id=%s', (id,))
    return jsonify({'ok': True})

# ── SERVE FRONTEND ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), path)

# ── START ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)