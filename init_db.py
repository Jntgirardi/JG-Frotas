import os
from datetime import date
from app import app, db, auth_service, fleet_service, trip_service, maintenance_service

def init_database():
    print("Inicializando banco de dados no padrão Clean Architecture...")
    
    with app.app_context():
        # Remove se já existirem
        db.drop_all()
        # Cria todas as tabelas
        db.create_all()
        
        print("Tabelas físicas criadas com sucesso. Populando dados iniciais...")

        # 1. Cria usuário administrador inicial criptografado
        print("Criando usuário jonathas...")
        auth_service.register('jonathas', '1234')

        print("\n" + "="*50)
        print("Banco de dados populado com sucesso sob a ARQUITETURA LIMPA!")
        print("Perfil de teste inicial criado:")
        print("   - Usuário: jonathas")
        print("   - Senha:   1234")
        print("="*50)

if __name__ == '__main__':
    init_database()
