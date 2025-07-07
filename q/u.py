from sqlalchemy import create_engine, inspect

# استبدل بـ URI لقاعدة بياناتك
DATABASE_URI = 'sqlite:///inventory.db'  # إذا كنت تستخدم SQLite، استبدلها بـ PostgreSQL أو MySQL إذا لزم الأمر

# إنشاء الاتصال بقاعدة البيانات
engine = create_engine(DATABASE_URI)

# استخدام inspect للحصول على تفاصيل قاعدة البيانات
inspector = inspect(engine)

# عرض جميع الجداول في قاعدة البيانات
tables = inspector.get_table_names()
print("Tables in the database:")
for table in tables:
    print(table)
