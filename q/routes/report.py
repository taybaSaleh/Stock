from flask import Blueprint, send_file
import pandas as pd
from io import BytesIO
from models import Stock, Outgoing, Incoming
from extensions import db
from datetime import datetime
from sqlalchemy import func

report_bp = Blueprint('report', __name__)

# ---------- (Outgoing) ----------
@report_bp.route('/outgoing')
def generate_outgoing_report():
    # Filter Outgoing data for the current month using strftime
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Query Outgoing data for the current month
    outgoings = (
        db.session.query(Outgoing)
        .filter(func.strftime('%m', Outgoing.created) == str(current_month).zfill(2))  # Filter by current month
        .filter(func.strftime('%Y', Outgoing.created) == str(current_year))  # Filter by current year
        .all()
    )

    # Prepare data for the Excel file
    data = []
    for out in outgoings:
        # Ensure that 'out' is not None and check item and qty fields
        if out:
            # Ensure out.item exists and is not None
            item_name = (out.item.name if getattr(out, "item", None) else "Unknown")  # Ensure out.item is not None
            
            # Ensure out.qty exists and is not None
            qty = out.qty if out.qty is not None else 0  # Use 0 if qty is None
            
            row = {
                "Item Name": item_name,
                "Qty": str(qty),
                "Employee": str(out.emp_name or ""),
                "Department": str(out.emp_dep or ""),
                "Date": str(out.created or ""),
                "Ticket": str(out.ticket or "")
            }
            data.append(row)

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Convert DataFrame to Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Outgoing Transactions")
    
    output.seek(0)

    # Return the Excel file as response
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="outgoing_transactions.xlsx"
    )





# ---------- (Incoming) ----------

@report_bp.route('/report/incoming')
def generate_incoming_report():
    # Query Incoming data
    incomings = Incoming.query.all()

    # Prepare data for the Excel file
    data = []
    for inc in incomings:
        item_name = inc.item_id or "Unknown"
        qty = inc.qty or 0
        date_str = inc.created.strftime("%Y-%m-%d %H:%M") if inc.created else "N/A"
        
        row = {
            "Item Name": item_name,
            "Quantity": qty,
            "Date": date_str
        }
        data.append(row)

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Convert DataFrame to Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Incoming Transactions")
    
    output.seek(0)

    # Return the Excel file as response
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="incoming_transactions.xlsx"
    )
