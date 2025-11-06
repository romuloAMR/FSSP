import json
import re

def analisar_arquivo_flowshop(conteudo_arquivo, NOME_ARQUIVO_SAIDA_JSON):
    """
    Analisa um arquivo de instâncias Flow Shop e extrai os dados para um JSON
    
    Args:
        conteudo_arquivo (str): Conteúdo do arquivo a ser analisado
        NOME_ARQUIVO_SAIDA_JSON (str): Nome do arquivo JSON de saída
    
    Returns:
        dict: Dados extraídos das instâncias
    """

    padrao_instancia = re.compile(r'\+\++\s*\n\s*instance\s+(\w+)\s*\n\s*\+{3,}', re.IGNORECASE)
    padrao_dimensoes = re.compile(r'^\s*(\d+)\s+(\d+)\s*$', re.MULTILINE)
    
    instancias = []
    partes = padrao_instancia.split(conteudo_arquivo)

    for i in range(1, len(partes), 2):
        if i + 1 < len(partes):
            nome_instancia = partes[i]
            conteudo_instancia = partes[i + 1]
            match_dimensoes = padrao_dimensoes.search(conteudo_instancia)
            if match_dimensoes:
                num_jobs = int(match_dimensoes.group(1))
                num_machines = int(match_dimensoes.group(2))
                
                tempos = extrair_tempos_processamento(conteudo_instancia, num_jobs, num_machines)
                
                if tempos:
                    instancia_data = {
                        "nome_instancia": nome_instancia,
                        "num_jobs": num_jobs,
                        "num_machines": num_machines,
                        "matriz_tempos": tempos
                    }
                    instancias.append(instancia_data)

    dados_finais = {
        "metadata": {
            "total_instancias": len(instancias),
            "tipo_problema": "Flow Shop Scheduling"
        },
        "instancias": instancias
    }
    
    with open(NOME_ARQUIVO_SAIDA_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados_finais, f, indent=2, ensure_ascii=False)
    
    return dados_finais

def extrair_tempos_processamento(conteudo_instancia, num_jobs, num_machines):
    """
    Extrai os tempos de processamento da instância
    
    Args:
        conteudo_instancia (str): Conteúdo da instância
        num_jobs (int): Número de jobs
        num_machines (int): Número de máquinas
    
    Returns:
        list: Matriz de tempos de processamento
    """
    linhas = conteudo_instancia.split('\n')
    tempos = []
    
    for linha in linhas:
        linha = linha.strip()
        
        if not linha or 'instance' in linha.lower() or '++++' in linha:
            continue
        
        if linha.startswith('0') or re.match(r'^\s*\d+\s+\d+', linha):
            numeros = re.findall(r'\d+', linha)
            
            if len(numeros) == num_machines * 2 + 1:
                job_tempos = []
                for j in range(1, len(numeros), 2):
                    if j + 1 < len(numeros):
                        job_tempos.append(int(numeros[j + 1]))
                
                if len(job_tempos) == num_machines:
                    tempos.append(job_tempos)
    
    if len(tempos) == num_jobs:
        return tempos
    else:
        return extrair_tempos_alternativo(conteudo_instancia, num_jobs, num_machines)

def extrair_tempos_alternativo(conteudo_instancia, num_jobs, num_machines):
    """
    Método alternativo para extrair tempos quando o padrão principal falha
    """
    linhas = conteudo_instancia.split('\n')
    comecou_dados = False
    numeros_tempos = []
    
    for linha in linhas:
        linha = linha.strip()
    
        if re.match(r'^\s*\d+\s+\d+\s*$', linha):
            comecou_dados = True
            continue
        
        if comecou_dados and linha:
            numeros_linha = re.findall(r'\b\d+\b', linha)
            if numeros_linha:
                for i in range(1, len(numeros_linha), 2):
                    if i < len(numeros_linha):
                        numeros_tempos.append(int(numeros_linha[i]))
    
    if len(numeros_tempos) == num_jobs * num_machines:
        tempos = []
        for i in range(num_jobs):
            inicio = i * num_machines
            fim = inicio + num_machines
            tempos.append(numeros_tempos[inicio:fim])
        return tempos
    
    return []

if __name__ == "__main__":

    with open('data/flowshop1.txt', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    resultado = analisar_arquivo_flowshop(conteudo, 'data/instancias.json')
    print(f"Processadas {resultado['metadata']['total_instancias']} instâncias")
    print(f"Dados salvos em 'instancias.json'")