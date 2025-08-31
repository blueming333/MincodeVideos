"""
Main routes - 首页和仪表板
"""
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """首页 - 现代化的AI视频工具入口"""
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    """仪表板 - 工作流总览"""
    return render_template('dashboard.html')