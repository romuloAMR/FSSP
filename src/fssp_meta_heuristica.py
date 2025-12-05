import numpy as np
import random

class FsspSolver:
    def __init__(self, num_trabalhos: int, num_maquinas: int, tempos_trabalhos: list[list[float]] | np.ndarray) -> None:
        """
        Inicializa o solver do problema Flow-shop Scheduling.

        Args:
            num_trabalhos: Número de trabalhos (linhas).
            num_maquinas: Número de máquinas (colunas).
            tempos_trabalhos: Matriz de tempos de processamento dos trabalhos em cada máquina.

        Attributes:
            tempos_trabalhos: Matriz numpy com tempos de processamento.
            n: Número de trabalhos.
            m: Número de máquinas.
            melhor_seq: Lista para armazenar a melhor sequência encontrada.
        """
        self.tempos_trabalhos = np.array(tempos_trabalhos)
        self.n = num_trabalhos
        self.m = num_maquinas
        self.melhor_seq = []

    def _calcular_makespan(self, sequencia: list[int]) -> float:
        """
        Calcula o makespan (tempo total de conclusão) para uma dada sequência de trabalhos.

        O cálculo segue a lógica de programação dinâmica considerando as restrições:
        - Nenhuma ultrapassagem é permitida (ordem é mantida)
        - Cada operação, uma vez iniciada, tem que ser concluída
        - Um trabalho não pode ser processado por mais de uma máquina ao mesmo tempo

        Args:
            sequencia: Lista de índices representando a sequência de trabalhos.

        Returns:
            float: Valor do makespan (tempo total de conclusão).
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

    def _solucao_inicial(self) -> list[int]:
        """
        Gera solução inicial usando o algoritmo NEH (Nawaz-Enscore-Ham).

        O algoritmo NEH:
        1. Ordena trabalhos por tempo total de processamento decrescente
        2. Insere iterativamente cada trabalho na posição que minimiza o makespan

        Returns:
            list[int]: Sequência de trabalhos gerada pelo NEH.
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
    
    def _gerar_populacao(self, tamanho_populacao: int = 2) -> list[list[int]]:
        """
        Gera população inicial para algoritmos genéticos.

        Args:
            tamanho_populacao: Tamanho da população a ser gerada.

        Returns:
            list[list[int]]: Lista contendo os indivíduos da população.
        """
        populacao = []
        populacao.append(self._solucao_inicial())

        for _ in range(tamanho_populacao - 1):
            individuo = list(range(self.n))
            random.shuffle(individuo)
            populacao.append(individuo)
        return populacao
    
    def _calcular_aptidao(self, individuo: list[int]) -> float:
        """
        Calcula a aptidão (fitness) de um indivíduo.

        Nota: Quanto menor o makespan, maior a aptidão. O valor negativo é usado
        para permitir maximização com makespan minimizado.

        Args:
            individuo: Sequência de trabalhos representando um indivíduo.

        Returns:
            float: Valor de aptidão (makespan negativo).
        """
        return -self._calcular_makespan(individuo)
    
    def _torneio(self, populacao: list[list[int]], k: int = 3) -> list[int]:
        """
        Seleção por torneio.

        Args:
            populacao: População atual.
            k: Número de candidatos no torneio.

        Returns:
            list[int]: Melhor indivíduo selecionado no torneio.
        """
        candidatos = random.sample(populacao, k)
        melhor = max(candidatos, key=lambda ind: self._calcular_aptidao(ind))
        return melhor

    def _selecionar_pais(self, populacao: list[list[int]], num_pares: int) -> list[tuple[list[int]]]:
        """
        Seleciona pares de pais para cruzamento.

        Args:
            populacao: População atual.
            num_pares: Número de pares de pais a selecionar.

        Returns:
            list[tuple[list[int]]]: Lista de pares de pais.
        """
        pais = []
        for _ in range(num_pares):
            p1 = self._torneio(populacao)
            p2 = self._torneio(populacao)
            pais.append((p1,p2))
        return pais

    def _ox2(self, genitor1: list[int], genitor2: list[int]) -> list[int]:
        """
        Realiza o cruzamento Order Crossover 2 (OX2).

        O operador OX2 seleciona um subconjunto de genes do genitor2 e impõe
        a ordem relativa desses genes nas posições correspondentes do genitor1.
        Isso preserva a estrutura de posições do genitor1, mas injeta a
        sequência relativa do genitor2.

        Args:
            genitor1: O cromossomo base que fornece as posições (slots).
            genitor2: O cromossomo doador que fornece a ordem relativa.

        Returns:
            list[int]: Um novo cromossomo (filho) resultante da recombinação.
        """
        tamanho = len(genitor1)
        k = random.randint(1, tamanho - 1)
        indices_troca = sorted(random.sample(range(tamanho), k))
        valores_selecionados = [genitor2[i] for i in indices_troca]
        posicoes_no_genitor1 = sorted([genitor1.index(v) for v in valores_selecionados])
        filho = genitor1.copy()
        for pos, val in zip(posicoes_no_genitor1, valores_selecionados):
            filho[pos] = val

        return filho
    
    def _recombinar(self, pais: list[tuple[list[int]]], taxa_crossover: float) -> list[list[int]]:
        """
        Realiza cruzamento entre pares de pais.

        Args:
            pais: Lista de pares de pais.
            taxa_crossover: Probabilidade de ocorrer cruzamento.

        Returns:
            list[list[int]]: Lista de filhos gerados.
        """
        filhos = []
        for p1, p2 in pais:
            if random.random() < taxa_crossover:
                f1 = self._ox2(p1, p2)
                f2 = self._ox2(p2, p1)
            else:
                f1 = p1.copy()
                f2 = p2.copy()
            filhos.append(f1)
            filhos.append(f2)
        return filhos
    
    def _mutagenico(self, individuo: list[int]) -> list[int]:
        """
        Aplica operador de mutação por inserção.

        Remove um gene em posição aleatória e insere em outra posição aleatória.

        Args:
            individuo: Indivíduo a ser mutado.

        Returns:
            list[int]: Indivíduo mutado.
        """
        array = individuo[:]
        l = len(array)
        if l < 2: return array

        r1 = random.randrange(l)
        r2 = random.randrange(l)
        
        while r1 == r2:
            r2 = random.randrange(l)

        gene = array.pop(r1)
        array.insert(r2, gene)

        return array

    def _renovar(
            self,
            populacao_atual: list[list[int]],
            nova_geracao: list[list[int]],
            tamanho_populacao: int
    ) -> list[list[int]]:
        """
        Realiza substituição geracional com elitismo.

        Combina população atual com nova geração e seleciona os melhores.

        Args:
            populacao_atual: População atual.
            nova_geracao: Nova geração gerada.
            tamanho_populacao: Tamanho final da população.

        Returns:
            list[list[int]]: Nova população selecionada.
        """
        populacao = populacao_atual + nova_geracao
        populacao.sort(key=lambda ind: self._calcular_aptidao(ind), reverse=True)
        return populacao[:tamanho_populacao]
    
    def _algoritmo_genetico(
            self, 
            tamanho_populacao: int = 20,
            numero_geracoes: int = 50,
            taxa_crossover: float = 0.8,
            taxa_mutacao: float = 0.2,
            com_busca_local: bool = False
    ) -> tuple[list[int], float]:
        """
        Executa algoritmo genético para o problema FSSP.

        Args:
            tamanho_populacao: Tamanho da população.
            numero_geracoes: Número de gerações a executar.
            taxa_crossover: Probabilidade de cruzamento.
            taxa_mutacao: Probabilidade de mutação.
            com_busca_local: Se True, aplica busca local (algoritmo memético).

        Returns:
            tuple[list[int], float]: Melhor solução encontrada e seu makespan.

        Raises:
            ValueError: Se tamanho_populacao for menor que 2.
        """
        if tamanho_populacao < 2:
            raise ValueError("População deve ser >= 2")
        
        populacao = self._gerar_populacao(tamanho_populacao)
        melhor_solucao_global = None
        melhor_makespan_global = float('inf')
        
        for _ in range(numero_geracoes):
            
            # Avaliação e Melhor Global
            for individuo in populacao:
                ms = self._calcular_makespan(individuo)
                if ms < melhor_makespan_global:
                    melhor_makespan_global = ms
                    melhor_solucao_global = individuo.copy()

            # Seleção de Pais
            num_pares = tamanho_populacao // 2
            pais = self._selecionar_pais(populacao, num_pares)
            
            # Crossover
            filhos = self._recombinar(pais, taxa_crossover)
            
            # Mutação
            for i in range(len(filhos)):
                if random.random() < taxa_mutacao:
                    filhos[i] = self._mutagenico(filhos[i])

            # Busca Local (Memético)
            if com_busca_local:
                for i in range(len(filhos)):
                    if random.random() < 0.2:
                        #filhos[i] = self._busca_local(filhos[i])
            
            # 6. Sobrevivência (Renovação)
            populacao = self._renovar(populacao, filhos, tamanho_populacao)

        return melhor_solucao_global, melhor_makespan_global

    def run(self, metodo: str = "neh") -> tuple[list, float]:
        """
        Método principal para executar diferentes algoritmos de resolução.

        Args:
            metodo: Algoritmo a ser executado ('neh', 'genetico' ou 'memetico').

        Returns:
            tuple[list, float]: Sequência de trabalhos e makespan correspondente.

        Raises:
            ValueError: Se método não for reconhecido.
        """
        if metodo == "neh":
            solucao = self._solucao_inicial()
            return solucao, self._calcular_makespan(solucao)
        elif metodo == "genetico":
            return self._algoritmo_genetico(com_busca_local=False)
        elif metodo == "memetico":
            return self._algoritmo_genetico(com_busca_local=True)
        else:
            raise ValueError("Método deve ser 'neh', 'genetico' ou 'memetico'")

if __name__ == "__main__":
    """Teste do algoritmo"""
    from fssp_branch_and_bound import FsspSolverExato

    nome = "Teste"
    num_trabalhos = 5
    num_maquinas = 3
    tempos_de_trabalho = [
        [3, 5, 4],
        [1, 2, 3],
        [5, 3, 1],
        [6, 1, 2],
        [2, 4, 3]
    ]
    
    solver_exato = FsspSolverExato(num_trabalhos, num_maquinas, tempos_de_trabalho)
    solver = FsspSolver(num_trabalhos, num_maquinas, tempos_de_trabalho)

    print("--- Exato ---")
    seq_exato, ms_exato = solver_exato.run()
    print(f"Solução: {seq_exato} | Makespan: {ms_exato}")

    print("\n--- NEH ---")
    seq_neh, ms_neh = solver.run("neh")
    print(f"Solução: {seq_neh} | Makespan: {ms_neh}")

    print("\n--- Genético ---")
    seq_ga, ms_ga = solver.run("genetico")
    print(f"Solução: {seq_ga} | Makespan: {ms_ga}")

    print("\n--- Memético ---")
    seq_mem, ms_mem = solver.run("memetico")
    print(f"Solução: {seq_mem} | Makespan: {ms_mem}")