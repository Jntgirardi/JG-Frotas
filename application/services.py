from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from domain.entities import Usuario, Caminhao, Viagem, Manutencao
from infrastructure.repositories import (
    UsuarioRepository, CaminhaoRepository, ViagemRepository, ManutencaoRepository
)

# ==========================================
# SERVIÇO DE AUTENTICAÇÃO E PERFIL (AuthService)
# ==========================================

class AuthService:
    def __init__(self):
        self.user_repo = UsuarioRepository()

    def has_users(self) -> bool:
        return self.user_repo.count() > 0

    def register(self, username, password) -> Usuario:
        # Criptografa a senha antes de salvar
        password_hash = generate_password_hash(password)
        novo_usuario = Usuario(username=username, password_hash=password_hash)
        return self.user_repo.save(novo_usuario)

    def authenticate(self, username, password) -> Usuario:
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        
        # Verifica se a senha criptografada bate
        if check_password_hash(user.password_hash, password):
            return user
        return None

    def get_user_by_id(self, id) -> Usuario:
        return self.user_repo.get_by_id(id)


# ==========================================
# SERVIÇO DE FROTA (FleetService)
# ==========================================

class FleetService:
    def __init__(self):
        self.caminhao_repo = CaminhaoRepository()

    def list_trucks(self) -> list:
        return self.caminhao_repo.get_all()

    def get_truck_by_id(self, id) -> Caminhao:
        return self.caminhao_repo.get_by_id(id)

    def get_truck_by_placa(self, placa) -> Caminhao:
        return self.caminhao_repo.get_by_placa(placa)

    def register_truck(self, placa, modelo, ano, cor, status='Disponível') -> Caminhao:
        novo = Caminhao(placa=placa.upper(), modelo=modelo, ano=ano, cor=cor, status=status)
        return self.caminhao_repo.save(novo)

    def update_truck(self, id, placa, modelo, ano, cor, status) -> Caminhao:
        caminhao = Caminhao(id=id, placa=placa.upper(), modelo=modelo, ano=ano, cor=cor, status=status)
        return self.caminhao_repo.save(caminhao)

    def remove_truck(self, id) -> bool:
        return self.caminhao_repo.delete(id)


# ==========================================
# SERVIÇO DE VIAGENS (TripService)
# ==========================================

class TripService:
    def __init__(self):
        self.viagem_repo = ViagemRepository()
        self.caminhao_repo = CaminhaoRepository()

    def list_trips(self) -> list:
        return self.viagem_repo.get_all_ordered_by_date()

    def get_trip_by_id(self, id) -> Viagem:
        return self.viagem_repo.get_by_id(id)

    def register_trip(self, caminhao_id, origem, destino, data, valor_frete, 
                      custo_combustivel=0.0, custo_pedagio=0.0, outros_custos=0.0, 
                      pago=False, observacoes=None) -> Viagem:
        
        nova = Viagem(
            caminhao_id=caminhao_id,
            origem=origem,
            destino=destino,
            data=data,
            valor_frete=valor_frete,
            custo_combustivel=custo_combustivel,
            custo_pedagio=custo_pedagio,
            outros_custos=outros_custos,
            pago=pago,
            observacoes=observacoes
        )
        viagem_salva = self.viagem_repo.save(nova)
        
        # Regra de negócio: Coloca caminhão em viagem se estivesse "Disponível"
        caminhao = self.caminhao_repo.get_by_id(caminhao_id)
        if caminhao and caminhao.status == 'Disponível':
            caminhao.status = 'Em Viagem'
            self.caminhao_repo.save(caminhao)
            
        return viagem_salva

    def update_trip(self, id, caminhao_id, origem, destino, data, valor_frete, 
                    custo_combustivel=0.0, custo_pedagio=0.0, outros_custos=0.0, 
                    pago=False, observacoes=None) -> Viagem:
        
        viagem = Viagem(
            id=id,
            caminhao_id=caminhao_id,
            origem=origem,
            destino=destino,
            data=data,
            valor_frete=valor_frete,
            custo_combustivel=custo_combustivel,
            custo_pedagio=custo_pedagio,
            outros_custos=outros_custos,
            pago=pago,
            observacoes=observacoes
        )
        return self.viagem_repo.save(viagem)

    def toggle_paid(self, id) -> Viagem:
        viagem = self.viagem_repo.get_by_id(id)
        if viagem:
            viagem.pago = not viagem.pago
            self.viagem_repo.save(viagem)
        return viagem

    def remove_trip(self, id) -> bool:
        return self.viagem_repo.delete(id)


# ==========================================
# SERVIÇO DE MANUTENÇÃO (MaintenanceService)
# ==========================================

class MaintenanceService:
    def __init__(self):
        self.manutencao_repo = ManutencaoRepository()
        self.caminhao_repo = CaminhaoRepository()

    def list_maintenances(self) -> list:
        return self.manutencao_repo.get_all_ordered_by_date()

    def get_maintenance_by_id(self, id) -> Manutencao:
        return self.manutencao_repo.get_by_id(id)

    def register_maintenance(self, caminhao_id, descricao, custo, data, 
                             tipo='Corretiva', oficina=None) -> Manutencao:
        
        nova = Manutencao(
            caminhao_id=caminhao_id,
            descricao=descricao,
            custo=custo,
            data=data,
            tipo=tipo,
            oficina=oficina
        )
        manutencao_salva = self.manutencao_repo.save(nova)
        
        # Regra de negócio: Coloca caminhão em manutenção automaticamente
        caminhao = self.caminhao_repo.get_by_id(caminhao_id)
        if caminhao:
            caminhao.status = 'Em Manutenção'
            self.caminhao_repo.save(caminhao)
            
        return manutencao_salva

    def update_maintenance(self, id, caminhao_id, descricao, custo, data, 
                           tipo='Corretiva', oficina=None) -> Manutencao:
        
        manutencao = Manutencao(
            id=id,
            caminhao_id=caminhao_id,
            descricao=descricao,
            custo=custo,
            data=data,
            tipo=tipo,
            oficina=oficina
        )
        return self.manutencao_repo.save(manutencao)

    def remove_maintenance(self, id) -> bool:
        return self.manutencao_repo.delete(id)


# ==========================================
# SERVIÇO FINANCEIRO E DE INTELIGÊNCIA (FinanceService)
# ==========================================

class FinanceService:
    def __init__(self):
        self.caminhao_repo = CaminhaoRepository()
        self.viagem_repo = ViagemRepository()
        self.manutencao_repo = ManutencaoRepository()

    def get_dashboard_data(self) -> dict:
        caminhoes = self.caminhao_repo.get_all()
        viagens = self.viagem_repo.get_all_ordered_by_date()
        manutencoes = self.manutencao_repo.get_all_ordered_by_date()

        # Totais consolidados
        total_frete = sum(v.valor_frete for v in viagens)
        total_custo_viagens = sum(v.custo_combustivel + v.custo_pedagio + v.outros_custos for v in viagens)
        total_manutencao = sum(m.custo for m in manutencoes)
        
        total_despesas = total_custo_viagens + total_manutencao
        lucro_real = total_frete - total_despesas

        # Contagem de status dos caminhões
        status_contagem = {'Disponível': 0, 'Em Viagem': 0, 'Em Manutenção': 0}
        for c in caminhoes:
            if c.status in status_contagem:
                status_contagem[c.status] += 1

        # Dados mensais para os gráficos
        dados_mensais = {}
        for v in viagens:
            mes_ano = v.data.strftime('%m/%Y')
            if mes_ano not in dados_mensais:
                dados_mensais[mes_ano] = {'receitas': 0.0, 'despesas': 0.0}
            dados_mensais[mes_ano]['receitas'] += v.valor_frete
            dados_mensais[mes_ano]['despesas'] += (v.custo_combustivel + v.custo_pedagio + v.outros_custos)

        for m in manutencoes:
            mes_ano = m.data.strftime('%m/%Y')
            if mes_ano not in dados_mensais:
                dados_mensais[mes_ano] = {'receitas': 0.0, 'despesas': 0.0}
            dados_mensais[mes_ano]['despesas'] += m.custo

        meses_ordenados = sorted(dados_mensais.keys(), key=lambda x: datetime.strptime(x, '%m/%Y'))
        labels_grafico = meses_ordenados[-6:]  # Últimos 6 meses
        receitas_grafico = [dados_mensais[m]['receitas'] for m in labels_grafico]
        despesas_grafico = [dados_mensais[m]['despesas'] for m in labels_grafico]
        lucros_grafico = [receitas_grafico[i] - despesas_grafico[i] for i in range(len(labels_grafico))]

        return {
            'total_caminhoes': len(caminhoes),
            'status_contagem': status_contagem,
            'total_frete': total_frete,
            'total_despesas': total_despesas,
            'lucro_real': lucro_real,
            'ultimas_viagens': viagens[:5],
            'ultimas_manutencoes': manutencoes[:5],
            'labels_grafico': labels_grafico,
            'receitas_grafico': receitas_grafico,
            'despesas_grafico': despesas_grafico,
            'lucros_grafico': lucros_grafico,
            'caminhoes': caminhoes
        }

    def get_financial_report_data(self) -> dict:
        caminhoes = self.caminhao_repo.get_all()
        viagens = self.viagem_repo.get_all_ordered_by_date()
        manutencoes = self.manutencao_repo.get_all_ordered_by_date()

        # Detalhamento de custos
        receitas_totais = sum(v.valor_frete for v in viagens)
        diesel_total = sum(v.custo_combustivel for v in viagens)
        pedagio_total = sum(v.custo_pedagio for v in viagens)
        outros_viagens_total = sum(v.outros_custos for v in viagens)
        manutencao_total = sum(m.custo for m in manutencoes)

        despesas_totais = diesel_total + pedagio_total + outros_viagens_total + manutencao_total
        saldo_geral = receitas_totais - despesas_totais

        # Lucratividade por caminhão
        analise_frota = []
        for c in caminhoes:
            viagens_c = [v for v in viagens if v.caminhao_id == c.id]
            manutencoes_c = [m for m in manutencoes if m.caminhao_id == c.id]

            receita_c = sum(v.valor_frete for v in viagens_c)
            custo_viagem_c = sum(v.custo_combustivel + v.custo_pedagio + v.outros_custos for v in viagens_c)
            manutencao_c = sum(m.custo for m in manutencoes_c)
            
            despesa_total_c = custo_viagem_c + manutencao_c
            saldo_c = receita_c - despesa_total_c

            analise_frota.append({
                'caminhao': c,
                'viagens_qtd': len(viagens_c),
                'receita': receita_c,
                'despesa': despesa_total_c,
                'saldo': saldo_c
            })

        return {
            'receitas_totais': receitas_totais,
            'diesel_total': diesel_total,
            'pedagio_total': pedagio_total,
            'outros_viagens_total': outros_viagens_total,
            'manutencao_total': manutencao_total,
            'despesas_totais': despesas_totais,
            'saldo_geral': saldo_geral,
            'analise_frota': analise_frota
        }
