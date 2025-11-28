import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, g
from database import db
from models.paciente import Paciente
from models.usuario import Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.log_manager import registrar_log 

pacientes_bp = Blueprint('pacientes', __name__, url_prefix='/pacientes')


# LISTAR WEB
@pacientes_bp.route('/', methods=['GET'])
def listar_pacientes():
    if not session.get('user_id'):
        return redirect(url_for('usuarios.login_page'))
    user_id = session.get('user_id')
    
    # Busca apenas os pacientes do usuario logado
    pacientes = Paciente.query.filter_by(usuario_id=user_id).all()
    return render_template('pacientes.html', pacientes=pacientes)


# FORMULARIO WEB
@pacientes_bp.route('/novo', methods=['GET', 'POST'])
def novo_paciente():
    if not session.get('user_id'):
        return redirect(url_for('usuarios.login_page'))
    
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        data_nasc = request.form.get('data_nascimento')
        sexo = request.form.get('sexo')
        contato = request.form.get('contato')
        objetivo = request.form.get('objetivo')
        historico = request.form.get('historico')

        try:
            p = Paciente(nome=nome, data_nascimento=data_nasc, sexo=sexo, contato=contato,
                         objetivo=objetivo, historico=historico, usuario_id=user_id)
            db.session.add(p)
            db.session.commit()
            
            # NOVO: REGISTRO DE LOG APOSS CRIACAO
            registrar_log(user_id, 'CREATE', 'PACIENTE', p.id)
            
            flash('Paciente cadastrado.', 'success')
            return redirect(url_for('pacientes.listar_pacientes'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar paciente. Verifique os dados.', 'error')
            print(f"Erro ao cadastrar paciente: {e}")
            return redirect(url_for('pacientes.novo_paciente'))

    return render_template('paciente_form.html', paciente=None)


# EDITAR WEB
@pacientes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id): 
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('usuarios.login_page'))
    
    p = Paciente.query.get_or_404(id)

    if p.usuario_id != user_id:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('pacientes.listar_pacientes'))

    if request.method == 'POST':
        p.nome = request.form.get('nome')
        p.data_nascimento = request.form.get('data_nascimento')
        p.sexo = request.form.get('sexo')
        p.contato = request.form.get('contato')
        p.objetivo = request.form.get('objetivo')
        p.historico = request.form.get('historico')
        
        try: 
            db.session.commit()
            
            # NOVO: REGISTRO DE LOG APÓS EDIÇÃO
            registrar_log(user_id, 'UPDATE', 'PACIENTE', p.id)
            
            flash('Paciente atualizado.', 'success')
            return redirect(url_for('pacientes.listar_pacientes'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar paciente.', 'error')
            print(f"Erro ao atualizar paciente: {e}")
            return redirect(url_for('pacientes.editar_paciente', id=id))
        
    return render_template('paciente_form.html', paciente=p)


# WEB EXCLUIR
@pacientes_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir_paciente(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('usuarios.login_page'))
        
    p = Paciente.query.get_or_404(id)
    
    if p.usuario_id != user_id:
        flash('Você não tem permissão para excluir este paciente.', 'error')
        return redirect(url_for('pacientes.listar_pacientes'))

    try:
        db.session.delete(p)
        db.session.commit()
        
        # NOVO: REGISTRO DE LOG APOIS A EXCLUSAO
        registrar_log(user_id, 'DELETE', 'PACIENTE', id)
        
        flash(f'Paciente {p.nome} excluído.', 'info')
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir paciente: {e}") 
        flash('Erro ao excluir o paciente. Verifique os logs.', 'error')

    return redirect(url_for('pacientes.listar_pacientes'))


# API endpoints (JWT)
@pacientes_bp.route('/api', methods=['GET'])
@jwt_required()
def api_list_pacientes():
    user_id = get_jwt_identity()
    pacientes = Paciente.query.filter_by(usuario_id=user_id).all()
    results = []
    for p in pacientes:
        results.append({
            "id": p.id,
            "nome": p.nome,
            "data_nascimento": p.data_nascimento,
            "sexo": p.sexo,
            "contato": p.contato,
            "objetivo": p.objetivo
        })
    return jsonify(results)


@pacientes_bp.route('/api', methods=['POST'])
@jwt_required()
def api_create_paciente():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    try:
        p = Paciente(
            nome=data.get('nome'),
            data_nascimento=data.get('data_nascimento'),
            sexo=data.get('sexo'),
            contato=data.get('contato'),
            objetivo=data.get('objetivo'),
            historico=data.get('historico'),
            usuario_id=user_id
        )
        db.session.add(p)
        db.session.commit()

        registrar_log(user_id, 'CREATE', 'PACIENTE', p.id)

        return jsonify({"msg": "Paciente criado", "id": p.id}), 201

    except Exception as e:
        db.session.rollback()
        print("Erro API CREATE PACIENTE:", e)
        return jsonify({"error": "Não foi possível criar o paciente"}), 500


@pacientes_bp.route('/api/<int:id>', methods=['DELETE'])
@jwt_required()
def api_excluir_paciente(id):
    user_id = get_jwt_identity()

    p = Paciente.query.get_or_404(id)

    if p.usuario_id != user_id:
        return jsonify({"error": "Acesso negado"}), 403

    try:
        db.session.delete(p)
        db.session.commit()

        registrar_log(user_id, 'DELETE', 'PACIENTE', id)

        return jsonify({"msg": "Paciente excluído"}), 200

    except Exception as e:
        db.session.rollback()
        print("Erro API DELETE PACIENTE:", e)
        return jsonify({"error": "Erro ao excluir paciente"}), 500
