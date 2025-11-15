import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("/workspaces/paa-projeto-3-1/data/resultados_refinados.csv")

df_agregado = (
    df.groupby("nome_instancia")
      .agg({
          "tempo": "mean",
          "makespan": "mean",
          "num_tarefas": "mean",
          "num_maquinas": "mean"
      })
      .rename(columns={
          "tempo": "tempo_medio",
          "makespan": "makespan_medio",
          "num_tarefas": "num_tarefas_media",
          "num_maquinas": "num_maquinas_media"
      })
      .reset_index()
)

# ================================
# |     Geração dos Gráficos     |
# ================================

# >>> Relação Razão (Tarefas/Máquinas) vs Tempo Médio
df_agregado["razao"] = df_agregado["num_tarefas_media"] / df_agregado["num_maquinas_media"]

plt.figure(figsize=(8,6))
plt.scatter(df_agregado["razao"], df_agregado["tempo_medio"], color="teal")
for _, row in df_agregado.iterrows():
    plt.text(row["razao"], row["tempo_medio"], row["nome_instancia"], fontsize=9, ha='right')
plt.title("Relação Razão (Tarefas/Máquinas) vs Tempo Médio")
plt.xlabel("Razão Tarefas/Máquinas")
plt.ylabel("Tempo Médio (s)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# >>> Tempo Médio por Instância (escala log)
df_sorted = df_agregado.sort_values("tempo_medio", ascending=False)

plt.figure(figsize=(10,6))
plt.bar(df_sorted["nome_instancia"], df_sorted["tempo_medio"], color="orange")
plt.yscale("log")
plt.title("Tempo Médio por Instância (Escala Logarítmica)")
plt.xlabel("Instância")
plt.ylabel("Tempo Médio (s)")
plt.grid(True, which="both", axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# >>> Relação Makespan Médio vs Tempo Médio
plt.figure(figsize=(8,6))
plt.scatter(df_agregado["makespan_medio"], df_agregado["tempo_medio"], color="purple")
for _, row in df_agregado.iterrows():
    plt.text(row["makespan_medio"], row["tempo_medio"], row["nome_instancia"], fontsize=9, ha='right')
plt.title("Relação Makespan Médio vs Tempo Médio")
plt.xlabel("Makespan Médio")
plt.ylabel("Tempo Médio (s)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# >>> Boxplot (car6 vs car8)
df_box = df[df["nome_instancia"].isin(["car6", "car8"])]

plt.figure(figsize=(8,6))
df_box.boxplot(column="tempo", by="nome_instancia", patch_artist=True,
               boxprops=dict(facecolor="lightblue", color="blue"),
               medianprops=dict(color="red", linewidth=2))
plt.title("Distribuição dos Tempos de Execução (car6 vs car8)")
plt.suptitle("")
plt.xlabel("Instância")
plt.ylabel("Tempo (s)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# >>> Relação Tarefas vs Máquinas
plt.figure(figsize=(8,6))
plt.scatter(df_agregado["num_maquinas_media"], df_agregado["num_tarefas_media"], color="green")
for _, row in df_agregado.iterrows():
    plt.text(row["num_maquinas_media"], row["num_tarefas_media"], row["nome_instancia"], fontsize=9, ha='right')
plt.title("Relação entre Número de Máquinas e Número de Tarefas")
plt.xlabel("Número Médio de Máquinas")
plt.ylabel("Número Médio de Tarefas")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()