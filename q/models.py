from extensions import db  
class Item(db.Model):
    __tablename__ = 'StockList'
    id   = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Item', db.String, unique=True, nullable=False)

class Stock(db.Model):
    __tablename__ = 'Stock'
    id      = db.Column('ID', db.Integer, primary_key=True)
    item_id = db.Column('Item', db.String)  
    ava_qty = db.Column('AvaQty', db.Integer, nullable=False)
    qty     = db.Column('Qty', db.Integer)
    item = db.relationship('Item', primaryjoin='foreign(Stock.item_id) == Item.name', uselist=False)

class Incoming(db.Model):
    __tablename__ = 'Incoming'
    id      = db.Column(db.Integer, primary_key=True)
    item_id = db.Column('Item', db.String)   
    qty     = db.Column('Qty', db.Integer)
    created = db.Column('IncomingDate', db.Date)

class Outgoing(db.Model):
    __tablename__ = 'Outgoing'
    id        = db.Column('ID1', db.Integer, primary_key=True,autoincrement=True)
    item_id   = db.Column('Item', db.String)  
    qty       = db.Column('Qty', db.Integer)
    emp_name  = db.Column('EmpName', db.String)
    emp_dep   = db.Column('EmpDep', db.String)
    created   = db.Column('OutgoingDate', db.String(10))
    ticket    = db.Column('Ticket', db.String)
    item = db.relationship('Item', primaryjoin='foreign(Outgoing.item_id) == Item.name', uselist=False)

class EmployeeDepartment(db.Model):
    __tablename__ = 'EmployeeDepartment'  # اسم الجدول داخل قاعدة البيانات

    id = db.Column('ID', db.Integer, primary_key=True)  # معرف فريد لكل سجل
    employee_name = db.Column('EmployeeName', db.String(100), nullable=False)  # اسم الموظف
    department = db.Column('Department', db.String(100), nullable=False)  # القسم
    date_added = db.Column('DateAdded', db.DateTime, default=db.func.current_timestamp())  # تاريخ إضافة السجل

    def __repr__(self):
        return f"<EmployeeDepartment(EmployeeName={self.employee_name}, Department={self.department})>"