#!/usr/bin/env python3
"""
Prompt Studio API Server
Flask backend with SQLite database + 兑换码体系
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import string
import random
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'prompt_studio.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_activated INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS prompt_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original_prompt TEXT,
            optimized_prompt TEXT,
            scene TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS redeem_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            creator_id INTEGER,
            used_by INTEGER,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (creator_id) REFERENCES users(id),
            FOREIGN KEY (used_by) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_code(length=12):
    """生成随机兑换码"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def is_admin(user_id):
    """检查是否为管理员"""
    conn = get_db()
    user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user and user['is_admin'] == 1

# ==================== 公开接口 ====================

@app.route('/api/register', methods=['POST'])
def register():
    """注册新用户（需要兑换码）"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    redeem_code = data.get('redeem_code', '').strip().upper()
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    if not redeem_code:
        return jsonify({'error': '兑换码不能为空'}), 400
    
    # 验证兑换码
    conn = get_db()
    code_record = conn.execute(
        'SELECT * FROM redeem_codes WHERE code = ? AND is_active = 1',
        (redeem_code,)
    ).fetchone()
    
    if not code_record:
        conn.close()
        return jsonify({'error': '兑换码无效'}), 400
    
    if code_record['used_by']:
        conn.close()
        return jsonify({'error': '兑换码已被使用'}), 400
    
    try:
        # 创建用户
        cursor = conn.execute(
            'INSERT INTO users (username, email, password_hash, is_activated) VALUES (?, ?, ?, 1)',
            (username, email, hash_password(password))
        )
        user_id = cursor.lastrowid
        
        # 标记兑换码已使用
        conn.execute(
            'UPDATE redeem_codes SET used_by = ?, used_at = CURRENT_TIMESTAMP WHERE code = ?',
            (user_id, redeem_code)
        )
        conn.commit()
        conn.close()
        
        token = secrets.token_hex(16)
        return jsonify({
            'message': '注册成功',
            'token': token,
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'is_admin': 0
            }
        }), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username or email already exists'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    """登录用户"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'error': 'Missing credentials'}), 400
    
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password_hash = ?',
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # 检查是否激活（非管理员且未激活不允许登录）
    if user['is_admin'] != 1 and user['is_activated'] == 0:
        return jsonify({'error': '账号未激活，请联系管理员获取兑换码'}), 403
    
    token = secrets.token_hex(16)
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': user['is_admin']
        }
    })

@app.route('/api/redeem', methods=['POST'])
def redeem_code():
    """用户兑换兑换码（已注册未激活用户使用）"""
    data = request.get_json()
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    redeem_code = data.get('code', '').strip().upper()
    
    if not redeem_code:
        return jsonify({'error': '兑换码不能为空'}), 400
    
    # 从token获取用户（简化版：直接用username）
    username = data.get('username')
    if not username:
        return jsonify({'error': '用户名不能为空'}), 400
    
    conn = get_db()
    
    # 验证兑换码
    code_record = conn.execute(
        'SELECT * FROM redeem_codes WHERE code = ? AND is_active = 1',
        (redeem_code,)
    ).fetchone()
    
    if not code_record:
        conn.close()
        return jsonify({'error': '兑换码无效'}), 400
    
    if code_record['used_by']:
        conn.close()
        return jsonify({'error': '兑换码已被使用'}), 400
    
    # 激活用户
    user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'error': '用户不存在'}), 404
    
    conn.execute(
        'UPDATE redeem_codes SET used_by = ?, used_at = CURRENT_TIMESTAMP WHERE code = ?',
        (user['id'], redeem_code)
    )
    conn.execute('UPDATE users SET is_activated = 1 WHERE id = ?', (user['id'],))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '激活成功'})

# ==================== 管理员接口 ====================

@app.route('/api/admin/generate-code', methods=['POST'])
def generate_redeem_code():
    """生成兑换码（仅管理员）"""
    auth = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    # 简化验证：从请求体获取admin信息
    data = request.get_json()
    admin_id = data.get('admin_id')
    
    if not admin_id or not is_admin(admin_id):
        return jsonify({'error': 'Unauthorized'}), 401
    
    count = data.get('count', 1)
    codes = []
    
    conn = get_db()
    for _ in range(count):
        code = generate_code()
        # 确保不重复
        while conn.execute('SELECT 1 FROM redeem_codes WHERE code = ?', (code,)).fetchone():
            code = generate_code()
        
        conn.execute(
            'INSERT INTO redeem_codes (code, creator_id) VALUES (?, ?)',
            (code, admin_id)
        )
        codes.append(code)
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'codes': codes,
        'count': len(codes)
    })

@app.route('/api/admin/codes', methods=['GET'])
def list_codes():
    """查看兑换码列表（仅管理员）"""
    admin_id = request.args.get('admin_id')
    
    if not admin_id or not is_admin(int(admin_id)):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    codes = conn.execute('''
        SELECT r.id, r.code, r.is_active, r.created_at, r.used_at,
               u.username as used_by_username
        FROM redeem_codes r
        LEFT JOIN users u ON r.used_by = u.id
        ORDER BY r.created_at DESC
    ''').fetchall()
    conn.close()
    
    return jsonify([{
        'id': c['id'],
        'code': c['code'],
        'is_active': c['is_active'],
        'used': bool(c['used_by_username']),
        'used_by': c['used_by_username'],
        'used_at': c['used_at'],
        'created_at': c['created_at']
    } for c in codes])

@app.route('/api/admin/toggle-code/<int:code_id>', methods=['POST'])
def toggle_code(code_id):
    """启用/禁用兑换码（仅管理员）"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    
    if not admin_id or not is_admin(admin_id):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    conn.execute('UPDATE redeem_codes SET is_active = NOT is_active WHERE id = ?', (code_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '更新成功'})

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表（仅管理员）"""
    admin_id = request.args.get('admin_id')
    
    if not admin_id or not is_admin(int(admin_id)):
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    users = conn.execute(
        'SELECT id, username, email, is_admin, is_activated, created_at FROM users'
    ).fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    conn = get_db()
    user_count = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    activated_count = conn.execute('SELECT COUNT(*) as count FROM users WHERE is_activated = 1').fetchone()['count']
    code_count = conn.execute('SELECT COUNT(*) as count FROM redeem_codes').fetchone()['count']
    code_used = conn.execute('SELECT COUNT(*) as count FROM redeem_codes WHERE used_by IS NOT NULL').fetchone()['count']
    prompt_count = conn.execute('SELECT COUNT(*) as count FROM prompt_history').fetchone()['count']
    conn.close()
    return jsonify({
        'users': user_count,
        'activated': activated_count,
        'codes': code_count,
        'codes_used': code_used,
        'prompts': prompt_count
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
