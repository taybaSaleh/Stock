from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
from models import db, Outgoing, Item, Stock ,EmployeeDepartment # Change the import path if necessary
from sqlalchemy import distinct  # add this import
from sqlalchemy import func  
from sqlalchemy.exc import IntegrityError, DataError

outgoing_bp = Blueprint('outgoing', __name__, url_prefix='/outgoing')


@outgoing_bp.route('/', methods=['GET', 'POST'])
def subtract():
    # ---------- available items ----------


    items = (
        db.session.query(
            Item.name.label('name'),
            func.coalesce(func.sum(Stock.ava_qty), 0).label('ava_qty')
        )
        .outerjoin(
            Stock,
            func.lower(Stock.item_id) == func.lower(Item.name)
        )
        .group_by(Item.name)
        .order_by(Item.name)
        .all()
    )



    # ---------- unique employees ----------
    # fetch just name & department, ignore ticket to avoid duplicates
 # ---------- unique employees ----------
# Fetch name & department from EmployeeDepartment, not Outgoing
    employees = (
        db.session.query(
            EmployeeDepartment.employee_name.label('name'),
            EmployeeDepartment.department.label('dep')
        )
        .filter(EmployeeDepartment.employee_name.isnot(None))  # Ensure no empty names
        .distinct()  # To get unique employees based on name & department
        .order_by(EmployeeDepartment.employee_name)  # Order by employee name
        .all()
    )


    # ---------- POST ----------
    if request.method == 'POST':
        item_id  = request.form['item_id']
        qty      = int(request.form['qty'])
        emp_name = request.form.get('emp_name', '')
        emp_dep  = request.form.get('emp_dep', '')
        ticket   = request.form.get('ticket', '')

        stock = (Stock.query
                .filter(func.lower(Stock.item_id) == func.lower(item_id))
                .first())

        if stock and stock.ava_qty >= qty:

            max_id = (db.session.query(func.max(Outgoing.id))
                                .filter(Outgoing.id.isnot(None))
                                .scalar())
            next_id = (max_id or 0) + 1

            outgoing = Outgoing(
                id=next_id,              
                item_id=item_id,
                qty=qty,
                emp_name=emp_name,
                emp_dep=emp_dep,
                ticket=ticket,
                created=datetime.utcnow().strftime('%Y-%m-%d')
            )
            db.session.add(outgoing)

            stock.ava_qty -= qty
            try:
                db.session.commit()
                flash("Quantity deducted and transaction recorded successfully.", "success")
            except (IntegrityError, DataError) as e:
                db.session.rollback()
                current_app.logger.exception(e)
                flash("DB error: " + str(e.orig), "danger")
        else:
            flash("Insufficient quantity or item not found.", "danger")

        return redirect(url_for('outgoing.subtract'))

    # ---------- GET ----------
    return render_template('outgoing.html', items=items, employees=employees)
@outgoing_bp.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        emp_name = request.form['emp_name']
        emp_dep = request.form['emp_dep']

        # Create a new employee record in the EmployeeDepartment table
        try:
            new_employee = EmployeeDepartment(employee_name=emp_name, department=emp_dep)
            db.session.add(new_employee)
            db.session.commit()
            flash("Employee added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error adding employee: " + str(e), "danger")
        return redirect(url_for('outgoing.subtract'))

    return render_template('add_employee.html')
