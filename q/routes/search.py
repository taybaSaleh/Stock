from flask import Blueprint, render_template, request, flash, send_file
from datetime import datetime
from models import Outgoing, Item
from extensions import db
import pandas as pd
import io
from sqlalchemy import func

search_bp = Blueprint('search', __name__)        


@search_bp.route('/', methods=['GET', 'POST'])
def search():
    items = Item.query.all()         
    results = []                      

    emp_name = emp_dep = item_val = date_raw = ''

    if request.method == 'POST':
        emp_name = request.form.get('emp_name', '').strip()
        emp_dep  = request.form.get('emp_dep',  '').strip()
        item_val = request.form.get('item_id',  '').strip()
        date_raw = request.form.get('date',     '').strip()

        query = Outgoing.query                       

        if emp_name:
            query = query.filter(Outgoing.emp_name.ilike(f"%{emp_name}%"))
        if emp_dep:
            query = query.filter(Outgoing.emp_dep.ilike(f"%{emp_dep}%"))
        if item_val:

            search_val = item_val.strip().lower()

            query = query.filter(
                func.lower(func.trim(Outgoing.item_id)).like(f"%{search_val}%")
            )
            
        if date_raw:
            try:
                input_date = datetime.strptime(date_raw, "%Y-%m-%d").strftime("%m/%d/%Y")
                query = query.filter(Outgoing.created == input_date)
            except ValueError:
                flash("Invalid date format. Expected: YYYY-MM-DD", "danger")

        results = query.all()

    return render_template(
        'search.html',
        items=items,
        results=results,
        emp_name=emp_name,
        emp_dep=emp_dep,
        item_val=item_val,
        date_raw=date_raw
    )


@search_bp.route('/export_excel')
def export_excel():
    """
    يستخدم نفس الفلاتر الواردة في شريط العنوان (?emp_name=...&item_id=...).
    إذا لم تُرسَل فلاتر، يُصدّر كل البيانات.
    """
    emp_name = request.args.get('emp_name', '').strip()
    emp_dep  = request.args.get('emp_dep',  '').strip()
    item_val = request.args.get('item_id',  '').strip()
    date_raw = request.args.get('date',     '').strip()

    query = Outgoing.query

    if emp_name:
        query = query.filter(Outgoing.emp_name.ilike(f"%{emp_name}%"))
    if emp_dep:
        query = query.filter(Outgoing.emp_dep.ilike(f"%{emp_dep}%"))
    if item_val:
        query = query.filter(Outgoing.item_id == item_val)
    if date_raw:
        try:
            input_date = datetime.strptime(date_raw, "%Y-%m-%d").strftime("%m/%d/%Y")
            query = query.filter(Outgoing.created == input_date)
        except ValueError:
            pass      

    data = []
    for q in query.all():
        if q is None:
            continue
        data.append({
            'Item':      q.item_id,
            'Quantity':  q.qty,
            'Employee':  q.emp_name,
            'Department':q.emp_dep,
            'Date':      q.created,
            'Ticket':    q.ticket
        })


    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='SearchResults')
    output.seek(0)

    return send_file(
        output,
        download_name='search_results.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
