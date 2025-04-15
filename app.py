from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from werkzeug.security import generate_password_hash, check_password_hash
import time
import re
from docx import Document
import PyPDF2
import io
import os
from datetime import datetime
from Levenshtein import distance
import json
from functools import wraps
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///search_engine.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# Initialize extensions
db = SQLAlchemy(app)
cache = Cache(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    searches = db.relationship('SearchHistory', backref='user', lazy=True)

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    keyword = db.Column(db.String(200), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    results_count = db.Column(db.Integer, default=0)
    search_time = db.Column(db.Float, default=0.0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Search algorithms
def boyer_moore(text, pattern, case_sensitive=True):
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()
    
    n = len(text)
    m = len(pattern)

    skip = {}
    for i in range(m):
        skip[pattern[i]] = m - i - 1

    i = m - 1
    while i < n:
        j = m - 1
        while text[i] == pattern[j]:
            if j == 0:
                return i
            i -= 1
            j -= 1
        i += max(skip.get(text[i], m), m - j)

    return -1

def kmp_search(text, pattern, case_sensitive=True):
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()
    
    def compute_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        for i in range(1, len(pattern)):
            while length > 0 and pattern[i] != pattern[length]:
                length = lps[length - 1]
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
        return lps

    lps = compute_lps(pattern)
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):
                return i - j
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return -1

def fuzzy_search(text, pattern, max_distance=2):
    words = text.split()
    results = []
    for i, word in enumerate(words):
        if distance(word.lower(), pattern.lower()) <= max_distance:
            results.append((i, word))
    return results

def wildcard_search(text, pattern):
    regex_pattern = pattern.replace('*', '.*').replace('?', '.')
    return [(m.start(), m.group()) for m in re.finditer(regex_pattern, text, re.IGNORECASE)]

# File processing
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")

def extract_text_from_docx(file):
    try:
        doc = Document(io.BytesIO(file.read()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading DOCX file: {str(e)}")

# Utility functions
def highlight_keyword(line, keyword, case_sensitive=True):
    if not case_sensitive:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    else:
        pattern = re.compile(re.escape(keyword))
    
    def highlight(match):
        return f'<span class="highlight">{match.group()}</span>'
    
    return pattern.sub(highlight, line)

def get_context(text, position, context_size=50):
    start = max(0, position - context_size)
    end = min(len(text), position + context_size)
    return text[start:end]

# Routes
@app.route('/')
def index():
    if 'dark_mode' not in session:
        session['dark_mode'] = False
    return render_template('file_upload.html', dark_mode=session.get('dark_mode', False))

@app.route('/toggle_dark_mode')
def toggle_dark_mode():
    session['dark_mode'] = not session.get('dark_mode', False)
    return redirect(request.referrer or url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
            
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', dark_mode=session.get('dark_mode', False))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', dark_mode=session.get('dark_mode', False))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/search_history')
@login_required
def search_history():
    searches = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.timestamp.desc()).all()
    return render_template('search_history.html', searches=searches, dark_mode=session.get('dark_mode', False))

@app.route('/result', methods=['POST'])
@login_required
def result():
    start_time = time.time()
    keyword = request.form.get('keyword', '')
    file = request.files.get('file')
    case_sensitive = request.form.get('caseSensitive') == 'on'
    use_regex = request.form.get('regexSearch') == 'on'
    use_fuzzy = request.form.get('fuzzySearch') == 'on'
    use_wildcard = request.form.get('wildcardSearch') == 'on'
    max_distance = int(request.form.get('maxDistance', 2))

    if not keyword:
        flash('Please enter a keyword to search.')
        return redirect(url_for('index'))

    if not file or file.filename == '':
        flash('Please select a file.')
        return redirect(url_for('index'))

    try:
        if file.filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        elif file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif file.filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        else:
            flash('Unsupported file format. Please upload a .txt, .pdf, or .docx file.')
            return redirect(url_for('index'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))

    results = []
    if use_regex:
        try:
            pattern = re.compile(keyword, 0 if case_sensitive else re.IGNORECASE)
            matches = pattern.finditer(text)
            for match in matches:
                context = get_context(text, match.start())
                results.append({
                    'position': match.start(),
                    'match': match.group(),
                    'context': context
                })
        except re.error:
            flash('Invalid regular expression pattern.')
            return redirect(url_for('index'))
    elif use_fuzzy:
        matches = fuzzy_search(text, keyword, max_distance)
        for position, match in matches:
            context = get_context(text, position)
            results.append({
                'position': position,
                'match': match,
                'context': context
            })
    elif use_wildcard:
        matches = wildcard_search(text, keyword)
        for position, match in matches:
            context = get_context(text, position)
            results.append({
                'position': position,
                'match': match,
                'context': context
            })
    else:
        index = boyer_moore(text, keyword, case_sensitive)
        if index != -1:
            context = get_context(text, index)
            results.append({
                'position': index,
                'match': keyword,
                'context': context
            })

    search_time = round((time.time() - start_time) * 1000, 2)

    # Save search history
    search = SearchHistory(
        user_id=current_user.id,
        keyword=keyword,
        file_name=file.filename,
        results_count=len(results),
        search_time=search_time
    )
    db.session.add(search)
    db.session.commit()

    return render_template('result.html',
                         keyword=keyword,
                         results=results,
                         search_time=search_time,
                         dark_mode=session.get('dark_mode', False))

@app.route('/api/search', methods=['POST'])
@login_required
def api_search():
    data = request.get_json()
    keyword = data.get('keyword')
    text = data.get('text')
    
    if not keyword or not text:
        return jsonify({'error': 'Missing keyword or text'}), 400
    
    results = []
    matches = re.finditer(keyword, text, re.IGNORECASE)
    for match in matches:
        results.append({
            'position': match.start(),
            'match': match.group(),
            'context': get_context(text, match.start())
        })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
