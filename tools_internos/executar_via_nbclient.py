# -*- coding: utf-8 -*-
"""
Executa notebooks individualmente via nbclient (sem bug de path duplicado do nbconvert).
Salva os outputs in-place no proprio arquivo .ipynb.
"""
import nbformat
import nbclient
import os
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)

NOTEBOOKS = [
    "notebooks/01_carga_modelagem.ipynb",
    "notebooks/02_analise_performance.ipynb",
    "notebooks/03_decaimento_temporal.ipynb",
    "notebooks/04_algoritmo_final.ipynb",
]

SEPARADOR = "=" * 60

def executar_e_salvar(caminho_nb):
    """Executa o notebook e salva outputs in-place."""
    nome = os.path.basename(caminho_nb)
    abs_path = os.path.abspath(caminho_nb)
    nb_dir  = os.path.dirname(abs_path)

    print(f"\n  Executando: {nome}")
    inicio = time.time()

    with open(abs_path, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    client = nbclient.NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": nb_dir}},
    )

    try:
        client.execute()
        duracao = time.time() - inicio

        # Salva o notebook com os outputs preenchidos
        with open(abs_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

        # Conta outputs gerados
        total_outputs = sum(len(c.outputs) for c in nb.cells if c.cell_type == "code")
        print(f"  [OK] Concluido em {duracao:.1f}s | {total_outputs} outputs gerados")
        return True

    except Exception as e:
        duracao = time.time() - inicio
        print(f"  [ERRO] Falhou em {duracao:.1f}s")
        # Salva o notebook mesmo com erro (outputs parciais)
        with open(abs_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)
        msg = str(e)
        # Mostra apenas a parte relevante do traceback
        linhas = [l for l in msg.split("\n") if l.strip()]
        for l in linhas[-4:]:
            print(f"    {l}")
        return False

# Execucao
print(f"\n{SEPARADOR}")
print("  Executando notebooks via nbclient (outputs salvos in-place)")
print(SEPARADOR)

resultados = {}
for nb_path in NOTEBOOKS:
    ok = executar_e_salvar(nb_path)
    resultados[nb_path] = ok

# Relatorio
print(f"\n{SEPARADOR}")
print("  RELATORIO FINAL")
print(SEPARADOR)
for nb_path, ok in resultados.items():
    tag = "[OK]     " if ok else "[FALHOU]"
    print(f"  {tag}  {os.path.basename(nb_path)}")

total_ok = sum(resultados.values())
print(f"\n  {total_ok}/{len(NOTEBOOKS)} notebooks com outputs salvos com sucesso.")
if total_ok == len(NOTEBOOKS):
    print("  Todos os notebooks prontos para o GitHub!")
print(SEPARADOR)
