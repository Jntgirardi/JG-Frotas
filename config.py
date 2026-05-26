import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rotas_secret_key_super_segura'
    
    # Configuração do Banco de Dados
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_DIR = os.path.join(BASE_DIR, 'database')
    
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Só cria a pasta do banco se realmente for usar SQLite local
        if not os.path.exists(DB_DIR):
            try:
                os.makedirs(DB_DIR)
            except Exception:
                pass
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DB_DIR, 'frota.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


