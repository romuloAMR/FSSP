import numpy as np
import random

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
    
    def _gerar_populacao(self, tamanho_populacao: int = 2) -> list[list]:
        populacao = []
        populacao.append(self._solucao_inicial())

        for _ in range(tamanho_populacao - 1):
            individuo = list(range(self.n))
            random.shuffle(individuo)
            populacao.append(individuo)

        return populacao
    
    def _calcular_aptidao(self, individuo: list[float]): # Segundo o framework de Silvia, isso aqui já seria papo de método de adequação
        """
        Calcular o quão apto é, quanto menor o makespan maior a aptidao.
        """
        return 1.0/self._calcular_makespan(individuo)
    
    def _torneio(self, populacao, k):
        candidatos = random.sample(populacao, k)
        melhor = max(candidatos, key=lambda ind: self._calcular_aptidao(ind))
        return melhor

    # Método para selecionar cromossomos para reproduzir
    def _reproduzir(self, populacao, num_filhos):
        pais = []
        for _ in range(num_filhos):
            p1 = self._torneio(populacao, k=3)
            p2 = self._torneio(populacao, k=3)
            pais.append((p1,p2))
        return pais

    def _ox2(self, parent1, parent2):
        size = len(parent1)
        k = random.randint(1, size - 1)
        swap_indexes = sorted(random.sample(range(size), k))
        selected_values = [parent2[i] for i in swap_indexes]
        positions = [parent1.index(v) for v in selected_values]
        child = parent1.copy()
        for pos, val in zip(positions, selected_values):
            child[pos] = val
        return child
    
    # Método para recombinar
    def _recombinar(self, pais):
        """Recebe lista de pares e retorna lista de filhos."""
        filhos = []
        for p1, p2 in pais:
            f1 = self._ox2(p1, p2)
            f2 = self._ox2(p2, p1)
            filhos.append(f1)
            filhos.append(f2)
        return filhos
    
    # Método para efetuar mutação
    def _mutagenico(self, individuo):
        array = individuo[:]
        l = len(array)

        r1 = random.randrange(l)
        r2 = random.randrange(l)
        while r1 == r2:
            r2 = random.randrange(l)

        if r1 > r2:
            r1, r2 = r2, r1

        gene = array[r2]
        for i in range(r2, r1, -1):
            array[i] = array[i - 1]
        
        array[r1] = gene

        return array


    def _renovar(self, parents, offspring, mu):
        # 2.2 Avaliar pais e filhos
        evaluated_parents = [(ind, self._calcular_aptidao(ind)) for ind in parents]
        evaluated_offspring = [(ind, self._calcular_aptidao(ind)) for ind in offspring]

        # 2.3 Combinar populações: R = P ∪ O
        combined = evaluated_parents + evaluated_offspring  # tamanho μ + λ

        # 2.4 Selecionar os melhores μ indivíduos
        combined.sort(key=lambda x: x[1], reverse=True)  # menor fitness primeiro (ou inverter se for maximização)
        survivors = [ind for ind, fit in combined[:mu]]

        # 2.5 Retorna os μ sobreviventes
        return survivors
    
    def _algoritmo_genetico(
            self, 
            tamanho_populacao: int = 50,
            numero_geracoes: int = 100,
            taxa_crossover: float = 0.8,
            taxa_mutacao: float = 0.1,
            com_busca_local: bool = False
    ) -> tuple[list, float]:
        #TODO: adicionar o doc string
        """
        Fazer
        """
        if tamanho_populacao < 2:
            raise ValueError("População deve ser >= 2!!!!!")
        
        populacao = self._gerar_populacao(tamanho_populacao)
        melhor_solucao = None
        melhor_makespan = float('inf')
        
        #TODO: Continuar
        for geracao in range(numero_geracoes):
            
            aptidoes_populacao_atual = [self._calcular_aptidao(individuo) for individuo in populacao]
            melhor_individuo = populacao[np.argmax(aptidoes_populacao_atual)]
            melhor_individuo_makespan = self._calcular_makespan(melhor_individuo)
            if melhor_individuo_makespan < melhor_makespan:
                melhor_solucao = melhor_individuo.copy()
                melhor_makespan = melhor_individuo_makespan
            
            nova_populacao = []

        return melhor_solucao, melhor_makespan

    def run(self, metodo: str = "neh") -> tuple[list, float]:
        """Método principal para executar diferentes algoritmos"""
        if metodo == "neh":
            solucao = self._solucao_inicial()
            return solucao, self._calcular_makespan(solucao)
        elif metodo == "genetico":
            return self._algoritmo_genetico()
        elif metodo == "memetico":
            return self._algoritmo_genetico(com_busca_local=True)
        else:
            raise ValueError("Método deve ser 'neh', 'genetico' ou 'memetico'")


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
