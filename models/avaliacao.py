import datetime
from database import db
from sqlalchemy import func 

# CLASSIFICAÇÕES MASCULINAS E FEMININAS PARA %GC E PERÍMETROS
# As classificações complexas como Adequação do PB e Curvas serão baseadas em referências fixas no Python.(nao esqucer)

class Avaliacao(db.Model):
    __tablename__ = 'avaliacao'

    id = db.Column(db.Integer, primary_key=True)
    
    # 🔑 CORREÇÃO CRÍTICA: Usa func.now() para que o banco de dados defina a data/hora
    data = db.Column(db.DateTime, default=func.now(), nullable=False) 
    
    # DADOS BÁSICOS
    peso = db.Column(db.Float, nullable=False) # Kg
    altura = db.Column(db.Float, nullable=False) # cm
    
    # PERÍMETROS
    perim_cintura = db.Column(db.Float) # PC
    perim_quadril = db.Column(db.Float) # PQ
    perim_pescoco = db.Column(db.Float) # PP
    perim_braco = db.Column(db.Float) # PB
    
    # DOBRAS CUTÂNEAS (DC)
    dc_tricipital = db.Column(db.Float)
    dc_bicipital = db.Column(db.Float)
    dc_subescapular = db.Column(db.Float)
    dc_suprailiaca = db.Column(db.Float)
    
    observacoes = db.Column(db.Text) 

    # CHAVE ESTRANGEIRA
    paciente_id = db.Column(
        db.Integer, 
        db.ForeignKey('paciente.id', ondelete='CASCADE'), 
        nullable=False
    )

    #  CÁLCULOS QUE  O SITE VAI FAZER

    @property
    def imc(self):
        """Calcula o Índice de Massa Corporal (IMC)"""
        if self.peso and self.altura:
            altura_m = self.altura / 100.0
            try:
                imc_valor = self.peso / (altura_m ** 2)
                return round(imc_valor, 2)
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def classificacao_imc_risco(self):
        """Classifica o Risco de Comorbidade associado ao IMC."""
        imc = self.imc
        if imc < 18.5: return "Baixo Risco"
        if 18.5 <= imc <= 24.99: return "Risco Baixo"
        if 25.00 <= imc <= 29.99: return "Risco Aumentado"
        if 30.00 <= imc <= 34.99: return "Moderado"
        if 35.00 <= imc <= 39.99: return "Grave"
        if imc >= 40.00: return "Muito Grave"
        return "-"

    @property
    def rce(self):
        """Relação Cintura Estatura (RCE = PC / Altura em cm)"""
        if self.perim_cintura and self.altura:
            rce_valor = self.perim_cintura / self.altura
            return round(rce_valor, 2)
        return 0.0

    @property
    def classificacao_rce(self):
        """Classifica RCE (RCE >= 0.5 é risco para alterações metabólicas)"""
        if self.rce >= 0.5:
            return "Risco para Alterações Metabólicas (Elevado)"
        return "Risco Baixo"

    @property
    def rcq(self):
        """Relação Cintura Quadril (RCQ = PC / PQ)"""
        if self.perim_cintura and self.perim_quadril:
            rcq_valor = self.perim_cintura / self.perim_quadril
            return round(rcq_valor, 2)
        return 0.0

    def classificacao_rcq(self, sexo):
        """Classifica RCQ com base no sexo."""
        rcq = self.rcq
        if sexo == 'Feminino':
            return "Maior que 0,85 - Risco de Gordura Abdominal" if rcq > 0.85 else "Risco Baixo"
        if sexo == 'Masculino':
            return "Maior que 1,0 - Risco de Gordura Abdominal" if rcq > 1.0 else "Risco Baixo"
        return "Sexo não definido"

    @property
    def soma_dobras_centrais(self):
        """Soma das dobras Centrais (Subescapular + Supra-ilíaca)"""
        return (self.dc_subescapular or 0) + (self.dc_suprailiaca or 0)

    @property
    def soma_dobras_perifericas(self):
        """Soma das dobras Periféricas (Tricipital + Bicipital)"""
        return (self.dc_tricipital or 0) + (self.dc_bicipital or 0)
    
    @property
    def idc_dcp_dcc(self):
        """Índice de Distribuição de Gordura (IDP/DCC)"""
        if self.soma_dobras_centrais > 0:
            idc = self.soma_dobras_perifericas / self.soma_dobras_centrais
            return round(idc, 2)
        return 0.0
    
    def classificacao_idc(self):
        """Classificação do Índice de Distribuição de Gordura"""
        idc = self.idc_dcp_dcc
        if idc > 1:
            return "Localizada em região periférica"
        if idc < 1:
            return "Localizada em região central"
        return "Distribuição Balanceada"