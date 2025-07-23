from flask import Flask, render_template, request
from datetime import datetime
from modelo_fungicida import executar_inferencia_fungicida, map_PT, map_EF, map_PA, map_C, map_ES, map_I, map_MV, map_OLV, map_ACE, map_VS, map_IP, map_IPV, map_OP, map_CA, map_SS, map_CI, map_G, executar_segunda_inferencia_fungicida, map_TC, map_A1, map_SA1, map_SA2, map_FA1, map_A2, map_D12, map_PA1, executar_terceira_inferencia_fungicida, map_A2, map_A3, map_D23, map_EM, map_FA2, map_PA2, map_SA2, map_SA3, map_TC

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

# Rota para exibir o primeiro formulário
@app.route('/')
def index():
    return render_template('index.html')

# Rota para exibir o primeiro formulário
@app.route('/form1')
def aplicacaoUm():
    return render_template('aplicacaoUm.html')

# Rota para processar os dados do formulário
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

#rota para exibir o segundo Formulario
@app.route("/form2")
def segundaAplicacao():
    return render_template('aplicacaoDois.html')

#Rota para processsar os dados do segundo formulário
@app.route("/resultado2", methods=['POST'])
def calcular_segunda_aplicacao():
    print("Função resultado2() chamada")
    if request.method == 'POST':
        # Converte as datas recebidas em semanas do ano
        data_primeira = datetime.strptime(request.form['dataPrimeira'], '%Y-%m-%d')
        data_segunda = datetime.strptime(request.form['dataSegunda'], '%Y-%m-%d')

        semana_primeira = data_primeira.isocalendar()[1]
        semana_segunda = data_segunda.isocalendar()[1]

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
            'Primeira aplicação (data)'                        : data_primeira.strftime('%d/%m/%Y') + f" (Semana {semana_primeira})",
            'Segunda aplicação (data)'                         : data_segunda.strftime('%d/%m/%Y') + f" (Semana {semana_segunda})",
            'Periodo Residual do Produto'                      : segundo_mapeamento_display['periodoAplicacao'][var_pa1],
            'Diferença entre a primeira e a segunda aplicação' : segundo_mapeamento_display['diferencaDias'][valorD12]
        }

        # Formatação da probabilidade
        decisao_prob = f"{prob:.2%}"

        # Recomendação textual com base na probabilidade
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

#rota para exibir o terceiro Formulario
@app.route("/form3")
def aplicacaoTres():
    return render_template('aplicacaoTres.html')

#Rota para processar os dados do terceiro formulario
@app.route("/resultado3", methods=['POST'])
def calcular_terceira_aplicacao():
    print("Função resultado3() chamada")
    if request.method == 'POST':
        evidencias_numericas = {
            'TC' :  int(request.form['toleranciaCultivar']),
            'FA2' :  int(request.form['fungicidaUtilizado']),
            'SA2':  int(request.form['segundaSemana']),
            'SA3':  int(request.form['terceiraSemana'])
        }

        prob, var_em, var_pa2 = executar_terceira_inferencia_fungicida(evidencias_numericas)

        dados_para_exibir = {
            'Tolerância do Cultivar'        : terceiro_mapeamento_display['toleranciaCultivar'][evidencias_numericas['TC']],
            'Fungicida Utilizado'           : terceiro_mapeamento_display['fungicidaUtilizado'][evidencias_numericas['FA2']],
            'Segunda semana de aplicação'   : f"Semana {evidencias_numericas['SA2']}",
            'Terceira semana de aplicação'  : f"Semana {evidencias_numericas['SA3']}",
            'Período Residual do produto'   : terceiro_mapeamento_display['periodoAplicacao'][var_pa2],
            'Estádio de Maturação'          : terceiro_mapeamento_display['estadioMaturacao'][var_em]
        }
        # formatacao da probabilidade
        decisao_prob = f"{prob:.2%}"

        recomendacao_texto = "Provavelmente Recomendado" if prob >= 0.5 else "Provavelmente Não Recomendado"
        if prob >= 0.8:
            recomendacao_texto = "Fortemente Recomendado"
        elif prob <= 0.2:
            recomendacao_texto = "Fortemente Não Recomendado"

        return render_template('resultado3.html', dados=dados_para_exibir, decisao_prob=decisao_prob, recomendacao_texto=recomendacao_texto)

    return "Método não permitido", 405

if __name__ == '__main__':
    app.run(debug=True)