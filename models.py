from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    email_corporativo = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    perfil = db.Column(db.String(20), default='Usuario') # Usuario, Tecnico, Gestor, Admin
    equipe = db.Column(db.String(50), nullable=True) # Elétrica, Hidráulica, etc.
    funcao = db.Column(db.String(20), default='Operacional') # Operacional, Lider
    
    chamados_abertos = db.relationship('Chamado', foreign_keys='Chamado.usuario_id', backref='solicitante', lazy=True)
    chamados_atendidos = db.relationship('Chamado', foreign_keys='Chamado.tecnico_lider_id', backref='tecnico_lider', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Setor(db.Model):
    __tablename__ = 'setores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    
    chamados = db.relationship('Chamado', backref='setor_local', lazy=True)


class Chamado(db.Model):
    __tablename__ = 'chamados'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    problema = db.Column(db.String(150), nullable=False)
    detalhes = db.Column(db.Text, nullable=True) # max 500 chars
    prioridade = db.Column(db.String(20), nullable=False) # BAIXA, MÉDIA, ALTA
    status = db.Column(db.String(30), default='ABERTO') # ABERTO, EQUIPE TÉCNICA ACIONADA, ATENDIMENTO INICIADO, CONCLUÍDO
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_acionamento = db.Column(db.DateTime, nullable=True)
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    tempo_estimado = db.Column(db.Float, nullable=True) # Em horas ou minutos previstos pelo ML
    
    tecnico_lider_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    equipe_responsavel = db.Column(db.String(50), nullable=True)
    
    avaliacoes = db.relationship('Avaliacao', backref='chamado_associado', lazy=True)
    logs = db.relationship('Logs_Chamado', backref='chamado_associado', lazy=True)


class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    nota = db.Column(db.Integer, nullable=False) # 1 a 5
    comentario = db.Column(db.Text, nullable=True)


class Logs_Chamado(db.Model):
    __tablename__ = 'logs_chamado'
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id'), nullable=False)
    status_anterior = db.Column(db.String(30), nullable=True)
    status_novo = db.Column(db.String(30), nullable=False)
    data_alteracao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_alteracao_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
