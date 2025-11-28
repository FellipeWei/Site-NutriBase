import os
from flask import Flask, request, session, redirect, url_for, render_template, g, make_response, current_app
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from database import db
from models.log_auditoria import LogAuditoria # 🔑 NOVO: Importar o modelo de Log
from routes.usuarios import usuarios_bp
from routes.pacientes import pacientes_bp
from routes.avaliacoes import avaliacoes_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'troque-essa-chave-para-producao' # para sessão web
    app.config['JWT_SECRET_KEY'] = 'chave-super-secreta-jwt' 

    db.init_app(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    # -------------------------------------------------------------
    # FUNÇÕES GLOBAIS (Middleware e Rotas Simples)
    # -------------------------------------------------------------
    
    # 🔑 CORRIGIDO: Registra o before_request DENTRO da função create_app
    @app.before_request
    def set_global_theme():
        # Lê o tema do cookie. Se não existir, assume 'light'.
        g.theme = request.cookies.get('theme', 'light')

    # Rota para ALTERNAR o tema e definir o cookie (action do botão)
    @app.route('/toggle_theme')
    def toggle_theme():
        current_theme = request.cookies.get('theme', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        
        # Redireciona o usuário de volta para a página anterior
        response = make_response(redirect(request.referrer or url_for('index_page')))
        
        # Define o cookie com a nova preferência
        response.set_cookie('theme', new_theme, max_age=60*60*24*365, samesite='Lax')
        return response
    
    # ROTA ORIGINAL (HOME)
    @app.route('/')
    def home():
        if session.get('user_id'):
            return redirect(url_for('usuarios.dashboard'))
        return redirect(url_for('usuarios.login_page'))

    # >>> ROTA ADICIONADA PARA O INDEX.HTML <<<
    @app.route('/index')
    def index_page():
        return render_template('index.html') 

    # -------------------------------------------------------------
    # REGISTRO DE BLUEPRINTS
    # -------------------------------------------------------------
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(pacientes_bp)
    app.register_blueprint(avaliacoes_bp)

    # -------------------------------------------------------------
    # CRIAÇÃO DO BANCO DE DADOS (Incluindo LogAuditoria)
    # -------------------------------------------------------------
    with app.app_context():
        # db.create_all() agora reconhece LogAuditoria
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)