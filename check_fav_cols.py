from app.models import db_session
from sqlalchemy import inspect

inspector = inspect(db_session.get_bind())
cols = inspector.get_columns('favorites')
print('Favorites DB columns:')
for c in cols:
    print(f"  {c['name']}: nullable={c['nullable']}, default={c.get('default')}")
