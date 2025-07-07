from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Incoming, Item, Stock
from datetime import datetime
from sqlalchemy import func  

incoming_bp = Blueprint('incoming', __name__)

@incoming_bp.route('/', methods=['GET', 'POST'])
def add():
    items = (
        db.session.query(
            Item.name.label('name'),
            func.coalesce(func.sum(Stock.ava_qty), 0).label('ava_qty')
        )
        .outerjoin(Stock, func.lower(Stock.item_id) == func.lower(Item.name))
        .group_by(Item.name)
        .order_by(Item.name)
        .all()
    )
    
    if request.method == 'POST':
        if 'item_id' in request.form and 'qty' in request.form:
            item_name = request.form['item_id']
            qty = int(request.form['qty'])

            incoming = Incoming(
                item_id=item_name,
                qty=qty,
                created=datetime.utcnow()  
            )
            db.session.add(incoming)

            stock = Stock.query.filter_by(item_id=item_name).first()
            if stock:
                stock.ava_qty += qty
            else:
                stock = Stock(item_id=item_name, ava_qty=qty)
                db.session.add(stock)

            db.session.commit()
            flash("Quantity added successfully", "success")
            return redirect(url_for('incoming.add'))

    return render_template('incoming.html', items=items)


@incoming_bp.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        new_item_name = request.form['new_item_name']
        quantity = int(request.form['quantity']) 
        existing_item = Item.query.filter_by(name=new_item_name).first()
        if existing_item:
            flash("The item already exists", "danger")
        else:
            max_id = (db.session.query(func.max(Stock.id))
                                .filter(Stock.id.isnot(None))
                                .scalar())
            next_id = (max_id or 0) + 1
            new_item = Item(name=new_item_name)
            db.session.add(new_item)
            db.session.commit() 
            flash("New item added successfully!", "success")

            stock = Stock.query.filter_by(item_id=new_item_name).first()
            if stock:
                stock.ava_qty += quantity  
            else:
                stock = Stock(id=next_id,item_id=new_item_name, ava_qty=quantity)  
                db.session.add(stock)

            db.session.commit()  

        return redirect(url_for('incoming.add_item'))

    return render_template('add_item.html')


