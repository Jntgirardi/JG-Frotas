import unittest
import sys
import os

# Define a variável de ambiente de teste antes de importar o app
os.environ['TESTING'] = 'true'

# Garante que a raiz do projeto esteja no path do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from application.services import AuthService, FleetService, TripService, MaintenanceService
from datetime import date

class RotaFacilSecurityTestCase(unittest.TestCase):
    def setUp(self):
        # Configura o app para modo de testes e banco em memória
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test_secret_key'
        
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        self.client = app.test_client()
        self.auth_service = AuthService()
        self.fleet_service = FleetService()
        self.trip_service = TripService()
        self.maintenance_service = MaintenanceService()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_unauthenticated_redirects(self):
        """Verifica se rotas protegidas redirecionam usuários não autenticados para o Login"""
        protected_routes = [
            '/',
            '/caminhoes',
            '/manutencoes',
            '/financeiro',
            '/caminhao/1'
        ]
        
        # Inicializa um admin para garantir que o sistema não force cadastro inicial automático
        self.auth_service.register('jc_admin', 'jc_admin123')
        
        for route in protected_routes:
            with self.subTest(route=route):
                res = self.client.get(route)
                # Verifica se é um redirecionamento (302)
                self.assertEqual(res.status_code, 302)
                self.assertTrue(res.headers['Location'].endswith(('/login', '/cadastro_inicial')))

    def test_registration_lock(self):
        """Verifica se /cadastro_inicial é bloqueado após o primeiro registro"""
        # 1. Sem usuários: deve retornar 200 para cadastro_inicial
        res = self.client.get('/cadastro_inicial')
        self.assertEqual(res.status_code, 200)

        # 2. Registra o admin inicial
        self.auth_service.register('jc_admin', 'jc_admin123')

        # 3. Tenta acessar novamente: deve redirecionar para login
        res = self.client.get('/cadastro_inicial')
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.headers['Location'].endswith('/login'))

    def test_calculations_logic(self):
        """Valida se as regras de cálculo do lucro líquido da viagem funcionam perfeitamente"""
        # Registrar caminhão de teste
        truck = self.fleet_service.register_truck('BRA2E19', 'Volvo FH 540', 2021, 'Branco')
        
        # Registrar viagem
        trip = self.trip_service.register_trip(
            caminhao_id=truck.id,
            origem='SP',
            destino='RJ',
            data=date(2026, 6, 18),
            valor_frete=10000.0,
            custo_combustivel=3000.0,
            custo_pedagio=500.0,
            outros_custos=200.0,
            comissao_motorista=1200.0,
            prestacao=1000.0,
            impostos=1000.0,
            pago=True,
            observacoes='Teste de calculos'
        )
        
        # Lucro líquido esperado: 10000 - (3000 + 500 + 200 + 1200 + 1000 + 1000) = 3100
        self.assertEqual(trip.lucro_liquido, 3100.0)

    def test_duplicate_truck_plate_raises_error(self):
        """Valida que o sistema impede cadastrar placas de caminhões duplicadas"""
        self.fleet_service.register_truck('BRA2E19', 'Volvo FH 540', 2021, 'Branco')
        
        # Tentativa de registrar a mesma placa deve lançar exceção de integridade no commit
        from sqlalchemy.exc import IntegrityError
        with self.assertRaises(IntegrityError):
            try:
                self.fleet_service.register_truck('BRA2E19', 'Scania R 450', 2022, 'Vermelho')
            except Exception as e:
                db.session.rollback()
                raise e

    def test_invalid_truck_id_redirect(self):
        """Verifica se acessar um ID de caminhão inválido redireciona com segurança para o Dashboard"""
        # Simular login
        self.auth_service.register('jc_admin', 'jc_admin123')
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'jc_admin'
            
        res = self.client.get('/caminhao/99999')
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.headers['Location'].endswith('/'))

if __name__ == '__main__':
    unittest.main()
