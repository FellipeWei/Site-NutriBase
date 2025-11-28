import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, jsonify
from database import db
from models.paciente import Paciente 
from models.avaliacao import Avaliacao 
from utils.log_manager import registrar_log
from sqlalchemy.orm.exc import NoResultFound

avaliacoes_bp = Blueprint('avaliacoes', __name__, url_prefix='/avaliacoes')

#  FUNÇÃO AUXILIAR PARA TRATAMENTO SEGURO DE FLOAT
def safe_float_get(form_data, key):
    """Retorna o valor como float ou None se o campo estiver vazio."""
    value = form_data.get(key)
    if value:
        try:
            # Tenta converter para float, remove a validacao dO tipo do Flask
            return float(value)
        except ValueError:
            return None 
    return None

# LISTAR AVALIAÇÕES E EXIBIR O FORMULÁRIO
@avaliacoes_bp.route('/<int:paciente_id>', methods=['GET'])
def listar_avaliacoes(paciente_id):
    if not session.get('user_id'):
        return redirect(url_for('usuarios.login_page'))
    
    paciente = Paciente.query.get_or_404(paciente_id)
    
    if paciente.usuario_id != session.get('user_id'):
        flash("Acesso negado.", "error")
        return redirect(url_for('pacientes.listar_pacientes'))
        
 
    avaliacoes = Avaliacao.query.filter_by(paciente_id=paciente_id).order_by(Avaliacao.data.desc()).all()

    return render_template('avaliacoes.html', paciente=paciente, avaliacoes=avaliacoes)


# Rota 2: PROCESSAR NOVA AVALIAÇÃO 

@avaliacoes_bp.route('/nova/<int:paciente_id>', methods=['POST'])
def nova_avaliacao(paciente_id):
    if not session.get('user_id'):
        return redirect(url_for('usuarios.login_page'))
    
    paciente = Paciente.query.get_or_404(paciente_id)
    user_id = session.get('user_id')
    
    # VALIDAR SE OS DADOS ESTAO CEROS
    peso = safe_float_get(request.form, 'peso')
    altura = safe_float_get(request.form, 'altura')
    
    if peso is None or altura is None:
        flash("Peso e altura são obrigatórios e devem ser números válidos.", "error")
        return redirect(url_for('avaliacoes.listar_avaliacoes', paciente_id=paciente_id))

    try:
        # UTILIZA A FUNCAO AUXILIAR 'safe_float_get' PARA TODOS OS CAPOS
        nova_ava = Avaliacao(
            paciente_id=paciente_id,
            peso=peso,
            altura=altura,
            perim_cintura=safe_float_get(request.form, 'perim_cintura'),
            perim_quadril=safe_float_get(request.form, 'perim_quadril'),
            perim_pescoco=safe_float_get(request.form, 'perim_pescoco'),
            perim_braco=safe_float_get(request.form, 'perim_braco'),
            dc_tricipital=safe_float_get(request.form, 'dc_tricipital'),
            dc_bicipital=safe_float_get(request.form, 'dc_bicipital'),
            dc_subescapular=safe_float_get(request.form, 'dc_subescapular'),
            dc_suprailiaca=safe_float_get(request.form, 'dc_suprailiaca'),
            observacoes=request.form.get('observacoes')
        )
        
        db.session.add(nova_ava)
        db.session.commit()
        
        # REGISTRO DE LOG
        
        flash("Avaliação registrada com sucesso!", "success")
        
        return redirect(url_for('avaliacoes.listar_avaliacoes', paciente_id=paciente_id))

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar avaliação: {e}")
        flash("Erro interno ao salvar avaliação.", "error")
        return redirect(url_for('avaliacoes.listar_avaliacoes', paciente_id=paciente_id))


# EXIBIR DETALHES DE UMA AVALIAÇÃO (ROTA FALTANTE) AAAA

@avaliacoes_bp.route('/detalhes/<int:id>', methods=['GET'])
def exibir_avaliacao(id): #<----------------------------------ESTA FUNÇÃO É O ENDPOINT 
    if not session.get('user_id'):
        return redirect(url_for('usuarios.login_page'))

    avaliacao = Avaliacao.query.get_or_404(id)
    paciente = Paciente.query.get_or_404(avaliacao.paciente_id)

    if paciente.usuario_id != session.get('user_id'):
        flash("Acesso negado.", "error")
        return redirect(url_for('pacientes.listar_pacientes'))

    return render_template('relatorio_paciente.html', 
                           avaliacao=avaliacao, 
                           paciente=paciente)

#  EXCLUIR AVALIACAO
@avaliacoes_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir_avaliacao(id):
    if not session.get('user_id'):
        return redirect(url_for('usuarios.login_page'))

    try:
        avaliacao = Avaliacao.query.get_or_404(id)
        paciente_id = avaliacao.paciente_id
        
        if Paciente.query.get_or_404(paciente_id).usuario_id != session.get('user_id'):
             flash("Acesso negado.", "error")
             return redirect(url_for('avaliacoes.listar_avaliacoes', paciente_id=paciente_id))

        db.session.delete(avaliacao)
        db.session.commit()
        
        # REGISTRAR QUE VOI EXCLUIDA

        flash("Avaliação excluída com sucesso.", "info")
        return redirect(url_for('avaliacoes.listar_avaliacoes', paciente_id=paciente_id))

    except NoResultFound:
        flash("Avaliação não encontrada.", "error")
        return redirect(url_for('pacientes.listar_pacientes'))
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir avaliação: {e}")
        flash("Erro interno ao excluir avaliação.", "error")
        return redirect(url_for('avaliacoes.listar_avaliacoes', paciente_id=paciente_id))