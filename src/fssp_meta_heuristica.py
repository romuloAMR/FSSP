import numpy as np

class FsspSolver:
    def __init__(self, num_trabalhos: int, num_maquinas: int, tempos_trabalhos: list[list] | np.ndarray) -> None:
        """
            Classe FsspSolver para o Flow-shop Scheduling Problem (FSSP).

            Como parametros temos:
                - tempos_trabalhos: matriz de tempos de processamento dos trabalhos em cada máquina
                - num_trabalhos: número de trabalhos (linhas)
                - num_maquinas: número de máquinas (colunas)
        """
        self.tempos_trabalhos = np.array(tempos_trabalhos)
        self.n = num_trabalhos
        self.m = num_maquinas
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

    def _custo_tarefa(self, tarefa: list[float]) -> float:
        """
        Função para calcular o tempo total de uma tarefa isoladamente.
        """
        return sum(tarefa)

    def _solucao_inicial(self) -> list:
        """
        Solução inicial usando NEH para gerar a solução inicial do FSSP
        """
        if self.n <= 1:
            return list(range(self.n))

        trabalhos_ordenados = sorted(
            [(i, sum(self.tempos_trabalhos[i])) for i in range(self.n)],
            key=lambda x: x[1],
            reverse=True
        )

        indices_ordenados = [trabalho[0] for trabalho in trabalhos_ordenados]

        solucao = [indices_ordenados[0]]

        for i in range(1, self.n):
            trabalho_atual = indices_ordenados[i]
            melhor_insercao = None
            menor_makespan = float('inf')
            
            for posicao in range(len(solucao) + 1):
                solucao_teste = solucao.copy()
                solucao_teste.insert(posicao, trabalho_atual)

                makespan_teste = self._calcular_makespan(solucao_teste)

                if makespan_teste < menor_makespan:
                    menor_makespan = makespan_teste
                    melhor_insercao = solucao_teste

            solucao = melhor_insercao

        return solucao

    def run(self) -> tuple[list, float]:
        solucao = self._solucao_inicial()
        return solucao, self._calcular_makespan(solucao)


if __name__ == "__main__":
    """Teste do algoritmo"""

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

    solver = FsspSolver(num_trabalhos, num_maquinas, tempos_de_trabalho)

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