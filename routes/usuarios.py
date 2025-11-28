from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database import db
from models.usuario import Usuario
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')
bcrypt = Bcrypt()

# PAGINAS WEB
@usuarios_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@usuarios_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@usuarios_bp.route('/register', methods=['POST'])
def register():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    crn = request.form.get('crn')

    if Usuario.query.filter_by(email=email).first():
        flash('E-mail já cadastrado.', 'danger')
        return redirect(url_for('usuarios.register_page'))

    usuario = Usuario(nome=nome, email=email, crn=crn)
    usuario.set_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    flash('Cadastro realizado. Faça login.', 'success')
    return redirect(url_for('usuarios.login_page'))

@usuarios_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.verificar_senha(senha):
        flash('Credenciais inválidas.', 'danger')
        return redirect(url_for('usuarios.login_page'))

    session['user_id'] = usuario.id
    session['user_name'] = usuario.nome
    flash('Bem-vindo, ' + usuario.nome, 'success')
    return redirect(url_for('usuarios.dashboard'))

@usuarios_bp.route('/logout')
def logout():
    session.clear()
    flash('Desconectado.', 'info')
    return redirect(url_for('usuarios.login_page'))

def login_required_web(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('usuarios.login_page'))
        return f(*args, **kwargs)
    return decorated

@usuarios_bp.route('/dashboard')
@login_required_web
def dashboard():
    # PAGINA PRINCIPAL
    from models.paciente import Paciente
    user_id = session.get('user_id')
    total = Paciente.query.filter_by(usuario_id=user_id).count()
    return render_template('dashboard.html', total_pacientes=total)

# ENDPOINTS API
@usuarios_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    crn = data.get('crn')

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"msg": "email_exists"}), 400

    usuario = Usuario(nome=nome, email=email, crn=crn)
    usuario.set_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    return jsonify({"msg": "usuario_criado"}), 201

@usuarios_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.verificar_senha(senha):
        return jsonify({"msg": "credenciais_invalidas"}), 401

    access_token = create_access_token(identity=usuario.id, expires_delta=timedelta(hours=12))
    return jsonify(access_token=access_token)
