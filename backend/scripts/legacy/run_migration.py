
# Historical data-maintenance script. Review paths and back up data before use.
import os as _os
import sys as _sys
from pathlib import Path as _Path
if __name__ != "__main__" or _os.getenv("ALLOW_LEGACY_MAINTENANCE") != "1":
    raise SystemExit("Historical maintenance is disabled; review paths and back up data before setting ALLOW_LEGACY_MAINTENANCE=1")
_backend = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_backend))
from dotenv import load_dotenv as _load_dotenv
_load_dotenv(_backend / ".env")

import sqlite3
import os


def _column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns


def add_category_column(cursor):
    """添加category列到templates表"""
    if _column_exists(cursor, 'templates', 'category'):
        print("✓ category列已存在，无需迁移")
        return

    cursor.execute("ALTER TABLE templates ADD COLUMN category VARCHAR(50) DEFAULT 'other'")
    print("✓ 成功添加category列")
    cursor.execute("UPDATE templates SET category = 'other' WHERE category IS NULL")
    print(f"✓ 更新了 {cursor.rowcount} 条记录")


def add_user_profile_columns(cursor):
    """添加用户画像相关字段到users表"""
    columns_to_add = [
        ("nickname", "ALTER TABLE users ADD COLUMN nickname VARCHAR(80)"),
        ("avatar_url", "ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)"),
        ("teacher_gender", "ALTER TABLE users ADD COLUMN teacher_gender VARCHAR(20)"),
        ("teacher_age", "ALTER TABLE users ADD COLUMN teacher_age INTEGER"),
        ("school_name", "ALTER TABLE users ADD COLUMN school_name VARCHAR(200)"),
        ("subject_category", "ALTER TABLE users ADD COLUMN subject_category VARCHAR(100)"),
        ("courses", "ALTER TABLE users ADD COLUMN courses JSON"),
        ("teaching_styles", "ALTER TABLE users ADD COLUMN teaching_styles JSON"),
    ]

    for column_name, ddl in columns_to_add:
        if _column_exists(cursor, 'users', column_name):
            print(f"✓ users.{column_name} 已存在")
            continue
        cursor.execute(ddl)
        print(f"✓ 成功添加 users.{column_name}")


def add_template_extended_columns(cursor):
    """添加templates扩展字段（styles/template_info/source_format）"""
    columns_to_add = [
        ("source_format", "ALTER TABLE templates ADD COLUMN source_format VARCHAR(20) DEFAULT 'pptx'"),
        ("styles", "ALTER TABLE templates ADD COLUMN styles JSON"),
        ("template_info", "ALTER TABLE templates ADD COLUMN template_info JSON"),
    ]

    for column_name, ddl in columns_to_add:
        if _column_exists(cursor, 'templates', column_name):
            print(f"✓ templates.{column_name} 已存在")
            continue
        cursor.execute(ddl)
        print(f"✓ 成功添加 templates.{column_name}")


if __name__ == "__main__":
    print("=" * 60)
    print("执行数据库迁移")
    print("=" * 60)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'instance', 'guowaibao.db')

    print(f"数据库路径: {db_path}")

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            add_category_column(cursor)
            add_user_profile_columns(cursor)
            add_template_extended_columns(cursor)
            conn.commit()
            print("✓ 数据库迁移完成")
        except Exception as e:
            conn.rollback()
            print(f"✗ 迁移失败: {e}")
        finally:
            conn.close()

    print("=" * 60)
