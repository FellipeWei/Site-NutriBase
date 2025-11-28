from database import db
from flask_bcrypt import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    crn = db.Column(db.String(50), nullable=True)

    pacientes = db.relationship('Paciente', backref='responsavel', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha).decode('utf-8')

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
