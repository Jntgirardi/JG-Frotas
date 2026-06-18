from datetime import datetime
from infrastructure.db import db

class UsuarioModel(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<UsuarioModel {self.username}>"


class CaminhaoModel(db.Model):
    __tablename__ = 'caminhoes'
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    cor = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default='Disponível')
    motorista = db.Column(db.String(100), nullable=True, default='Não definido')

    # Relacionamentos com cascade para integridade referencial
    viagens = db.relationship('ViagemModel', backref='caminhao', lazy=True, cascade="all, delete-orphan")
    manutencoes = db.relationship('ManutencaoModel', backref='caminhao', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CaminhaoModel {self.placa}>"


class ViagemModel(db.Model):
    __tablename__ = 'viagens'
    id = db.Column(db.Integer, primary_key=True)
    caminhao_id = db.Column(db.Integer, db.ForeignKey('caminhoes.id'), nullable=False)
    origem = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    valor_frete = db.Column(db.Float, nullable=False, default=0.0)
    custo_combustivel = db.Column(db.Float, nullable=False, default=0.0)
    custo_pedagio = db.Column(db.Float, nullable=False, default=0.0)
    outros_custos = db.Column(db.Float, nullable=False, default=0.0)
    comissao_motorista = db.Column(db.Float, nullable=False, default=0.0)
    prestacao = db.Column(db.Float, nullable=False, default=0.0)
    impostos = db.Column(db.Float, nullable=False, default=0.0)
    lucro_liquido = db.Column(db.Float, nullable=False, default=0.0)
    pago = db.Column(db.Boolean, default=False)
    observacoes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<ViagemModel {self.origem} -> {self.destino}>"


class ManutencaoModel(db.Model):
    __tablename__ = 'manutencoes'
    id = db.Column(db.Integer, primary_key=True)
    caminhao_id = db.Column(db.Integer, db.ForeignKey('caminhoes.id'), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    custo = db.Column(db.Float, nullable=False, default=0.0)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    tipo = db.Column(db.String(50), default='Corretiva')
    oficina = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return f"<ManutencaoModel {self.descricao}>"
