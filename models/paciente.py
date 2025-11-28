from database import db
from datetime import date

class Paciente(db.Model):
    __tablename__ = 'paciente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.String(20))
    sexo = db.Column(db.String(10))
    contato = db.Column(db.String(120))
    objetivo = db.Column(db.String(200))
    historico = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    avaliacoes = db.relationship('Avaliacao', backref='paciente', lazy=True)
    
    
