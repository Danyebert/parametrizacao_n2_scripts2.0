"""Executa criação/ajustes de schema fora do cold start da Vercel."""
from app import create_app, db, ensure_schema_updates

app = create_app()

with app.app_context():
    db.create_all()
    if not str(db.engine.url).startswith("sqlite"):
        ensure_schema_updates()

print("Banco atualizado com sucesso.")
