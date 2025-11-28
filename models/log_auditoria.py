import datetime
from database import db

class LogAuditoria(db.Model):
    """
    Modelo para registrar todas as ações críticas (Criação/Exclusão/Atualização)
    feitas por um usuário no sistema.
    """
    __tablename__ = 'log_auditoria'
    
    id = db.Column(db.Integer, primary_key=True)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    acao = db.Column(db.String(50), nullable=False)
    recurso = db.Column(db.String(100), nullable=False)
    recurso_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<LogAuditoria {self.id}: {self.acao} em {self.recurso} por User {self.usuario_id}>'