# Inteligência de Escolha: Prioridade de Telefones (Squad WhatsApp - PCRJ)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Statsmodels](https://img.shields.io/badge/statsmodels-blue?style=for-the-badge)
![LGPD](https://img.shields.io/badge/Compliance-LGPD-green?style=for-the-badge)

Motor de priorização de telefones orientado por evidências estatísticas, construído para responder à pergunta central do desafio:

> **"O que define um telefone quente? Aquele que tem maior probabilidade de estar ativo, ser entregue e lido pelo cidadão correto."**

---

### Destaques do Impacto (ROI)
>
> [!IMPORTANT]
>
> * **Eficiência Operacional:** Redução de **91,8%** em redundâncias sistémicas.
> * **Alcance Preciso:** Média de **1,01 mensagens por CPF**, garantindo o máximo alcance com o mínimo custo.
> * **Economia Escalonável:** Eliminação de **~5,7 milhões de disparos** redundantes identificados na base histórica.

---

## Arquitetura do Score de Elite

A solução decompõe a definição de "telefone quente" em 3 dimensões mensuráveis e integradas:

| Dimensão | Componente do Score | Peso | Razão Estatística e de Negócio |
| :--- | :--- | :--- | :--- |
| **Estar Ativo** | Taxa de Entrega Empírica (`id_sistema`) | **50%** | Maior coeficiente no modelo Logit; reflete a performance real da fonte. |
| **Ser Entregue** | Fator de Recência (Decaimento) | **25%** | Queda validada de performance após 180 dias de inatividade (NB03). |
| **Cidadão Correto** | Bônus DDD + Exclusividade | **25%** | **Pilar LGPD:** Garante que o chip pertence ao dono real do CPF. |

---

## Estrutura do Repositório

```
Inteligencia-Escolha-WhatsApp/
├── data/                                 # Armazenamento de dados (IGNORADOS NO GIT)
│   ├── whatsapp_base_disparo_mascarado/  # Fonte bruta: Histórico de performance
│   └── whatsapp_dim_telefone_mascarado/  # Fonte bruta: Dimensão RMI (Cadastro)
│
├── notebooks/                            # Fluxo lógico da análise (notebooks executados com outputs)
│   ├── 01_carga_modelagem.ipynb          # Join Real, tipagem segura e limpeza inicial
│   ├── 02_analise_performance.ipynb      # Taxas de entrega e Regressão Logística (controle de viés)
│   ├── 03_decaimento_temporal.ipynb      # Estudo da "meia-vida" do dado e recência
│   └── 04_algoritmo_final.ipynb          # Motor de Score e geração da lista Top 2 por CPF
│
├── tools_internos/                       # Scripts de suporte e automação
│   └── executar_via_nbclient.py          # Reexecução em lote dos notebooks (headless)
│
├── docs/                                 # Documentação suplementar
│   └── imagens/                          # Gráficos e capturas de tela dos resultados
│
├── 05_ab_test_design.md                  # Planejamento do Experimento (Power Analysis)
├── whatsapp_schema.yml                   # Dicionário de dados alinhado ao dbt
├── requirements.txt                      # Bibliotecas necessárias (pandas, statsmodels, etc.)
├── .gitignore                            # Proteção para não subir a pasta /data/
└── README.md                             # O guia mestre do projeto
```

| Arquivo / Pasta | Papel no desafio |
| :--- | :--- |
| `notebooks/01_carga_modelagem.ipynb` | Engenharia de dados — Join real (6,2M registros), tipagem segura |
| `notebooks/02_analise_performance.ipynb` | **Parte 1A** — Taxas DELIVERED por sistema + Regressão Logística (viés) |
| `notebooks/03_decaimento_temporal.ipynb` | **Parte 1B** — Decaimento temporal, cutoff operacional de 180 dias |
| `notebooks/04_algoritmo_final.ipynb` | **Parte 2** — Score final + seleção Top 2 por CPF |
| `05_ab_test_design.md` | **Parte 3** — Desenho A/B com Power Analysis numérico |
| `whatsapp_schema.yml` | Dicionário de dados (formato dbt) |
| `requirements.txt` | Reprodutibilidade do ambiente |
| `.gitignore` | Protege dados sensíveis (LGPD) e arquivos grandes |

---

## Origem e Gestão dos Dados

* **Fontes Externas:** Os dados brutos foram extraídos do bucket GCS oficial da PCRJ.
* **Ingestão Local:** Os ficheiros parquet devem ser posicionados no diretório `/data` seguindo o esquema definido no `whatsapp_schema.yml`.
* **Camada de Trusted:** Através do notebook `01_carga_modelagem.ipynb`, é gerada a **Tabela Mestra de Performance**, consolidando o histórico de disparos e o cadastro dimensional.

---

## Ciência de Dados Aplicada

### Controle de Viés via Regressão Logística

Utilizámos o modelo `statsmodels.logit` para isolar a performance real de cada sistema. Confirmámos que o `id_sistema` possui **P-valor < 0,05**, validando que a origem do dado é um preditor independente de qualidade, e não apenas ruído de volume.

### Higienização e LGPD

* **Filtro de Outliers:** Foram removidos números com `> 5 proprietários` (evitando telefones comerciais ou institucionais).
* **Foco no Proprietário:** O Score prioriza o vínculo exclusivo entre CPF e Telefone (exclusividade), minimizando o risco de entrega de dados sensíveis a terceiros.

---

## Desenho de Experimento (A/B Test)

* **Unidade de Randomização:** CPF (evita contaminação entre grupos).
* **Hipótese:** O novo score aumenta a taxa de alcance por cidadão (Reach Rate) vs. a estratégia atual.
* **Tamanho da Amostra:** Calculados **~1.650 cidadãos por grupo** para detectar um lift de 5% com 80% de poder estatístico ($\alpha=0,05$).

---

## Como Reproduzir

1. **Dados:** Coloque os ficheiros parquet na pasta `data/` com os nomes originais.
2. **Ambiente:**

    ```bash
    pip install pandas numpy seaborn matplotlib statsmodels pyarrow nbclient
    ```

3. **Execução:** Os notebooks já contêm os **outputs salvos**. Para reprocessar, execute os ficheiros na ordem numérica de 01 a 04.

---

**Cientista de Dados:** Jhones Sena  
**Squad WhatsApp — Prefeitura do Rio de Janeiro**
