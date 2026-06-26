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
        print("Criando usuário jc_admin...")
        auth_service.register('jc_admin', 'jc_admin123')

        # 2. Cria 3 Caminhões de Exemplo (Frota inicial)
        print("Criando caminhões...")
        c1 = fleet_service.register_truck('BRA2E19', 'Volvo FH 540 Globetrotter', 2021, 'Branco', 'Em Viagem', motorista='Carlos Souza')
        c2 = fleet_service.register_truck('BRA3F22', 'Scania R 450 Highline', 2022, 'Vermelho', 'Disponível', motorista='José Santos')
        c3 = fleet_service.register_truck('BRA4G25', 'Mercedes-Benz Actros 2651', 2020, 'Azul Escuro', 'Em Manutenção', motorista='Antônio Lima')

        # 3. Cria Viagens de Exemplo (últimos 3 meses)
        print("Criando viagens...")
        v1 = trip_service.register_trip(
            caminhao_id=c1.id,
            origem='São Paulo - SP',
            destino='Rio de Janeiro - RJ',
            data=date(2026, 3, 15),
            data_chegada=date(2026, 3, 16),
            valor_frete=3800.00,
            custo_combustivel=1400.00,
            custo_pedagio=350.00,
            outros_custos=150.00,
            comissao_motorista=300.00,
            prestacao=500.00,
            impostos=120.00,
            pago=True,
            observacoes='Carga de bobinas de papel. Tudo OK.'
        )
        v2 = trip_service.register_trip(
            caminhao_id=c2.id,
            origem='Curitiba - PR',
            destino='Porto Alegre - RS',
            data=date(2026, 4, 10),
            data_chegada=date(2026, 4, 11),
            valor_frete=4500.00,
            custo_combustivel=1700.00,
            custo_pedagio=280.00,
            outros_custos=100.00,
            comissao_motorista=350.00,
            prestacao=500.00,
            impostos=150.00,
            pago=True,
            observacoes='Carga seca, grãos. Frete rápido.'
        )
        v3 = trip_service.register_trip(
            caminhao_id=c1.id,
            origem='Belo Horizonte - MG',
            destino='Vitória - ES',
            data=date(2026, 5, 2),
            data_chegada=date(2026, 5, 3),
            valor_frete=5200.00,
            custo_combustivel=2100.00,
            custo_pedagio=420.00,
            outros_custos=200.00,
            comissao_motorista=400.00,
            prestacao=500.00,
            impostos=200.00,
            pago=True,
            observacoes='Minério de ferro. Pedágios caros.'
        )
        v4 = trip_service.register_trip(
            caminhao_id=c2.id,
            origem='São Paulo - SP',
            destino='Campinas - SP',
            data=date(2026, 5, 20),
            data_chegada=date(2026, 5, 20),
            valor_frete=1800.00,
            custo_combustivel=550.00,
            custo_pedagio=120.00,
            outros_custos=50.00,
            comissao_motorista=150.00,
            prestacao=300.00,
            impostos=80.00,
            pago=False,
            observacoes='Carga fracionada expressa. Aguardando liberação do faturamento.'
        )

        # 4. Cria Manutenções de Exemplo
        print("Criando manutenções...")
        m1 = maintenance_service.register_maintenance(
            caminhao_id=c3.id,
            descricao='Troca preventiva de óleo de motor e filtros',
            custo=850.00,
            data=date(2026, 4, 5),
            tipo='Preventiva',
            oficina='Mecânica Diesel Express'
        )
        
        m2 = maintenance_service.register_maintenance(
            caminhao_id=c3.id,
            descricao='Retífica do sistema de freios (lonas e tambores novos)',
            custo=2400.00,
            data=date(2026, 5, 25),
            tipo='Corretiva',
            oficina='Freios Paranaense'
        )

        print("\n" + "="*50)
        print("Banco de dados populado com sucesso sob a ARQUITETURA LIMPA!")
        print("Perfil de teste inicial criado:")
        print("   - Usuário: jc_admin")
        print("   - Senha:   jc_admin123")
        print("="*50)

if __name__ == '__main__':
    init_database()
