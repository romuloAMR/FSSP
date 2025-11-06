import numpy as np

class MathDev:
    def __init__(self, tempos_trabalhos):
        """
            Classe MathDev para o problema de escalonamento de trabalhos em máquinas (FSSP).
            A classe é uma abstração do desenvolvimento apresentado no artigo, diferenciando que temos uma generalização
            para m máquinas e n trabalhos.

            Como atributos temos:
                - tempos_trabalhos: matriz de tempos de processamento dos trabalhos em cada máquina
                - n: número de trabalhos (linhas)
                - m: número de máquinas (colunas)
                - C: matriz de tempos de conclusão
                - lbs: lista de lower bounds para cada máquina
        """
        self.tempos_trabalhos = tempos_trabalhos 
        self.n = len(tempos_trabalhos)
        self.m = len(tempos_trabalhos[0])

        self.C = np.zeros((self.n, self.m))
        self.lbs = [0] * self.m 

    def calcular_makespan(self, sequencia):
        """
            Função 'calcular_makespan' calcula o makespan (tempo total de conclusão) para uma dada sequência de trabalhos.
            Retorna o valor do makespan.
            
            O cálculo segue a lógica de programação dinâmica considerando as restrições:
            - Nenhuma ultrapassagem é permitida (ordem é mantida)
            - Cada operação, uma vez iniciada, tem que ser concluída
            - Um trabalho não pode ser processado por mais de uma máquina ao mesmo tempo
            
            A matriz C[i][j] armazena o tempo de conclusão do trabalho i na máquina j.
        """
        n = len(sequencia)
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

    def calcular_gargalos(self):
        """
            Função 'calcular_gargalos' calcula os gargalos (lower bounds) para cada máquina.
            Retorna uma lista com os lower bounds e o menor lower bound entre eles.

            Remete ao passo 2 do artigo.

            Explicação: Pegamos o tempo mais demorado para uma tarefa em específico do trabalho para aquela máquina
            e para outros trabalhos pegamos o menor tempo possível para cada máquina. Resulta que é algo otimista.
            
            Para cada máquina k:
                LBk = Max(Pik) + Soma(Min(Pij)) para j ≠ k
            
            O menor LB entre todos representa o limite inferior mais realista para o makespan.
        """
        matriz = np.array(self.tempos_trabalhos)
        maquinas = matriz.T
        
        gargalos = []
        for k in range(self.m):
            max_k = maquinas[k].max()
            
            soma_outros = sum(
                maquinas[j].min() 
                for j in range(self.m) 
                if j != k
            )
            
            LBk = max_k + soma_outros
            gargalos.append(LBk)
        
        return gargalos, min(gargalos)
    
    def calcular_lower_bound_parcial(self, sequencia_parcial, trabalhos_restantes):
        """
            Função 'calcular_lower_bound_parcial' calcula o lower bound para um escalonamento parcial.
            
            Utilizada no algoritmo Branch and Bound para estimar o makespan de sequências incompletas.
            
            Três cenários:
            1. Sem trabalhos restantes: retorna o makespan da sequência completa
            2. Sequência vazia (Jr = ∅): calcula LB usando apenas trabalhos restantes Jr'
            3. Sequência parcial Jr + trabalhos restantes Jr': makespan(Jr) + estimativa(Jr')
            
            Parâmetros:
                - sequencia_parcial: lista de trabalhos já escalados (Jr)
                - trabalhos_restantes: lista de trabalhos ainda não escalados (Jr')
            
            Retorna o lower bound estimado para completar o escalonamento.
        """
        # Condicional pra sequências vazias e calculo de LB apenas com trabalhos restantes
        if not trabalhos_restantes:
            if not sequencia_parcial:
                return 0
            return self.calcular_makespan(sequencia_parcial)
        
        # Sequência vazia... mas ainda há trabalhos restantes
        if not sequencia_parcial:
            tempos_restantes = [self.tempos_trabalhos[t] for t in trabalhos_restantes]
            matriz_restantes = np.array(tempos_restantes).T

            gargalos_restantes = []

            for k in range(self.m):
                max_k = matriz_restantes[k].max()
                soma_outros = sum(
                    matriz_restantes[j].min() 
                    for j in range(self.m) 
                    if j != k
                )
                gargalos_restantes.append(max_k + soma_outros)

            return min(gargalos_restantes)
        
        # Rock n' roll, temos tudo muchacho!
        else:
            makespan_parcial = self.calcular_makespan(sequencia_parcial)

            estimativa_restantes = sum(
                min(self.tempos_trabalhos[t]) for t in trabalhos_restantes
            )

            return makespan_parcial + estimativa_restantes


    def branch_and_bound(self):
        """
            Função 'branch_and_bound' implementa o algoritmo Branch and Bound para encontrar a sequência ótima S0.
            
            Algoritmo baseado no artigo:
            1. Começo
            2. Entradas (tempos de processamento)
            3. Summation do processamento para cada máquina
            4. Lower bound inicial
            5. Escolha o lower bound alvo
            6. Crie uma branch para cada trabalho (ramificação)
            7. Repita 4,5 (calcule LB para cada branch)
            8. Escolha o menor lower bound para todos os trabalhos
            9. Se o menor LB não for mais um → procure o maior lb que está mais perto nos trabalhos selecionados
            11. Selecione o menor trabalho lb
            12. Repita os passos 7 ao 11
            13. Pare (quando encontrar S0)
            
            Estratégia:
            - Explora a árvore de decisão de forma sistemática
            - Poda (bound): descarta branches com LB >= melhor solução conhecida
            - Ramificação (branch): cria subproblemas para cada trabalho não escalado
            
            Retorna: (melhor_sequencia, melhor_makespan)
        """
        # TO-DO
        pass

    # def busca_tabu(self):
    #   Essa aqui é como dizia a Banda Catedral...
    #  "Sabe lá... sabe lá... 
    #   -- TO-DO (Será mesmo?) --
    #   Sabe lá... sabe lá..."
    

    




