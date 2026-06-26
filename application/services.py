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

    def register_truck(self, placa, modelo, ano, cor, status='Disponível', motorista='Não definido') -> Caminhao:
        novo = Caminhao(placa=placa.upper(), modelo=modelo, ano=ano, cor=cor, status=status, motorista=motorista)
        return self.caminhao_repo.save(novo)

    def update_truck(self, id, placa, modelo, ano, cor, status, motorista='Não definido') -> Caminhao:
        caminhao = Caminhao(id=id, placa=placa.upper(), modelo=modelo, ano=ano, cor=cor, status=status, motorista=motorista)
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
                      comissao_motorista=0.0, prestacao=0.0, impostos=0.0,
                      pago=False, observacoes=None, data_chegada=None) -> Viagem:
        
        nova = Viagem(
            caminhao_id=caminhao_id,
            origem=origem,
            destino=destino,
            data=data,
            data_chegada=data_chegada,
            valor_frete=valor_frete,
            custo_combustivel=custo_combustivel,
            custo_pedagio=custo_pedagio,
            outros_custos=outros_custos,
            comissao_motorista=comissao_motorista,
            prestacao=prestacao,
            impostos=impostos,
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
                    comissao_motorista=0.0, prestacao=0.0, impostos=0.0,
                    pago=False, observacoes=None, data_chegada=None) -> Viagem:
        
        viagem = Viagem(
            id=id,
            caminhao_id=caminhao_id,
            origem=origem,
            destino=destino,
            data=data,
            data_chegada=data_chegada,
            valor_frete=valor_frete,
            custo_combustivel=custo_combustivel,
            custo_pedagio=custo_pedagio,
            outros_custos=outros_custos,
            comissao_motorista=comissao_motorista,
            prestacao=prestacao,
            impostos=impostos,
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
        total_custo_viagens = sum(
            v.custo_combustivel + v.custo_pedagio + v.outros_custos +
            v.comissao_motorista + v.prestacao + v.impostos for v in viagens
        )
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
            dados_mensais[mes_ano]['despesas'] += (
                v.custo_combustivel + v.custo_pedagio + v.outros_custos +
                v.comissao_motorista + v.prestacao + v.impostos
            )

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
        comissao_total = sum(v.comissao_motorista for v in viagens)
        prestacao_total = sum(v.prestacao for v in viagens)
        impostos_total = sum(v.impostos for v in viagens)
        manutencao_total = sum(m.custo for m in manutencoes)

        despesas_totais = (
            diesel_total + pedagio_total + outros_viagens_total + 
            comissao_total + prestacao_total + impostos_total + manutencao_total
        )
        saldo_geral = receitas_totais - despesas_totais

        # Lucratividade por caminhão
        analise_frota = []
        for c in caminhoes:
            viagens_c = [v for v in viagens if v.caminhao_id == c.id]
            manutencoes_c = [m for m in manutencoes if m.caminhao_id == c.id]

            receita_c = sum(v.valor_frete for v in viagens_c)
            custo_viagem_c = sum(
                v.custo_combustivel + v.custo_pedagio + v.outros_custos + 
                v.comissao_motorista + v.prestacao + v.impostos for v in viagens_c
            )
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
            'comissao_total': comissao_total,
            'prestacao_total': prestacao_total,
            'impostos_total': impostos_total,
            'manutencao_total': manutencao_total,
            'despesas_totais': despesas_totais,
            'saldo_geral': saldo_geral,
            'analise_frota': analise_frota
        }

    def get_truck_dashboard_data(self, caminhao_id, start_date=None, end_date=None) -> dict:
        caminhao = self.caminhao_repo.get_by_id(caminhao_id)
        if not caminhao:
            return None

        # Busca todas as viagens e manutenções do caminhão
        all_viagens = self.viagem_repo.get_all_ordered_by_date()
        all_manutencoes = self.manutencao_repo.get_all_ordered_by_date()

        viagens_c = [v for v in all_viagens if v.caminhao_id == caminhao_id]
        manutencoes_c = [m for m in all_manutencoes if m.caminhao_id == caminhao_id]

        # Calcula a lista de meses/anos únicos em que há registros para o dropdown
        meses_com_dados = set()
        # Garante que o mês atual esteja na lista
        meses_com_dados.add(datetime.today().date().replace(day=1))
        
        for v in all_viagens:
            if v.caminhao_id == caminhao_id:
                meses_com_dados.add(v.data.replace(day=1))
        for m in all_manutencoes:
            if m.caminhao_id == caminhao_id:
                meses_com_dados.add(m.data.replace(day=1))
                
        meses_lista = sorted(list(meses_com_dados), reverse=True)
        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        meses_formatados = []
        for dt in meses_lista:
            meses_formatados.append({
                'label': f"{meses_nomes[dt.month]} de {dt.year}",
                'mes': dt.month,
                'ano': dt.year
            })

        # Aplica filtros de data se fornecidos
        if start_date:
            viagens_c = [v for v in viagens_c if v.data >= start_date]
            manutencoes_c = [m for m in manutencoes_c if m.data >= start_date]
        if end_date:
            viagens_c = [v for v in viagens_c if v.data <= end_date]
            manutencoes_c = [m for m in manutencoes_c if m.data <= end_date]

        # Ordenação correta por data (mais recente primeiro)
        viagens_c.sort(key=lambda x: x.data, reverse=True)
        manutencoes_c.sort(key=lambda x: x.data, reverse=True)

        # Cálculos de fechamento para este caminhão no período
        faturamento_bruto = sum(v.valor_frete for v in viagens_c)
        despesa_combustivel = sum(v.custo_combustivel for v in viagens_c)
        despesa_pedagio = sum(v.custo_pedagio for v in viagens_c)
        despesa_comissao = sum(v.comissao_motorista for v in viagens_c)
        despesa_prestacao = sum(v.prestacao for v in viagens_c)
        despesa_impostos = sum(v.impostos for v in viagens_c)
        outros_custos = sum(v.outros_custos for v in viagens_c)
        despesa_manutencao = sum(m.custo for m in manutencoes_c)

        despesas_totais = (
            despesa_combustivel + despesa_pedagio + despesa_comissao +
            despesa_prestacao + despesa_impostos + outros_custos + despesa_manutencao
        )
        lucro_real = faturamento_bruto - despesas_totais

        return {
            'caminhao': caminhao,
            'viagens': viagens_c,
            'manutencoes': manutencoes_c,
            'faturamento_bruto': faturamento_bruto,
            'despesa_combustivel': despesa_combustivel,
            'despesa_pedagio': despesa_pedagio,
            'despesa_comissao': despesa_comissao,
            'despesa_prestacao': despesa_prestacao,
            'despesa_impostos': despesa_impostos,
            'outros_custos': outros_custos,
            'despesa_manutencao': despesa_manutencao,
            'despesas_totais': despesas_totais,
            'lucro_real': lucro_real,
            'meses_periodo': meses_formatados
        }
