# Desenho de Experimento A/B: Validação da Inteligência de Escolha

O desenvolvimento de um modelo de score baseado em evidências (Logistic Regression, Decaimento Temporal e Exclusividade) requer validação empírica rigorosa antes do rollout completo. Apenas assim podemos afirmar que a solução entrega valor em produção.

---

## 1. Hipóteses

- **Hipótese Nula ($H_0$):** A nova estratégia de priorização (Score Baseado em Dados) **não** aumenta a taxa de entrega em relação à estratégia atual de envio.
- **Hipótese Alternativa ($H_1$):** A nova estratégia de Score aumenta significativamente a taxa de entrega (DELIVERED) por CPF **e** reduz o custo por cidadão alcançado.

---

## 2. Unidade Experimental e Divisão

- **Unidade:** **CPF (Cidadão)**. É fundamental randomizar o teste por CPF e não por telefone. Isso evita **contaminação**: o mesmo cidadão receber mensagens de grupos diferentes sujaria a métrica de eficácia.
- **Divisão (Split):** 50% Grupo Controle / 50% Grupo Tratamento.

---

## 3. Os Grupos

- **Grupo Controle (A):** Disparo realizado utilizando a regra atual da Prefeitura (aleatória ou alfabética, até 2 telefones por CPF).
- **Grupo Tratamento (B):** Disparo realizado apenas para o *Top 2 telefones* definidos pelo nosso novo Algoritmo de Score Empírico.

---

## 4. Métricas de Avaliação

- **Métrica Primária:**
  - *Taxa de Alcance por Cidadão:* `(CPFs com ≥1 msg DELIVERED)` / `(Total de CPFs acionados)`.
- **Métricas Secundárias:**
  - *Custo por Cidadão Alcançado:* `Custo Total` / `CPFs Alcançados`.
  - *Taxa de Falhas (FAILED):* Medir a redução de disparos perdidos em números inativos ou inválidos.
  - *Quantidade Média de Tentativas por CPF:* Espera-se redução nas tentativas mantendo ou subindo o alcance.

---

## 5. Duração e Tamanho da Amostra

- **Duração Estimada:** Pelo menos 1 ciclo completo de operações (2 a 4 semanas), evitando vieses de sazonalidade semanal ou feriados locais.

### Cálculo Formal do Tamanho de Amostra (Power Analysis)

Com base nas métricas históricas observadas na base de disparos:

| Parâmetro | Valor | Fonte |
|---|---|---|
| Taxa de alcance atual (controle, $p_0$) | ≈ 32,7% | Menor taxa empírica observada na base |
| Lift mínimo detectável | 10% relativo → $p_1$ ≈ 35,97% | Efeito mínimo com impacto de negócio |
| Nível de significância ($\alpha$) | 0,05 (bicaudal) | Padrão científico |
| Poder estatístico ($1-\beta$) | 0,80 | Padrão científico |

```python
from statsmodels.stats.proportion import proportion_effectsize
from statsmodels.stats.power import NormalIndPower

p0 = 0.327   # taxa de entrega atual (baseline)
p1 = 0.360   # taxa alvo (lift de ~10% relativo)

effect_size = proportion_effectsize(p1, p0)  # Cohen's h

analise = NormalIndPower()
n_por_grupo = analise.solve_power(
    effect_size=effect_size,
    alpha=0.05,
    power=0.80,
    alternative='two-sided'
)

print(f"Effect size (Cohen's h): {effect_size:.4f}")
print(f"N mínimo por grupo     : {n_por_grupo:.0f} cidadãos")
print(f"N total do experimento : {n_por_grupo * 2:.0f} cidadãos")
```

**Resultado calculado:**
```
Effect size (Cohen's h): ~0.069
N mínimo por grupo     : ~1.650 cidadãos
N total do experimento : ~3.300 cidadãos
```

> Com o volume de dados da Prefeitura do Rio (~510 mil cidadãos na base ativa), o tamanho mínimo de **3.300 cidadãos** é atingido em **menos de 1 dia** de operação. O período de 2 a 4 semanas é adotado para controle de sazonalidade, não por limitação de volume.

### Distribuição da Amostra por Estrato

Para garantir representatividade, a amostragem deve ser **estratificada** por:
- DDD (Rio 21 vs. outros DDDs)
- Fonte de origem do telefone (id_sistema)
- Faixa de recência do dado (0–30d, 31–180d, >180d)

---

## 6. Critérios de Parada Antecipada

| Critério | Ação |
|---|---|
| Efeito adverso: taxa de falha do grupo B > grupo A por mais de 3 dias consecutivos | Interromper e reverter |
| Significância estatística atingida antes do prazo | Continuar pelo período mínimo de sazonalidade |
| Diferença < 1% após 4 semanas | Concluir ausência de efeito prático |

---

## 7. Análise Pós-Experimento

```python
from scipy.stats import chi2_contingency
import numpy as np

# Tabela de contingência: [alcancados, nao_alcancados] por grupo
tabela = np.array([
    [alcancados_controle,    nao_alcancados_controle],
    [alcancados_tratamento,  nao_alcancados_tratamento]
])

chi2, p_valor, dof, expected = chi2_contingency(tabela)
lift_relativo = (taxa_tratamento - taxa_controle) / taxa_controle * 100

print(f"p-valor         : {p_valor:.4f}")
print(f"Resultado       : {'REJEITAR H0' if p_valor < 0.05 else 'NÃO rejeitar H0'}")
print(f"Lift relativo   : {lift_relativo:.1f}%")
print(f"ROI estimado    : economia de {mensagens_evitadas} disparos/campanha")
```
