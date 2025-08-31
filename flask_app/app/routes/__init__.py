"""
Main routes blueprint
"""
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """首页 - 现代化的仪表板设计"""
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')