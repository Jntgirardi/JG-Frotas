import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rotas_secret_key_super_segura'
    
    # Configuração do Banco de Dados SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_DIR = os.path.join(BASE_DIR, 'database')
    
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(DB_DIR, 'frota.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
