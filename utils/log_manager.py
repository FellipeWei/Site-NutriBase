from database import db
from models.log_auditoria import LogAuditoria

def registrar_log(usuario_id, acao, recurso, recurso_id=None):
    """
    Função auxiliar para persistir um evento no Log de Auditoria.
    """
    try:
        novo_log = LogAuditoria(
            usuario_id=usuario_id,
            acao=acao,
            recurso=recurso,
            recurso_id=recurso_id
        )
        db.session.add(novo_log)
        db.session.commit()
    except Exception as e:
        # Se o log falhar, apenas registramos o erro no console e continuamos.
        print(f"ERRO AO REGISTRAR LOG: {e}")
        db.session.rollback()