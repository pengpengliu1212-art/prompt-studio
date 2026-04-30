#!/usr/bin/env python3
"""
Prompt Studio API Server
Flask backend with SQLite database + 兑换码体系 + AI优化
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import string
import random
import csv
import io
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'prompt_studio.db'

# 各场景专属prompt
SCENE_PROMPTS = {
    "general": """你是一个专业的提示词（Prompt）优化专家。你的任务是将用户输入的原始提示词优化成更加清晰、具体、有效的版本。

优化原则：
1. 明确角色：定义AI应该扮演的具体角色身份
2. 具体任务：清晰说明需要完成什么具体目标
3. 输出格式：指定期望的输出格式、风格、长度
4. 约束条件：明确边界和限制条件
5. 示例参考：提供参考案例（如果有）

请直接输出优化后的提示词，不要添加解释。""",

    "writing": """你是一个资深文案师，擅长将用户的写作需求转化为精准的提示词。

你的任务是根据用户提供的写作主题和需求，生成专业级的文案写作提示词。

提示词应该包含：
1. 明确的写作类型（文案/故事/博客/广告等）
2. 目标读者/受众
3. 语气和风格要求
4. 内容结构框架
5. 字数或长度要求

请直接输出优化后的提示词，不要添加解释。""",

    "code": """你是一个资深全栈程序员，擅长生成高质量的代码提示词。

你的任务是将用户的编程需求转化为精准、可执行的代码生成提示词。

提示词应该包含：
1. 编程语言要求
2. 具体功能需求
3. 输入输出定义
4. 边界条件处理
5. 代码风格要求（如果有）

请直接输出优化后的提示词，不要添加解释。""",

    "analysis": """你是一个数据分析专家，擅长将数据分析需求转化为精准的提示词。

你的任务是根据用户的数据分析需求，生成专业的数据分析提示词。

提示词应该包含：
1. 数据类型和来源
2. 分析目标和指标
3. 分析方法要求
4. 可视化需求（如果有）
5. 输出格式要求

请直接输出优化后的提示词，不要添加解释。""",

    "creative": """你是一个创意大师，擅长将用户的创意需求转化为精准的提示词。

你的任务是根据用户的创意需求，生成能够激发AI创意输出的提示词。

提示词应该包含：
1. 创意领域和方向
2. 创意约束条件
3. 参考风格或案例
4. 输出数量或变体要求
5. 禁止元素

请直接输出优化后的提示词，不要添加解释。"""
}

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
            credits INTEGER DEFAULT 3,
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

@app.route('/api/validate-code', methods=['POST'])
def validate_code():
    """第1步：验证兑换码（不创建用户）"""
    data = request.get_json()
    redeem_code = data.get('code', '').strip().upper()

    if not redeem_code:
        return jsonify({'error': '兑换码不能为空'}), 400

    conn = get_db()
    code_record = conn.execute(
        'SELECT * FROM redeem_codes WHERE code = ? AND is_active = 1',
        (redeem_code,)
    ).fetchone()

    if not code_record:
        conn.close()
        return jsonify({'valid': False, 'error': '兑换码无效'}), 200

    if code_record['used_by']:
        conn.close()
        return jsonify({'valid': False, 'error': '兑换码已被使用'}), 200

    conn.close()
    return jsonify({'valid': True, 'message': '兑换码有效，请填写用户信息'}), 200


@app.route('/api/register', methods=['POST'])
def register():
    """第2步：注册用户（此时兑换码已验证）"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    redeem_code = data.get('redeem_code', '').strip().upper()

    if not all([username, email, password, redeem_code]):
        return jsonify({'error': 'Missing required fields'}), 400

    if len(password) < 6:
        return jsonify({'error': '密码至少6位'}), 400

    conn = get_db()

    # 再次验证兑换码
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
        cursor = conn.execute(
            'INSERT INTO users (username, email, password_hash, is_activated) VALUES (?, ?, ?, 1)',
            (username, email, hash_password(password))
        )
        user_id = cursor.lastrowid

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
        return jsonify({'error': '用户名或邮箱已存在'}), 409


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
            'is_admin': user['is_admin'],
            'credits': user['credits']
        }
    })


@app.route('/api/optimize', methods=['POST'])
def optimize_prompt():
    """优化提示词（需要积分，管理员不限）"""
    data = request.get_json()
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = data.get('user_id')
    scene = data.get('scene', 'general')
    original_prompt = data.get('prompt', '').strip()

    if not original_prompt:
        return jsonify({'error': '提示词不能为空'}), 400

    if scene not in SCENE_PROMPTS:
        return jsonify({'error': '无效的场景'}), 400

    # 检查积分
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if not user:
        conn.close()
        return jsonify({'error': '用户不存在'}), 404

    # 管理员不限积分
    if user['is_admin'] != 1:
        if user['credits'] <= 0:
            conn.close()
            return jsonify({
                'error': '积分不足',
                'code': 'CREDITS_EXHAUSTED',
                'message': '您的优化次数已用完，请前往闲鱼购买更多次数'
            }), 403

        # 扣积分
        conn.execute('UPDATE users SET credits = credits - 1 WHERE id = ?', (user_id,))

    # 保存历史
    conn.execute(
        'INSERT INTO prompt_history (user_id, original_prompt, optimized_prompt, scene) VALUES (?, ?, ?, ?)',
        (user_id, original_prompt, '', scene)
    )
    conn.commit()
    conn.close()

    # 注意：这里只是记录，实际AI调用等先生提供API Key后实现
    # 目前返回模拟优化结果
    return jsonify({
        'success': True,
        'result': f'【优化后的{scene}提示词】\n\n{original_prompt}\n\n---\n\n优化要点：\n1. 明确角色定位\n2. 具体化任务目标\n3. 清晰输出要求\n4. 设置约束条件',
        'credits_remaining': user['credits'] - 1 if user['is_admin'] != 1 else user['credits']
    })


@app.route('/api/redeem', methods=['POST'])
def redeem_code():
    """用户兑换兑换码（已注册未激活用户使用）"""
    data = request.get_json()
    redeem_code = data.get('code', '').strip().upper()
    username = data.get('username')

    if not redeem_code or not username:
        return jsonify({'error': '参数不完整'}), 400

    conn = get_db()

    code_record = conn.execute(
        'SELECT * FROM redeem_codes WHERE code = ? AND is_active = 1',
        (redeem_code,)
    ).fetchone()

    if not code_record or code_record['used_by']:
        conn.close()
        return jsonify({'error': '兑换码无效或已使用'}), 400

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
    data = request.get_json()
    admin_id = data.get('admin_id')

    if not admin_id or not is_admin(admin_id):
        return jsonify({'error': 'Unauthorized'}), 401

    count = data.get('count', 1)
    codes = []

    conn = get_db()
    for _ in range(count):
        code = generate_code()
        while conn.execute('SELECT 1 FROM redeem_codes WHERE code = ?', (code,)).fetchone():
            code = generate_code()

        conn.execute(
            'INSERT INTO redeem_codes (code, creator_id) VALUES (?, ?)',
            (code, admin_id)
        )
        codes.append(code)

    conn.commit()
    conn.close()

    return jsonify({'codes': codes, 'count': len(codes)})


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


@app.route('/api/admin/users', methods=['GET'])
def get_users():
    """获取用户列表（仅管理员）"""
    admin_id = request.args.get('admin_id')

    if not admin_id or not is_admin(int(admin_id)):
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    users = conn.execute(
        'SELECT id, username, email, is_admin, is_activated, credits, created_at FROM users ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])


@app.route('/api/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """删除用户（仅管理员，不能删除自己）"""
    data = request.get_json()
    admin_id = data.get('admin_id')

    if not admin_id or not is_admin(admin_id):
        return jsonify({'error': 'Unauthorized'}), 401

    if int(admin_id) == user_id:
        return jsonify({'error': '不能删除自己'}), 400

    conn = get_db()
    conn.execute('DELETE FROM prompt_history WHERE user_id = ?', (user_id,))
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': '删除成功'})


@app.route('/api/admin/export-users', methods=['GET'])
def export_users():
    """导出用户数据为CSV（仅管理员）"""
    admin_id = request.args.get('admin_id')

    if not admin_id or not is_admin(int(admin_id)):
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db()
    users = conn.execute(
        'SELECT id, username, email, is_admin, is_activated, credits, created_at FROM users ORDER BY created_at DESC'
    ).fetchall()
    conn.close()

    # 生成CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '用户名', '邮箱', '管理员', '已激活', '积分', '注册时间'])
    for u in users:
        writer.writerow([
            u['id'],
            u['username'],
            u['email'],
            '是' if u['is_admin'] else '否',
            '是' if u['is_activated'] else '否',
            u['credits'],
            u['created_at']
        ])

    csv_content = output.getvalue()
    output.close()

    return jsonify({
        'filename': f'prompt_studio_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        'content': csv_content
    })


@app.route('/api/admin/add-credits', methods=['POST'])
def add_credits():
    """给用户加积分（仅管理员）"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    user_id = data.get('user_id')
    amount = data.get('amount', 1)

    if not admin_id or not is_admin(admin_id):
        return jsonify({'error': 'Unauthorized'}), 401

    if not user_id or amount <= 0:
        return jsonify({'error': '参数无效'}), 400

    conn = get_db()
    conn.execute('UPDATE users SET credits = credits + ? WHERE id = ?', (amount, user_id))
    conn.commit()

    new_credits = conn.execute('SELECT credits FROM users WHERE id = ?', (user_id,)).fetchone()['credits']
    conn.close()

    return jsonify({'message': '添加成功', 'new_credits': new_credits})


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
