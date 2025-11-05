from flask import Flask, render_template, request
from datetime import datetime
from modelo_fungicida import executar_inferencia_fungicida, map_PT, map_EF, map_PA, map_C, map_ES, map_I, map_MV, map_OLV, map_ACE, map_VS, map_IP, map_IPV, map_OP, map_CA, map_SS, map_CI, map_G, executar_segunda_inferencia_fungicida, map_TC, map_A1, map_SA1, map_SA2, map_FA1, map_A2, map_D12, map_PA1, executar_terceira_inferencia_fungicida, map_A2, map_A3, map_D23, map_EM, map_FA2, map_PA2, map_SA2, map_SA3, map_TC
import pandas as pd
import os
from flask import redirect, url_for
import random
import sqlite3

app = Flask(__name__)

#mapeamentos inversos para exibir o que o usuário escolheu em forma de texto.
mapeamento_display = {
    'previsaoTempo'         : {v: k for k, v in map_PT.items()},
    'vazioSanitario'        : {v: k for k, v in map_VS.items()},
    'ocorrenciaParaguai'    : {v: k for k, v in map_OP.items()},
    'correnteAerea'         : {v: k for k, v in map_CA.items()},
    'sojaSafrinha'          : {v: k for k, v in map_SS.items()},
    'chuvaInverno'          : {v: k for k, v in map_CI.items()},
    'geada'                 : {v: k for k, v in map_G.items()},
    'estadioFenologico'     : {v: k for k, v in map_EF.items()},
    'perfilAgricultor'      : {v: k for k, v in map_PA.items()},
    'chuva'                 : {v: k for k, v in map_C.items()},
    'epocaSemeadura'        : {v: k for k, v in map_ES.items()},
    'monitoramentoVisual'   : {v: k for k, v in map_MV.items()},
    'ocorrencia'            : {v: k for k, v in map_OLV.items()},
    'coletaEsporos'         : {v: k for k, v in map_ACE.items()}
}
segundo_mapeamento_display = {
    'toleranciaCultivar'    : {v: k for k, v in map_TC.items()},
    'fungicidaUtilizado'    : {v: k for k, v in map_FA1.items()},
    'periodoAplicacao'      : {v: k for k, v in map_PA1.items()},
    'diferencaDias'         : {v: k for k, v in map_D12.items()}
}
terceiro_mapeamento_display = {
    'toleranciaCultivar'    : {v: k for k, v in map_TC.items()},
    'fungicidaUtilizado'    : {v: k for k, v in map_FA1.items()},
    'periodoAplicacao'      : {v: k for k, v in map_PA2.items()},
    'estadioMaturacao'      : {v: k for k, v in map_EM.items()}
}
nomes_variaveis = {
    "PT": "Previsão do Tempo",
    "EF": "Estádio Fenológico",
    "C" : "Chuva",
    "PA" : "Perfil do Agricultor",
    "OLV" : "Ocorrência em Lavouras Vizinhas",
    "MV" : "Monitoramento Visual",
    "ACE" : "Armadilha de Coleta de Esporos",
    "ES" : "Epoca de Semeadura",
    "VS" : "Vazio Sanitário",
    "OP" : "Ocorrência no Paraguai",
    "CA" : "Corrente Aerea do Oeste para o Leste",
    "SS" : "Soja Safrinha",
    "CI" : "Chuva de Inverno",
    "G" : "Geada",
    "TC" : "Tolerância do Cultivar",
    "SA1" : "Primeira Semana de Aplicação",
    "SA2" : "Segunda Semana de Aplicação",
    "SA3" : "Terceira Semana de Aplicação"
}

CENARIOS_PATH = "cenarios.csv"
RESPOSTAS_PATH = "respostas_especialista.csv"
DB_PATH = "especialista.db"

cenarios = pd.read_csv(CENARIOS_PATH)
total_cenarios = len(cenarios)

# Rota para exibir o primeiro formulário
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form1')
def aplicacaoUm():
    return render_template('aplicacaoUm.html')

@app.route('/resultado', methods=['POST'])
def resultado():
    print("Função resultado() chamada")
    if request.method == 'POST':
        # coleta os dados do formulário e converte para os valores numéricos do modelo
        evidencias_numericas = {
            'PT':   int(request.form['previsaoTempo']),
            'VS':   int(request.form['vazioSanitario']),
            'OP':   int(request.form['ocorrenciaParaguai']),
            'CA':   int(request.form['correnteAerea']),
            'SS':   int(request.form['sojaSafrinha']),
            'CI':   int(request.form['chuvaInverno']),
            'G':    int(request.form['geada']),
            'EF':   int(request.form['estadioFenologico']),
            'PA':   int(request.form['perfilAgricultor']),
            'C':    int(request.form['chuva']),
            'ES':   int(request.form['epocaSemeadura']),
            'MV':   int(request.form['monitoramentoVisual']),
            'OLV':  int(request.form['ocorrencia']),
            'ACE':  int(request.form['coletaEsporos'])
        }
        # exibe os dados no template usando os mapeamentos inversos
        dados_para_exibir = {
            'Previsão do Tempo': mapeamento_display['previsaoTempo'][evidencias_numericas['PT']],
            'Vazio Sanitário': mapeamento_display['vazioSanitario'][evidencias_numericas['VS']],
            'Ocorrência no Paraguai': mapeamento_display['ocorrenciaParaguai'][evidencias_numericas['OP']],
            'Corrente Aerea': mapeamento_display['correnteAerea'][evidencias_numericas['CA']],
            'Soja Safrinha': mapeamento_display['sojaSafrinha'][evidencias_numericas['SS']],
            'Chuva de Inverno': mapeamento_display['chuvaInverno'][evidencias_numericas['CI']],
            'Geada': mapeamento_display['geada'][evidencias_numericas['G']],
            'Estádio Fenológico': mapeamento_display['estadioFenologico'][evidencias_numericas['EF']],
            'Perfil do Agricultor': mapeamento_display['perfilAgricultor'][evidencias_numericas['PA']],
            'Chuva': mapeamento_display['chuva'][evidencias_numericas['C']],
            'Época de Semeadura': mapeamento_display['epocaSemeadura'][evidencias_numericas['ES']],
            'Monitoramento Visual': mapeamento_display['monitoramentoVisual'][evidencias_numericas['MV']],
            'Ocorrência em Lavouras Vizinhas': mapeamento_display['ocorrencia'][evidencias_numericas['OLV']],
            'Armadilha de Coleta de Esporos': mapeamento_display['coletaEsporos'][evidencias_numericas['ACE']]
        }
        # roda a inferencia com as evidencias
        prob_aplicar = executar_inferencia_fungicida(evidencias_numericas)

        # formatacao da probabilidade
        decisao_prob = f"{prob_aplicar:.2%}"

        recomendacao_texto = "Provavelmente Recomendado" if prob_aplicar >= 0.5 else "Provavelmente Não Recomendado"
        if prob_aplicar >= 0.8:
            recomendacao_texto = "Fortemente Recomendado"
        elif prob_aplicar <= 0.2:
            recomendacao_texto = "Fortemente Não Recomendado"

        return render_template('resultado.html', dados=dados_para_exibir, decisao_prob=decisao_prob, recomendacao_texto=recomendacao_texto)
    
    return "Método não permitido", 405

@app.route("/form2")
def segundaAplicacao():
    return render_template('aplicacaoDois.html')

@app.route("/resultado2", methods=['POST'])
def calcular_segunda_aplicacao():
    print("Função resultado2() chamada")
    if request.method == 'POST':
        
        data_plantio   = datetime.strptime(request.form['dataPlantio'], '%Y-%m-%d')
        data_primeira  = datetime.strptime(request.form['dataPrimeira'], '%Y-%m-%d')
        data_segunda   = datetime.strptime(request.form['dataSegunda'], '%Y-%m-%d')

        dt_primeiro = (data_primeira - data_plantio).days
        dt_segunda  = (data_segunda - data_plantio).days

        semana_primeira = max(1, dt_primeiro // 7 + 1)
        semana_segunda  = max(1, dt_segunda // 7 + 1)

        evidencias_numericas = {
            'TC' : int(request.form['toleranciaCultivar']),
            'FA1': int(request.form['fungicidaUtilizado']),
            'SA1': semana_primeira,
            'SA2': semana_segunda
        }

        prob, var_pa1, valorD12 = executar_segunda_inferencia_fungicida(evidencias_numericas)

        dados_para_exibir = {
            'Tolerância do Cultivar'                           : segundo_mapeamento_display['toleranciaCultivar'][evidencias_numericas['TC']],
            'Fungicida Utilizado'                              : segundo_mapeamento_display['fungicidaUtilizado'][evidencias_numericas['FA1']],
            'Data do Plantio'                                  : data_plantio.strftime('%d/%m/%Y'),
            'Primeira aplicação (data)'                        : data_primeira.strftime('%d/%m/%Y') + f" (Semana {semana_primeira})",
            'Segunda aplicação (data)'                         : data_segunda.strftime('%d/%m/%Y') + f" (Semana {semana_segunda})",
            'Periodo Residual do Produto'                      : segundo_mapeamento_display['periodoAplicacao'][var_pa1],
            'Diferença entre a primeira e a segunda aplicação' : segundo_mapeamento_display['diferencaDias'][valorD12]
        }

        decisao_prob = f"{prob:.2%}"

        if prob >= 0.8:
            recomendacao_texto = "Fortemente Recomendado"
        elif prob >= 0.5:
            recomendacao_texto = "Provavelmente Recomendado"
        elif prob <= 0.2:
            recomendacao_texto = "Fortemente Não Recomendado"
        else:
            recomendacao_texto = "Provavelmente Não Recomendado"

        return render_template(
            'resultado2.html',
            dados=dados_para_exibir,
            decisao_prob=decisao_prob,
            recomendacao_texto=recomendacao_texto
        )

    return "Método não permitido", 405

@app.route("/form3")
def aplicacaoTres():
    return render_template('aplicacaoTres.html')

from datetime import datetime
from flask import request, render_template

@app.route("/resultado3", methods=['POST'])
def calcular_terceira_aplicacao():
    print("Função resultado3() chamada")
    if request.method == 'POST':
        try:
            # Captura e conversão das datas
            data_plantio   = datetime.strptime(request.form['dataPlantio'], '%Y-%m-%d')
            data_segunda   = datetime.strptime(request.form['dataSegunda'], '%Y-%m-%d')
            data_terceira  = datetime.strptime(request.form['dataTerceira'], '%Y-%m-%d')

            # Cálculo das semanas relativas ao plantio
            semana_segunda  = (data_segunda  - data_plantio).days // 7 + 1
            semana_terceira = (data_terceira - data_plantio).days // 7 + 1

            if semana_segunda <= 0 or semana_terceira <= 0:
                return "Erro: datas de aplicação não podem ser anteriores ao plantio."

            if semana_terceira < semana_segunda:
                return "Erro: a terceira aplicação não pode ocorrer antes da segunda."
            
            evidencias_numericas = {
                'TC' :  int(request.form['toleranciaCultivar']),
                'FA2':  int(request.form['fungicidaUtilizado']),
                'SA2':  semana_segunda,
                'SA3':  semana_terceira
            }

            prob, var_em, var_pa2 = executar_terceira_inferencia_fungicida(evidencias_numericas)

            dados_para_exibir = {
                'Tolerância do Cultivar'        : terceiro_mapeamento_display['toleranciaCultivar'][evidencias_numericas['TC']],
                'Fungicida Utilizado'           : terceiro_mapeamento_display['fungicidaUtilizado'][evidencias_numericas['FA2']],
                'Segunda semana de aplicação'   : data_segunda.strftime('%d/%m/%Y') + f" (Semana {semana_segunda})",
                'Terceira semana de aplicação'  : data_terceira.strftime('%d/%m/%Y') + f" (Semana {semana_terceira})",
                'Período Residual do produto'   : terceiro_mapeamento_display['periodoAplicacao'][var_pa2],
                'Estádio de Maturação'          : terceiro_mapeamento_display['estadioMaturacao'][var_em]
            }

            decisao_prob = f"{prob:.2%}"

            if prob >= 0.8:
                recomendacao_texto = "Fortemente Recomendado"
            elif prob >= 0.5:
                recomendacao_texto = "Provavelmente Recomendado"
            elif prob <= 0.2:
                recomendacao_texto = "Fortemente Não Recomendado"
            else:
                recomendacao_texto = "Provavelmente Não Recomendado"

            return render_template('resultado3.html',
                dados=dados_para_exibir,
                decisao_prob=decisao_prob,
                recomendacao_texto=recomendacao_texto)

        except Exception as e:
            return f"Erro ao processar os dados: {e}"

    return "Método não permitido", 405

@app.route("/especialista", methods=["GET", "POST"])
def formulario_especialista():
    if request.method == "POST":
        cenario_id = request.form["cenario_id"]
        decisao = request.form["decisao"]
        justificativa = request.form.get("justificativa", "")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO respostas_especialista (cenario_id, decisao, justificativa)
            VALUES (?, ?, ?)
        """, (cenario_id, decisao, justificativa))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    cenario_id = random.randint(0, total_cenarios - 1)
    cenario = cenarios.iloc[cenario_id].to_dict()

    return render_template(
        "formEspecialista.html",
        cenario=cenario,
        cenario_id=cenario_id,
        nomes_variaveis=nomes_variaveis,
        total=total_cenarios
    )

if __name__ == '__main__':
    from os import environ
    app.run(host='0.0.0.0', port=int(environ.get('PORT', 8080)))