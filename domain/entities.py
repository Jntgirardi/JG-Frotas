from datetime import date

class Usuario:
    def __init__(self, id=None, username=None, password_hash=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash


class Caminhao:
    def __init__(self, id=None, placa=None, modelo=None, ano=None, cor=None, status='Disponível', motorista='Não definido'):
        self.id = id
        self.placa = placa
        self.modelo = modelo
        self.ano = ano
        self.cor = cor
        self.status = status
        self.motorista = motorista


class Viagem:
    def __init__(self, id=None, caminhao_id=None, origem=None, destino=None, data=None, data_chegada=None,
                 valor_frete=0.0, custo_combustivel=0.0, custo_pedagio=0.0, outros_custos=0.0, 
                 comissao_motorista=0.0, prestacao=0.0, impostos=0.0,
                 lucro_liquido=0.0, pago=False, observacoes=None, caminhao=None):
        self.id = id
        self.caminhao_id = caminhao_id
        self.origem = origem
        self.destino = destino
        self.data = data or date.today()
        self.data_chegada = data_chegada or self.data
        self.valor_frete = valor_frete
        self.custo_combustivel = custo_combustivel
        self.custo_pedagio = custo_pedagio
        self.outros_custos = outros_custos
        self.comissao_motorista = comissao_motorista
        self.prestacao = prestacao
        self.impostos = impostos
        self.lucro_liquido = lucro_liquido
        self.pago = pago
        self.observacoes = observacoes
        
        # Objeto de domínio associado (opcional)
        self.caminhao = caminhao
        
        # Garante cálculo inicial correto
        self.calcular_lucro()

    def calcular_lucro(self):
        self.lucro_liquido = self.valor_frete - (
            self.custo_combustivel + self.custo_pedagio + self.outros_custos +
            self.comissao_motorista + self.prestacao + self.impostos
        )
        return self.lucro_liquido


class Manutencao:
    def __init__(self, id=None, caminhao_id=None, descricao=None, custo=0.0, data=None, 
                 tipo='Corretiva', oficina=None, caminhao=None):
        self.id = id
        self.caminhao_id = caminhao_id
        self.descricao = descricao
        self.custo = custo
        self.data = data or date.today()
        self.tipo = tipo
        self.oficina = oficina
        
        # Objeto de domínio associado (opcional)
        self.caminhao = caminhao
