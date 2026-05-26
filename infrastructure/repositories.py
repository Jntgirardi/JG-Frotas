from domain.entities import Usuario, Caminhao, Viagem, Manutencao
from infrastructure.db import db
from infrastructure.models import UsuarioModel, CaminhaoModel, ViagemModel, ManutencaoModel

# ==========================================
# MAPEAR MODELOS DE BANCO PARA ENTIDADES DOMÍNIO
# ==========================================

def _to_domain_usuario(model) -> Usuario:
    if not model:
        return None
    return Usuario(
        id=model.id,
        username=model.username,
        password_hash=model.password_hash
    )

def _to_domain_caminhao(model) -> Caminhao:
    if not model:
        return None
    return Caminhao(
        id=model.id,
        placa=model.placa,
        modelo=model.modelo,
        ano=model.ano,
        cor=model.cor,
        status=model.status
    )

def _to_domain_viagem(model) -> Viagem:
    if not model:
        return None
    return Viagem(
        id=model.id,
        caminhao_id=model.caminhao_id,
        origem=model.origem,
        destino=model.destino,
        data=model.data,
        valor_frete=model.valor_frete,
        custo_combustivel=model.custo_combustivel,
        custo_pedagio=model.custo_pedagio,
        outros_custos=model.outros_custos,
        lucro_liquido=model.lucro_liquido,
        pago=model.pago,
        observacoes=model.observacoes,
        caminhao=_to_domain_caminhao(model.caminhao)  # Carrega objeto caminhão relacionado
    )

def _to_domain_manutencao(model) -> Manutencao:
    if not model:
        return None
    return Manutencao(
        id=model.id,
        caminhao_id=model.caminhao_id,
        descricao=model.descricao,
        custo=model.custo,
        data=model.data,
        tipo=model.tipo,
        oficina=model.oficina,
        caminhao=_to_domain_caminhao(model.caminhao)  # Carrega objeto caminhão relacionado
    )


# ==========================================
# IMPLEMENTAÇÕES DOS REPOSITÓRIOS
# ==========================================

class UsuarioRepository:
    def get_by_id(self, id) -> Usuario:
        model = UsuarioModel.query.get(id)
        return _to_domain_usuario(model)

    def get_by_username(self, username) -> Usuario:
        model = UsuarioModel.query.filter_by(username=username).first()
        return _to_domain_usuario(model)

    def count(self) -> int:
        return UsuarioModel.query.count()

    def save(self, entity: Usuario) -> Usuario:
        if entity.id:
            model = UsuarioModel.query.get(entity.id)
            model.username = entity.username
            model.password_hash = entity.password_hash
        else:
            model = UsuarioModel(
                username=entity.username,
                password_hash=entity.password_hash
            )
            db.session.add(model)
        
        db.session.commit()
        entity.id = model.id
        return entity


class CaminhaoRepository:
    def get_by_id(self, id) -> Caminhao:
        model = CaminhaoModel.query.get(id)
        return _to_domain_caminhao(model)

    def get_by_placa(self, placa) -> Caminhao:
        model = CaminhaoModel.query.filter_by(placa=placa.upper()).first()
        return _to_domain_caminhao(model)

    def get_all(self) -> list:
        models = CaminhaoModel.query.all()
        return [_to_domain_caminhao(m) for m in models]

    def save(self, entity: Caminhao) -> Caminhao:
        if entity.id:
            model = CaminhaoModel.query.get(entity.id)
            model.placa = entity.placa.upper()
            model.modelo = entity.modelo
            model.ano = entity.ano
            model.cor = entity.cor
            model.status = entity.status
        else:
            model = CaminhaoModel(
                placa=entity.placa.upper(),
                modelo=entity.modelo,
                ano=entity.ano,
                cor=entity.cor,
                status=entity.status
            )
            db.session.add(model)
            
        db.session.commit()
        entity.id = model.id
        return entity

    def delete(self, id) -> bool:
        model = CaminhaoModel.query.get(id)
        if model:
            db.session.delete(model)
            db.session.commit()
            return True
        return False


class ViagemRepository:
    def get_by_id(self, id) -> Viagem:
        model = ViagemModel.query.get(id)
        return _to_domain_viagem(model)

    def get_all_ordered_by_date(self) -> list:
        models = ViagemModel.query.order_by(ViagemModel.data.desc()).all()
        return [_to_domain_viagem(m) for m in models]

    def save(self, entity: Viagem) -> Viagem:
        entity.calcular_lucro()  # Garante cálculo de lucro antes de salvar
        
        if entity.id:
            model = ViagemModel.query.get(entity.id)
            model.caminhao_id = entity.caminhao_id
            model.origem = entity.origem
            model.destino = entity.destino
            model.data = entity.data
            model.valor_frete = entity.valor_frete
            model.custo_combustivel = entity.custo_combustivel
            model.custo_pedagio = entity.custo_pedagio
            model.outros_custos = entity.outros_custos
            model.lucro_liquido = entity.lucro_liquido
            model.pago = entity.pago
            model.observacoes = entity.observacoes
        else:
            model = ViagemModel(
                caminhao_id=entity.caminhao_id,
                origem=entity.origem,
                destino=entity.destino,
                data=entity.data,
                valor_frete=entity.valor_frete,
                custo_combustivel=entity.custo_combustivel,
                custo_pedagio=entity.custo_pedagio,
                outros_custos=entity.outros_custos,
                lucro_liquido=entity.lucro_liquido,
                pago=entity.pago,
                observacoes=entity.observacoes
            )
            db.session.add(model)
            
        db.session.commit()
        entity.id = model.id
        return entity

    def delete(self, id) -> bool:
        model = ViagemModel.query.get(id)
        if model:
            db.session.delete(model)
            db.session.commit()
            return True
        return False


class ManutencaoRepository:
    def get_by_id(self, id) -> Manutencao:
        model = ManutencaoModel.query.get(id)
        return _to_domain_manutencao(model)

    def get_all_ordered_by_date(self) -> list:
        models = ManutencaoModel.query.order_by(ManutencaoModel.data.desc()).all()
        return [_to_domain_manutencao(m) for m in models]

    def save(self, entity: Manutencao) -> Manutencao:
        if entity.id:
            model = ManutencaoModel.query.get(entity.id)
            model.caminhao_id = entity.caminhao_id
            model.descricao = entity.descricao
            model.custo = entity.custo
            model.data = entity.data
            model.tipo = entity.tipo
            model.oficina = entity.oficina
        else:
            model = ManutencaoModel(
                caminhao_id=entity.caminhao_id,
                descricao=entity.descricao,
                custo=entity.custo,
                data=entity.data,
                tipo=entity.tipo,
                oficina=entity.oficina
            )
            db.session.add(model)
            
        db.session.commit()
        entity.id = model.id
        return entity

    def delete(self, id) -> bool:
        model = ManutencaoModel.query.get(id)
        if model:
            db.session.delete(model)
            db.session.commit()
            return True
        return False
