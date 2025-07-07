from flask import Blueprint, render_template
from models import Stock

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    low_stock = Stock.query.filter(Stock.ava_qty < 5).all()
    return render_template('dashboard.html', low_stock=low_stock)
