"""
查看並修復 favorites 表結構
"""
from app.models import db_session
from sqlalchemy import text

# 先查看表結構
result = db_session.execute(text("""
    SELECT column_name, is_nullable, column_default 
    FROM information_schema.columns 
    WHERE table_name = 'favorites'
    ORDER BY ordinal_position
"""))

print("=== favorites 表結構 ===")
columns = list(result)
for row in columns:
    print(f"  {row[0]}: nullable={row[1]}, default={row[2]}")

# 找出除了 id, user_id, house_id, created_at 以外的欄位
extra_cols = [c[0] for c in columns if c[0] not in ('id', 'user_id', 'house_id', 'created_at') and c[1] == 'NO']
print(f"\n需要修復的 NOT NULL 欄位: {extra_cols}")

# 修復
for col in extra_cols:
    try:
        db_session.execute(text(f'ALTER TABLE favorites ALTER COLUMN "{col}" DROP NOT NULL'))
        print(f"  ✓ 已修復 {col}")
    except Exception as e:
        print(f"  ✗ 修復 {col} 失敗: {e}")
        db_session.rollback()

db_session.commit()
print("\n完成！")
