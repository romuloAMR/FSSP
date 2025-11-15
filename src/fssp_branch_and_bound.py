import numpy as np

class FsspSolver:
    def __init__(self, num_trabalhos: int, num_maquinas: int, tempos_trabalhos: list[list] | np.ndarray) -> None:
        """
            Classe FsspSolver para o Flow-shop Scheduling Problem (FSSP).
            A classe é uma abstração do desenvolvimento apresentado no artigo, diferenciando que temos uma generalização
            para m máquinas e n trabalhos.

            Como parametros temos:
                - tempos_trabalhos: matriz de tempos de processamento dos trabalhos em cada máquina
                - num_trabalhos: número de trabalhos (linhas)
                - num_maquinas: número de máquinas (colunas)
        """
        self.tempos_trabalhos = np.array(tempos_trabalhos)
        self.n = num_trabalhos
        self.m = num_maquinas
        self.melhor_ub = float("inf")
        self.melhor_seq = []

    def _calcular_makespan(self, sequencia: list) -> float:
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
        m = self.m
        C = np.zeros((n, m))
        
        C[0, 0] = self.tempos_trabalhos[sequencia[0], 0]
        for j in range(1, m):
            C[0, j] = C[0, j-1] + self.tempos_trabalhos[sequencia[0], j]
        
        for i in range(1, n):
            trabalho = sequencia[i]
            C[i, 0] = C[i-1, 0] + self.tempos_trabalhos[trabalho, 0]
            for j in range(1, m):
                C[i, j] = max(C[i-1, j], C[i, j-1]) + self.tempos_trabalhos[trabalho, j]
        
        return C[n-1, m-1]

    def _calcular_gargalos(self, matriz:np.ndarray | None = None) -> tuple[list[float], float]:
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
        matriz = self.tempos_trabalhos.copy() if matriz is None else matriz
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
    
    def _calcular_lower_bound_parcial(self, sequencia_parcial: list, trabalhos_restantes: list) -> float:
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
            return self._calcular_makespan(sequencia_parcial)
        
        # Sequência vazia... mas ainda há trabalhos restantes
        if not sequencia_parcial:
            tempos_restantes = [self.tempos_trabalhos[t] for t in trabalhos_restantes]
            matriz_restantes = np.array(tempos_restantes)
            
            _, min_lb = self._calcular_gargalos(matriz_restantes)
            
            return min_lb
        
        # Rock n' roll, temos tudo muchacho!
        else:
            makespan_parcial = self._calcular_makespan(sequencia_parcial)

            estimativa_restantes = sum(
                min(self.tempos_trabalhos[t]) for t in trabalhos_restantes
            )

            return makespan_parcial + estimativa_restantes

    def _branch_and_bound(self, seq_atual: list, trabalhos_restantes: list) -> None:
        # Folha
        if not trabalhos_restantes:
            makespan_atual = self._calcular_makespan(seq_atual)
            
            if makespan_atual < self.melhor_ub:
                self.melhor_ub = makespan_atual
                self.melhor_seq = seq_atual
                
            return

        # Nó
        for trabalho in trabalhos_restantes:
            
            seq_novo = seq_atual + [trabalho]
            
            novo_trabalhos_restantes = trabalhos_restantes.copy()
            novo_trabalhos_restantes.remove(trabalho)
            
            lb_parcial = self._calcular_lower_bound_parcial(seq_novo, novo_trabalhos_restantes)
            
            if lb_parcial < self.melhor_ub:
                self._branch_and_bound(seq_novo, novo_trabalhos_restantes)

    def run(self) -> tuple[list, float]:
        todos_trabalhos = [i for i in range(self.n)]
        self.melhor_ub = self._calcular_makespan(todos_trabalhos)
        self.melhor_seq = todos_trabalhos

        self._branch_and_bound(seq_atual=[], trabalhos_restantes=todos_trabalhos)

        return self.melhor_seq, self.melhor_ub


if __name__ == "__main__":
    '''Teste do algoritmo'''

    nome = "Teste"
    num_trabalhos = 3
    num_maquinas = 3
    tempos_de_trabalho = [
        [3, 5, 4],
        [1, 2, 3],
        [5, 3, 1],
    ]
    
    print(f"Nome: {nome}")
    print(f"Trabalhos: {num_trabalhos}")
    print(f"Maquinas: {num_maquinas}")
    print("Matriz:")
    for linha in tempos_de_trabalho:
        linha_formatada = " ".join(f"{elem:>6}" for elem in linha)
        print(linha_formatada)

    solver = FsspSolver(num_maquinas, num_trabalhos, tempos_de_trabalho)
    seq = [0,1,2]
    print(f"MakeSpan de {seq}: {solver._calcular_makespan(seq)}")
    seq = [0,2,1]
    print(f"MakeSpan de {seq}: {solver._calcular_makespan(seq)}")
    seq = [1,0,2]
    print(f"MakeSpan de {seq}: {solver._calcular_makespan(seq)}")
    seq = [1,2,0]
    print(f"MakeSpan de {seq}: {solver._calcular_makespan(seq)}")
    seq = [2,0,1]
    print(f"MakeSpan de {seq}: {solver._calcular_makespan(seq)}")
    seq = [2,1,0]
    print(f"MakeSpan de {seq}: {solver._calcular_makespan(seq)}")
    seq_solucao, makespan_solucao = solver.run()
    print(f"Resposta {seq_solucao}: {makespan_solucao}")