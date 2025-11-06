import numpy as np

class Math_Dev:
    def __init__(self, tempos_trabalhos):
        # PAsso 0 do algoritmos
        # Lista de tempo de processamento dos trabalhos
        self.tempos_trabalhos = tempos_trabalhos # São os dados
        self.n = len(tempos_trabalhos) # Número de trabalhos
        self.m = len(tempos_trabalhos[0]) # Número de máquinas

        self.C = np.zeros((self.n, self.m)) # Matriz de tempos de conclusão

        # Linhas: trabalho
        # Colunas: máquinas

        self.lbs = [0] * self.m 

    def calcular_tempo_maquina(self):
        # Aqui vai ser papo do passo 1 do algoritmo

        totais = [0] * self.m
        for j in range(self.n):
            for i in range(self.m):
                totais[i] += self.tempos_trabalhos[j][i]
        return totais
    
    def calcular_gargalos(self):

        # Calculo de gargalos já generalizados, tava meio ruim
        # de adaptar de 3 pra mais

        matriz = np.array(self.tempos_trabalhos)
        maquinas = matriz.T  # (m_maquinas, n_trabalhos)
        
        gargalos = []
        for k in range(self.m):
            max_k = maquinas[k].max()
            
            soma_outros = sum(
                maquinas[j].min() 
                for j in range(self.m) 
                if j != k
            )# número de máquinas
            
            LBk = max_k + soma_outros
            gargalos.append(LBk)
        
        return gargalos, min(gargalos)

    def calcular_makespan(self, sequencia):
        n = len(sequencia) # fila de trabalhos
        m = len(self.tempos_trabalhos[0])

        for i in range(n):
            trabalho = sequencia[i]
            for j in range(m):
                if i == 0 and j == 0:
                    self.C[i][j] = self.tempos_trabalhos[trabalho][j]
                elif i == 0:
                    self.C[i][j] = self.C[i][j-1] + self.tempos_trabalhos[trabalho][j]
                elif j == 0:
                    self.C[i][j] = self.C[i-1][j] + self.tempos_trabalhos[trabalho][j]
                else:
                    self.C[i][j] = max(self.C[i-1][j], self.C[i][j-1]) + self.tempos_trabalhos[trabalho][j]
        return self.C[n-1][m-1]
    
    def calcular_lower_bound_parcial():
        # Teria que receber do cálculo de gargalos aqui
        # TO-DO
        pass

    def branch_and_bound(self):
        # TO-DO
        pass

    def busca_tabu(self):
        # TO-DO
        pass
    

    




