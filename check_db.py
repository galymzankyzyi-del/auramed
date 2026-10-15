
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "med.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)

    tables = cursor.fetchall()

    print("Таблицы в PostgreSQL:")

    if tables:
        for schema, table in tables:
            print(f"{schema}.{table}")
    else:
        print("Таблиц в схеме public нет.")
