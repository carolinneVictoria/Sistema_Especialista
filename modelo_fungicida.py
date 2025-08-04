import pymc as pm
import numpy as np
import arviz as az
import pymc.math as pm_math
import matplotlib.pyplot as plt
import multiprocessing
multiprocessing.set_start_method("spawn", force=True)

#Variaveis
map_A1  = {'nao': 0, 'sim': 1}
map_ACE = {'ausente': 0, 'presente': 1}
map_C   = {'pouca': 0, 'normal': 1, 'muita': 2}
map_CC  = {'desfav': 0, 'fav': 1}
map_CPS = {'desfav': 0, 'fav': 1}
map_D   = {'ausente': 0, 'presente': 1}
map_EF  = {'antesFlores': 0, 'aPartirFlores': 1}
map_ES  = {'precoce': 0, 'normal': 1, 'tardia': 2}
map_I   = {'baixo': 0, 'alto': 1}
map_MV  = {'negativo': 0, 'positivo': 1}
map_OLV = {'nao': 0, 'sim': 1}
map_PA  = {'conservador': 0, 'inovador': 1}
map_PT  = {'desfav': 0, 'fav': 1}
map_VS  = {'nao': 0, 'sim': 1}
map_IP  = {'ausente': 0, 'presente': 1}
map_IPV = {'baixo': 0, 'alto': 1}
map_OP  = {'nao': 0, 'sim': 1}
map_CA  = {'nao': 0, 'sim': 1}
map_SS  = {'nao': 0, 'sim': 1}
map_CI  = {'seco': 0, 'normal': 1, 'chuvoso': 2}
map_G   = {'pouca': 0, 'muita': 1}
map_A2  = {'nao': 0, 'sim': 1}
map_TC  = {'susceptivel': 0, 'tolerante': 1} #tolerancia de cultivar
map_PA1 = {'dentroPeriodo': 0, 'acimaPeriodo': 1} #Período residual do produto utilizado na primeira aplicação
map_SA1 = list(range(1, 18))  # semanas 1 a 17
map_SA2 = list(range(1, 18))
map_D12 = {'menos14Dias': 0, 'entre14E21Dias': 1, 'mais21Dias': 2} #Diferença entre a primeira e a segunda aplicação
map_FA1 = {'nenhum': 0, 'triazolEstrub': 1, 'carbEstrob': 2} #Fungicida utilizado na primeira aplicação
map_A1  = {'nao': 0, 'sim': 1}
map_A3   = {'nao': 0, 'sim': 1}
map_TC  = {'susceptivel': 0, 'tolerante': 1}
map_EM  = {'ateR6': 0, 'aPartirR6': 1} #estadio de maturação
map_PA2 = {'dentroPeriodo': 0, 'acimaPeriodo': 1}
map_SA2 = list(range(1, 18))
map_SA3 = list(range(1, 18))
map_FA2 = {'nenhum': 0, 'triazolEstrob': 1, 'carbEstrob': 2}
map_D23 = {'menos14Dias': 0, 'entre14E21Dias': 1, 'mais21Dias': 2}
map_A2  = {'nao': 0, 'sim': 1}

def calculoPeriodoResidual(sa1, sa2):
    dif = sa2 - sa1
    if dif < 2:
        return 0  # 'menos14Dias'
    elif dif < 3:
        return 1  # 'entre14E21Dias'
    else:
        return 2  # 'mais21Dias'
    
def calculoPeriodoResidual2(sa2, sa3):
    dif = sa3 - sa2
    if dif < 2:
        return 0  # 'menos14Dias'
    elif dif < 3:
        return 1  # 'entre14E21Dias'
    else:
        return 2  # 'mais21Dias'

def executar_inferencia_fungicida(evidencias=None):
    evidencias = evidencias or {}

    with pm.Model() as aplicacaoFungicida:
        def var(nome, p, mapeamento=None):
            if nome in evidencias:
                valor = evidencias[nome]
                return pm.ConstantData(nome, valor)
            else:
                return pm.Categorical(nome, p=p)

        # Variáveis raiz (com probabilidades marginais)
        C   = var("C", [0.33, 0.34, 0.33])
        PT  = var("PT", [0.5, 0.5])
        EF  = var("EF", [0.5, 0.5])
        PA  = var("PA", [0.5, 0.5])
        OLV = var("OLV", [0.5, 0.5])
        MV  = var("MV", [0.5, 0.5])
        ACE = var("ACE", [0.5, 0.5])
        ES  = var("ES", [0.33, 0.34, 0.33])
        VS  = var("VS", [0.5, 0.5])
        OP  = var("OP", [0.5, 0.5])
        CA  = var("CA", [0.5, 0.5])
        SS  = var("SS", [0.5, 0.5])
        CI  = var("CI", [0.33, 0.34, 0.33])
        G   = var("G", [0.5, 0.5])


        #tabelas de probabilidade condicional

        # 1. CC depende de C
        prob_CC = pm.math.switch(
            pm.math.eq(C, 0), [0.8, 0.2], #abaixo do normal
            pm.math.switch(
                pm.math.eq(C, 1), [0.5, 0.5],  #normal
                [0.0, 1.0]  #acima do normal
            )
        )
        CC = var("CC", prob_CC)

        # 1.1 IPV depende de SS, CI, G
        p_IPV = pm_math.switch(pm_math.eq(SS, 0),
            pm_math.switch(pm_math.eq(CI, 0),
                pm_math.switch(pm_math.eq(G, 0), [0.8, 0.2], [1.0, 0.0]),           # SS=0, CI=0
                pm_math.switch(pm_math.eq(CI, 1),
                    pm_math.switch(pm_math.eq(G, 0), [0.9, 0.1], [0.95, 0.05]),    # SS=0, CI=1
                    pm_math.switch(pm_math.eq(G, 0), [0.6, 0.4], [0.9, 0.1])       # SS=0, CI=2
                )
            ),
            pm_math.switch(pm_math.eq(CI, 0),
                pm_math.switch(pm_math.eq(G, 0), [0.7, 0.3], [0.9, 0.1]),           # SS=1, CI=0
                pm_math.switch(pm_math.eq(CI, 1),
                    pm_math.switch(pm_math.eq(G, 0), [0.5, 0.5], [0.85, 0.15]),    # SS=1, CI=1
                    pm_math.switch(pm_math.eq(G, 0), [0.0, 1.0], [0.8, 0.2])       # SS=1, CI=2
                )
            )
        )
        IPV = var("IPV", p_IPV)

        # 1.2 IP depende de OP e CA
        p_IP = pm.math.switch(pm.math.eq(OP, 0),
            pm.math.switch(pm.math.eq(CA, 0), [1.0, 0.0], [0.8, 0.2]),  # OP=0
            pm.math.switch(pm.math.eq(CA, 0), [1.0, 0.0], [0.2, 0.8])   # OP=1
        )
        IP = var("IP", p_IP)


        # 1.3 I depende de VS, IP e IPV
        p_I = pm_math.switch(pm_math.eq(IPV, 0),
            pm_math.switch(pm_math.eq(VS, 0),
                pm_math.switch(pm_math.eq(IP, 0), [0.4, 0.6], [0.3, 0.7]),  # IPV: 0, VS: 0, IP: 0 ou 1
                pm_math.switch(pm_math.eq(IP, 0), [0.8, 0.2], [0.4, 0.6])   # IPV: 0, VS: 1, IP: 0 ou 1
            ),
            pm_math.switch(pm_math.eq(VS, 0),
                pm_math.switch(pm_math.eq(IP, 1), [0.2, 0.8], [0.0, 1.0]),  # IPV: 1, VS: 0, IP: 0 ou 1
                pm_math.switch(pm_math.eq(IP, 1), [0.3, 0.7], [0.3, 0.7])   # IPV: 1, VS: 1, IP: 0 ou 1
            )
        )
        I = var("I", p_I)

        # 2. CPS depende de ES e I
        p_CPS = pm.math.switch(pm.math.eq(ES, 0),
            pm.math.switch(pm.math.eq(I, 0), 
            [1.0, 0.0], [0.6, 0.4]), #ES: 0, I: 0 ou 1
                                
            pm.math.switch(pm.math.eq(ES, 1),
                pm.math.switch(pm.math.eq(I, 0), [0.4, 0.6], [0.3, 0.7]), #ES: 1, I: 0 ou 1
                pm.math.switch(pm.math.eq(I, 0), [0.2, 0.8], [0.0, 1.0]) #ES: 2, I: 0 ou 1
            )
        )
        CPS = var("CPS", p_CPS)

        # 3. D depende MV, ACE, OLV
        p_D = pm_math.switch(pm_math.eq(MV, 0),
            pm_math.switch(pm_math.eq(ACE, 0),
                pm_math.switch(pm_math.eq(OLV, 0), [0.8, 0.2], [0.2, 0.8]), #mv: 0, ace: 0, olv: 0 e 1
                pm_math.switch(pm_math.eq(OLV, 0), [0.4, 0.6], [0.2, 0.8])  #mv: 0, ace: 1, olv: 0 e 1
            ), #se o MV for 1
            [0.0, 1.0]  # qualquer valor de ACE e OLV dá a mesma prob.
        )

        D = var("D", p_D)

        # 4. A1 depende de PT, EF, PA, CC, D, CPS
        p_A1 = pm.math.switch(
        pm.math.eq(D, 0),  # D: 'ausente'
        pm.math.switch(
            pm.math.eq(EF, 0),  # EF:'antesFlores'
            pm.math.stack([1.0, 0.0]),  # [1, 0]
            pm.math.switch(
                pm.math.eq(PA, 0),  # PA: 'conservador'
                pm.math.stack([0.0, 1.0]),
                pm.math.switch(
                    pm.math.eq(CC, 0) * pm.math.eq(PT, 0) * pm.math.eq(CPS, 0),
                    pm.math.stack([0.0, 1.0]),
                    pm.math.switch(
                        pm.math.eq(CC, 0) * pm.math.eq(PT, 0) * pm.math.eq(CPS, 1),
                        pm.math.stack([0.8, 0.2]),
                        pm.math.switch(
                            pm.math.eq(CC, 0) * pm.math.eq(PT, 1) * pm.math.eq(CPS, 0),
                            pm.math.stack([0.3, 0.7]),
                            pm.math.switch(
                                pm.math.eq(CC, 0) * pm.math.eq(PT, 1) * pm.math.eq(CPS, 1),
                                pm.math.stack([0.2, 0.8]),
                                pm.math.switch(
                                    pm.math.eq(CC, 1) * pm.math.eq(PT, 0) * pm.math.eq(CPS, 0),
                                    pm.math.stack([0.7, 0.3]),
                                    pm.math.switch(
                                        pm.math.eq(CC, 1) * pm.math.eq(PT, 0) * pm.math.eq(CPS, 1),
                                        pm.math.stack([0.5, 0.5]),
                                        pm.math.switch(
                                            pm.math.eq(CC, 1) * pm.math.eq(PT, 1) * pm.math.eq(CPS, 0),
                                            pm.math.stack([0.3, 0.7]),
                                            pm.math.switch(
                                                pm.math.eq(CC, 1) * pm.math.eq(PT, 1) * pm.math.eq(CPS, 1),
                                                pm.math.stack([0.0, 1.0]),
                                                pm.math.stack([0.5, 0.5])  # fallback
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        # se D: 'presente'
        pm.math.stack([0.0, 1.0])
            )
        A1 = pm.Categorical("A1", p=p_A1)
        
        trace_inf = pm.sample(draws=100, chains=1, tune=50, return_inferencedata=True)

    # Extrai as amostras e calcula a probabilidade de A1 ser 'sim' (1)
    a1_samples = trace_inf.posterior["A1"].values.flatten()
    prob_sim = np.mean(a1_samples == 1)
    return prob_sim

def executar_segunda_inferencia_fungicida(evidencias):
    sa1 = evidencias["SA1"]
    sa2 = evidencias["SA2"]
    valorD12 = calculoPeriodoResidual(sa1, sa2)

    with pm.Model() as aplicacaoFungicida2:
        TC  = pm.Categorical("TC", p=[0.5, 0.5])
        A1  = pm.Data("A1", 1)

        # tpc de FA1 depende de A1
        p_FA1 = pm_math.switch(pm_math.eq(A1, 0),
                    [1.0, 0.0, 0.0],  # A1: nao
                    [0.0, 0.5, 0.5])  # A1: sim

        FA1 = pm.Categorical("FA1", p=p_FA1)

        cond_d12= pm.math.eq(valorD12, 0)  #expressão para D12 = 0

        p_PA1 = pm.math.switch(pm.math.eq(FA1, 0),  # FA1: nenhum
            [1.0, 0.0],
            pm.math.switch(pm.math.eq(FA1, 1),      # FA1: triazol
                pm.math.switch(cond_d12, [1.0, 0.0], [0.0, 1.0]),
                pm.math.switch(cond_d12, [1.0, 0.0], [0.0, 1.0])
            )
        )
        PA1 = pm.Categorical("PA1", p=p_PA1)

        # tpc de A2 depende de TC e PA1
        p_A2 = pm.math.switch(pm.math.eq(TC, 0), #tc: suceptivel
            pm.math.switch(pm.math.eq(PA1, 0), #PA1: dentroPeriodo
                [1.0, 0.0],
                [0.0, 1.0] #acimaPeriodo
            ),
            pm.math.switch(pm.math.eq(PA1, 0), #TC: tolerante/PA1: dentroPeriodo
                [1.0, 0.0],
                [1.0, 0.0]
            )
        )

        A2 = pm.Categorical("A2", p=p_A2)

        trace_inf = pm.sample(draws=100, chains=1, tune=50, return_inferencedata=True)

    a2_samples = trace_inf.posterior["A2"].values.flatten()
    pa1_samples = trace_inf.posterior["PA1"].values.flatten()

    prob_sim = np.mean(a2_samples == 1)
    var_pa1 = int(np.round(np.mean(pa1_samples)))

    return prob_sim, var_pa1, valorD12

def executar_terceira_inferencia_fungicida(evidencias):
    sa2 = evidencias["SA2"]
    sa3 = evidencias["SA3"]
    valorD23 = calculoPeriodoResidual2(sa2, sa3)

    with pm.Model() as aplicacaoFungicida3:
        TC  = pm.Categorical("TC", p=[0.5, 0.5])
        A2  = pm.Data("A2", 1)

        # tpc de FA2 depende de A
        p_FA2 = pm_math.switch(pm_math.eq(A2, 0),
                    [1.0, 0.0, 0.0],  # A: nao
                    [0.0, 0.5, 0.5])  # A: sim

        FA2 = pm.Categorical("FA2", p=p_FA2)

        cond_d23= pm.math.eq(valorD23, 0)  #expressão para D23 = 0

        p_PA2 = pm.math.switch(pm.math.eq(FA2, 0),  # FA2: nenhum
            [1.0, 0.0],
            pm.math.switch(pm.math.eq(FA2, 1),      # FA1: triazol
                pm.math.switch(cond_d23, [1.0, 0.0], [0.0, 1.0]),
                pm.math.switch(cond_d23, [1.0, 0.0], [0.0, 1.0])
            )
        )
        PA2 = pm.Categorical("PA2", p=p_PA2)

        #SA2 e SA3 >= 16 : passou do R6
        causa_sa2 = 1.0 if sa2 >= 15 else 0.0
        causa_sa3 = 1.0 if sa3 >= 15 else 0.0
        leak = 0.3

        # Cálculo do noisy-MAX
        prob_aPartirR6 = 1 - (1 - causa_sa2) * (1 - causa_sa3) * (1 - leak)

        p_em = [1 - prob_aPartirR6, prob_aPartirR6]
        EM = pm.Categorical("EM", p=p_em)

        # TPC de A3 que depende de TC, EM e PA2
        p_A3 = pm.math.switch(pm.math.eq(TC, 0),  # susceptível
                    pm.math.switch(pm.math.eq(EM, 0),  # ateR6
                        pm.math.switch(pm.math.eq(PA2, 0),
                            np.array([1.0, 0.0]),  # nao
                            np.array([0.0, 1.0])   # sim
                        ),
                        pm.math.switch(pm.math.eq(PA2, 0),  # aPartirR6
                            np.array([0.0, 1.0]),  # sim
                            np.array([1.0, 0.0])   # nao
                        )
                    ),
                    pm.math.switch(pm.math.eq(EM, 0),  # tolerante + ateR6
                        np.array([1.0, 0.0]),  # nao
                        pm.math.switch(pm.math.eq(PA2, 0),
                            np.array([1.0, 0.0]),  # nao
                            np.array([0.0, 1.0])   # sim
                        )
                    )
                )

        A3 = pm.Categorical("A3", p=p_A3)
        trace_inf = pm.sample(draws=100, chains=1, tune=50, return_inferencedata=True)

    a3_samples = trace_inf.posterior["A3"].values.flatten()
    em_samples = trace_inf.posterior["EM"].values.flatten()
    pa2_samples = trace_inf.posterior["PA2"].values.flatten()

    prob_sim = np.mean(a3_samples == 1)
    var_em = int(np.round(np.mean(em_samples)))
    var_pa2 = int(np.round(np.mean(pa2_samples)))

    return prob_sim, var_em, var_pa2