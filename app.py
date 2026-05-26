import os
from functools import wraps
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Importações de camadas da Arquitetura Limpa (Clean Architecture)
from config import Config
from infrastructure.db import db
from application.services import AuthService, FleetService, TripService, MaintenanceService, FinanceService

app = Flask(__name__)
app.config.from_object(Config)

# Inicializa o SQLAlchemy
db.init_app(app)

# Instanciação dos Serviços da Camada de Aplicação
auth_service = AuthService()
fleet_service = FleetService()
trip_service = TripService()
maintenance_service = MaintenanceService()
finance_service = FinanceService()

# ==========================================
# INTERCEPTOR DE SEGURANÇA (Decorador)
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Se não houver usuários cadastrados no sistema, força cadastro inicial
        if not auth_service.has_users():
            return redirect(url_for('cadastro_inicial'))
        
        # 2. Se o usuário não estiver com sessão ativa, redireciona para login
        if session.get('user_id') is None:
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# ROTAS DE AUTENTICAÇÃO (Sem proteção)
# ==========================================

@app.route('/cadastro_inicial', methods=['GET', 'POST'])
def cadastro_inicial():
    # Segurança: Se já existirem usuários no sistema, bloqueia acesso a esta tela
    if auth_service.has_users():
        flash('O administrador inicial já foi configurado!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')

        if not username or len(password) < 6:
            flash('Por favor, escolha um usuário válido e uma senha com pelo menos 6 caracteres.', 'warning')
            return redirect(url_for('cadastro_inicial'))

        # Registra o primeiro usuário administrador
        user = auth_service.register(username, password)
        
        # Inicia a sessão automaticamente
        session['user_id'] = user.id
        session['username'] = user.username
        
        flash('Perfil de administrador configurado com sucesso! Bem-vindo ao RotaFácil.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('cadastro_inicial.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redireciona para o cadastro se for o primeiro acesso absoluto
    if not auth_service.has_users():
        return redirect(url_for('cadastro_inicial'))

    # Se já estiver logado, vai direto para o painel
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')

        user = auth_service.authenticate(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Olá, {user.username}! Login realizado com sucesso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos! Tente novamente.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada com segurança!', 'success')
    return redirect(url_for('login'))


# ==========================================
# ROTAS PROTEGIDAS (Apenas usuários logados)
# ==========================================

@app.route('/')
@login_required
def dashboard():
    # Busca todas as informações sintetizadas pelo serviço financeiro
    data = finance_service.get_dashboard_data()
    return render_template(
        'dashboard.html',
        **data,
        data_hoje=date.today().isoformat()
    )


# ----------------- CAMINHÕES -----------------

@app.route('/caminhoes', methods=['GET', 'POST'])
@login_required
def caminhoes():
    if request.method == 'POST':
        placa = request.form.get('placa').strip().upper()
        modelo = request.form.get('modelo').strip()
        ano = int(request.form.get('ano', datetime.now().year))
        cor = request.form.get('cor').strip()
        status = request.form.get('status', 'Disponível')

        if not placa or not modelo:
            flash('Por favor, preencha placa e modelo.', 'warning')
            return redirect(url_for('caminhoes'))

        # Valida se placa já existe
        existente = fleet_service.get_truck_by_placa(placa)
        if existente:
            flash(f'O caminhão placa {placa} já está cadastrado!', 'danger')
            return redirect(url_for('caminhoes'))

        fleet_service.register_truck(placa, modelo, ano, cor, status)
        flash('Caminhão cadastrado com sucesso!', 'success')
        return redirect(url_for('caminhoes'))

    caminhoes_lista = fleet_service.list_trucks()
    return render_template('caminhoes.html', caminhoes=caminhoes_lista)


@app.route('/caminhoes/editar/<int:id>', methods=['POST'])
@login_required
def editar_caminhao(id):
    placa = request.form.get('placa').strip().upper()
    modelo = request.form.get('modelo').strip()
    ano = int(request.form.get('ano'))
    cor = request.form.get('cor').strip()
    status = request.form.get('status')

    fleet_service.update_truck(id, placa, modelo, ano, cor, status)
    flash('Caminhão atualizado com sucesso!', 'success')
    return redirect(url_for('caminhoes'))


@app.route('/caminhoes/deletar/<int:id>')
@login_required
def deletar_caminhao(id):
    caminhao = fleet_service.get_truck_by_id(id)
    if caminhao:
        placa = caminhao.placa
        fleet_service.remove_truck(id)
        flash(f'Caminhão {placa} excluído com sucesso!', 'success')
    return redirect(url_for('caminhoes'))


# ----------------- VIAGENS -----------------

@app.route('/viagens', methods=['GET', 'POST'])
@login_required
def viagens():
    if request.method == 'POST':
        caminhao_id = int(request.form.get('caminhao_id'))
        origem = request.form.get('origem').strip()
        destino = request.form.get('destino').strip()
        data_str = request.form.get('data')
        valor_frete = float(request.form.get('valor_frete', 0.0) or 0)
        custo_combustivel = float(request.form.get('custo_combustivel', 0.0) or 0)
        custo_pedagio = float(request.form.get('custo_pedagio', 0.0) or 0)
        outros_custos = float(request.form.get('outros_custos', 0.0) or 0)
        pago = request.form.get('pago') == 'True'
        observacoes = request.form.get('observacoes').strip()

        data_viagem = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else date.today()

        trip_service.register_trip(
            caminhao_id=caminhao_id,
            origem=origem,
            destino=destino,
            data=data_viagem,
            valor_frete=valor_frete,
            custo_combustivel=custo_combustivel,
            custo_pedagio=custo_pedagio,
            outros_custos=outros_custos,
            pago=pago,
            observacoes=observacoes
        )
        flash('Viagem registrada com sucesso!', 'success')
        return redirect(url_for('viagens'))

    viagens_lista = trip_service.list_trips()
    caminhoes_lista = fleet_service.list_trucks()
    return render_template(
        'viagens.html',
        viagens=viagens_lista,
        caminhoes=caminhoes_lista
    )


@app.route('/viagens/editar/<int:id>', methods=['POST'])
@login_required
def editar_viagem(id):
    caminhao_id = int(request.form.get('caminhao_id'))
    origem = request.form.get('origem').strip()
    destino = request.form.get('destino').strip()
    data_str = request.form.get('data')
    valor_frete = float(request.form.get('valor_frete', 0.0) or 0)
    custo_combustivel = float(request.form.get('custo_combustivel', 0.0) or 0)
    custo_pedagio = float(request.form.get('custo_pedagio', 0.0) or 0)
    outros_custos = float(request.form.get('outros_custos', 0.0) or 0)
    pago = request.form.get('pago') == 'True'
    observacoes = request.form.get('observacoes').strip()

    data_viagem = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else date.today()

    trip_service.update_trip(
        id=id,
        caminhao_id=caminhao_id,
        origem=origem,
        destino=destino,
        data=data_viagem,
        valor_frete=valor_frete,
        custo_combustivel=custo_combustivel,
        custo_pedagio=custo_pedagio,
        outros_custos=outros_custos,
        pago=pago,
        observacoes=observacoes
    )
    flash('Registro de viagem atualizado!', 'success')
    return redirect(url_for('viagens'))


@app.route('/viagens/pago/<int:id>')
@login_required
def alternar_pago_viagem(id):
    viagem = trip_service.toggle_paid(id)
    status_str = "recebida" if viagem.pago else "marcada como pendente"
    flash(f'A viagem para {viagem.destino} foi {status_str}!', 'success')
    return redirect(request.referrer or url_for('viagens'))


@app.route('/viagens/deletar/<int:id>')
@login_required
def deletar_viagem(id):
    trip_service.remove_trip(id)
    flash('Registro de viagem removido com sucesso!', 'success')
    return redirect(url_for('viagens'))


# ----------------- MANUTENÇÃO -----------------

@app.route('/manutencoes', methods=['GET', 'POST'])
@login_required
def manutencoes():
    if request.method == 'POST':
        caminhao_id = int(request.form.get('caminhao_id'))
        descricao = request.form.get('descricao').strip()
        custo = float(request.form.get('custo', 0.0) or 0)
        data_str = request.form.get('data')
        tipo = request.form.get('tipo', 'Corretiva')
        oficina = request.form.get('oficina').strip()

        data_servico = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else date.today()

        maintenance_service.register_maintenance(
            caminhao_id=caminhao_id,
            descricao=descricao,
            custo=custo,
            data=data_servico,
            tipo=tipo,
            oficina=oficina
        )
        flash('Manutenção registrada com sucesso!', 'success')
        return redirect(url_for('manutencoes'))

    manutencoes_lista = maintenance_service.list_maintenances()
    caminhoes_lista = fleet_service.list_trucks()
    return render_template(
        'manutencoes.html',
        manutencoes=manutencoes_lista,
        caminhoes=caminhoes_lista
    )


@app.route('/manutencoes/editar/<int:id>', methods=['POST'])
@login_required
def editar_manutencao(id):
    caminhao_id = int(request.form.get('caminhao_id'))
    descricao = request.form.get('descricao').strip()
    custo = float(request.form.get('custo', 0.0) or 0)
    data_str = request.form.get('data')
    tipo = request.form.get('tipo')
    oficina = request.form.get('oficina').strip()

    data_servico = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else date.today()

    maintenance_service.update_maintenance(
        id=id,
        caminhao_id=caminhao_id,
        descricao=descricao,
        custo=custo,
        data=data_servico,
        tipo=tipo,
        oficina=oficina
    )
    flash('Registro de manutenção atualizado!', 'success')
    return redirect(url_for('manutencoes'))


@app.route('/manutencoes/deletar/<int:id>')
@login_required
def deletar_manutencao(id):
    maintenance_service.remove_maintenance(id)
    flash('Registro de manutenção removido!', 'success')
    return redirect(url_for('manutencoes'))


# ----------------- FINANCEIRO -----------------

@app.route('/financeiro')
@login_required
def financeiro():
    relatorio = finance_service.get_financial_report_data()
    return render_template('financeiro.html', **relatorio)


# ----------------- RESET / INICIALIZAR DADOS -----------------

@app.route('/inicializar_dados')
def inicializar_dados():
    # Remove e recria as tabelas físicas do banco SQLite
    db.drop_all()
    db.create_all()

    # 1. Cria usuário padrão admin/admin123 criptografado para o primeiro acesso
    auth_service.register('admin', 'admin123')

    # 2. Cria 3 caminhões de teste
    c1 = fleet_service.register_truck('BRA2E19', 'Volvo FH 540 Globetrotter', 2021, 'Branco', 'Em Viagem')
    c2 = fleet_service.register_truck('BRA3F22', 'Scania R 450 Highline', 2022, 'Vermelho', 'Disponível')
    c3 = fleet_service.register_truck('BRA4G25', 'Mercedes-Benz Actros 2651', 2020, 'Azul Escuro', 'Em Manutenção')

    # 3. Cria viagens de teste
    v1 = trip_service.register_trip(
        caminhao_id=c1.id,
        origem='São Paulo - SP',
        destino='Rio de Janeiro - RJ',
        data=date(2026, 3, 15),
        valor_frete=3800.00,
        custo_combustivel=1400.00,
        custo_pedagio=350.00,
        outros_custos=150.00,
        pago=True,
        observacoes='Carga de bobinas de papel. Tudo OK.'
    )
    v2 = trip_service.register_trip(
        caminhao_id=c2.id,
        origem='Curitiba - PR',
        destino='Porto Alegre - RS',
        data=date(2026, 4, 10),
        valor_frete=4500.00,
        custo_combustivel=1700.00,
        custo_pedagio=280.00,
        outros_custos=100.00,
        pago=True,
        observacoes='Carga seca, grãos. Frete rápido.'
    )
    v3 = trip_service.register_trip(
        caminhao_id=c1.id,
        origem='Belo Horizonte - MG',
        destino='Vitória - ES',
        data=date(2026, 5, 2),
        valor_frete=5200.00,
        custo_combustivel=2100.00,
        custo_pedagio=420.00,
        outros_custos=200.00,
        pago=True,
        observacoes='Minério de ferro. Pedágios caros.'
    )
    v4 = trip_service.register_trip(
        caminhao_id=c2.id,
        origem='São Paulo - SP',
        destino='Campinas - SP',
        data=date(2026, 5, 20),
        valor_frete=1800.00,
        custo_combustivel=550.00,
        custo_pedagio=120.00,
        outros_custos=50.00,
        pago=False,
        observacoes='Carga fracionada expressa. Aguardando liberação.'
    )

    # 4. Cria manutenções de teste
    maintenance_service.register_maintenance(
        caminhao_id=c3.id,
        descricao='Troca preventiva de óleo de motor e filtros',
        custo=850.00,
        data=date(2026, 4, 5),
        tipo='Preventiva',
        oficina='Mecânica Diesel Express'
    )
    maintenance_service.register_maintenance(
        caminhao_id=c3.id,
        descricao='Retífica do sistema de freios (lonas e tambores novos)',
        custo=2400.00,
        data=date(2026, 5, 25),
        tipo='Corretiva',
        oficina='Freios Paranaense'
    )

    flash('Banco de dados reconfigurado! Perfil criado: Usuário: admin | Senha: admin123', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas se ainda não existirem
        db.create_all()
        
    app.run(debug=True, host='0.0.0.0', port=5000)
