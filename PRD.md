# Documento de Requisitos do Produto (PRD) - FitPlan

O **FitPlan** é um módulo simples e direto para cálculo de mensalidades de academia e classificação de planos, desenvolvido para a atividade prática de Qualidade e Teste de Software (QTS).

---

## 🎯 Do que se trata o projeto?

O objetivo do sistema é calcular quanto um aluno vai pagar na mensalidade da academia levando em conta dependentes e descontos, e depois indicar em qual categoria de plano ele se enquadra.

Toda a lógica fica concentrada na classe `AvaliadorAcademia` (dentro de `app/academia.py`), com dois métodos principais:

1. **`calcular_mensalidade`**: calcula o valor final da mensalidade.
2. **`determinar_categoria_plano`**: define se o aluno é Bronze, Prata ou Ouro de acordo com o valor calculado.

---

## 📋 Regras de Negócio

### 1. Cálculo da Mensalidade
* **Valor Base**: o valor da mensalidade do plano deve ficar entre **R$ 60,00** e **R$ 1.000,00**.
* **Dependentes**: o titular pode incluir de **0 a 5 dependentes**. Cada dependente adiciona um custo fixo (o padrão é R$ 50,00 por pessoa).
* **Cupom de Desconto**: pode ser aplicado um cupom percentual de **0% a 50%** sobre o valor total da mensalidade.
* **Cálculo**: soma-se o valor base com o custo dos dependentes e, sobre esse total, aplica-se o desconto do cupom.

### 2. Categorias dos Planos
Com base na mensalidade final, o sistema classifica o plano do aluno:
* **Plano Bronze**: mensalidades de **R$ 60,00** até **R$ 119,99**.
* **Plano Prata**: mensalidades de **R$ 120,00** até **R$ 199,99**.
* **Plano Ouro**: mensalidades a partir de **R$ 200,00** (até o teto de R$ 1.000,00).

### 3. Validações e Tratamento de Erros
Para manter o sistema seguro e previsível:
* **Valores fora dos limites (`ValueError`)**: valores base menores que R$ 60,00 ou maiores que R$ 1.000,00, quantidade negativa de dependentes ou acima de 5, cupons menores que 0% ou maiores que 50%.
* **Tipos inválidos (`TypeError`)**: passar texto, nulo ou outro formato no lugar de números.

---

## 🧪 Estratégia de Testes

Os testes são organizados em um único arquivo (`tests/test_academia.py`) e cobrem:

* **Casos Comuns (AAA)**: simulação de cenários reais de contratação com cálculo exato do valor esperado.
* **Análise de Limites**: validação das fronteiras exatas entre cada categoria (ex: R$ 119,00 para Bronze e R$ 120,00 para Prata; R$ 199,00 para Prata e R$ 200,00 para Ouro).
* **Entradas Inválidas (Error Guessing)**: garantia de que o sistema rejeita valores absurdos ou tipos incompatíveis com os erros corretos.
