# FitPlan - Sistema de Gestão de Assinaturas de Academia (QTS)

Repositório da atividade prática avaliativa da disciplina **Qualidade e Teste de Software (QTS)** da **FATEC**. O projeto consiste em um motor determinístico de regras de negócio para cálculo e orquestração de matrículas e assinaturas de planos de academia (**FitPlan**), projetado para aplicação exaustiva de técnicas formais de Engenharia de Testes de Software.

---

## 🎯 Destaques do Projeto

* **Domínio Determinístico e Enxuto**: Gestão de planos de academia (`BRONZE`, `PRATA`, `OURO`), modalidades de acesso (`FORA_PICO`, `LIVRE`, `PICO_VIP`), pacote familiar com até 5 dependentes e descontos progressivos (10% e 20%), fidelidade por periodicidade (`MENSAL`, `SEMESTRAL`, `ANUAL`), cupons promocionais (`MATRICULAGRATIS`, `VERAO10`, `AMIGO20`) e condições financeiras por forma de pagamento (PIX, Boleto e Cartão de Crédito).
* **Validação Defensiva**: Modelos com Pydantic v2 e Type Hints estritos, com hierarquia de exceções personalizadas derivadas de `ErroFitPlan`.
* **Suíte de Testes Formais**:
  * Padrão **AAA (Arrange, Act, Assert)** explícito em todos os testes.
  * **Particionamento de Equivalência (EP)**.
  * **Análise do Valor Limite (BVA)** em todas as transições de regras e faixas numéricas.
  * **Adivinhação de Erros (Error Guessing)** cobrindo entradas anômalas, tipos incompatíveis e tentativas de violação de integridade.
  * Uso de `@pytest.mark.parametrize` e marcação `@pytest.mark.unit`.
* **100% de Cobertura de Código e Ramificações (Branch Coverage)**:
  * Medição oficial via `pytest-cov` com flag `--cov-branch`.

---

## 📁 Estrutura Enxuta do Repositório (100% em Português)

```text
atividade-qts/
├── .cursorrules                 # Diretrizes de contexto para IDEs de IA
├── AGENTS.md                    # Diretrizes para agentes autônomos e desenvolvedores
├── AI_USAGE.md                  # Relatório de transparência no uso de Inteligência Artificial
├── PRD.md                       # Documento de Requisitos do Produto (Especificação Formal)
├── README.md                    # Documentação principal e guia de apresentação
├── pyproject.toml               # Configuração do projeto uv, pytest e coverage
├── app/                         # Domínio do Sistema (SUT - Sistema Sob Teste)
│   ├── __init__.py
│   ├── excecoes.py              # Hierarquia de exceções customizadas de domínio
│   ├── modelos.py               # Modelos de dados Pydantic com validação defensiva
│   ├── motor_academia.py        # Motor de cálculo de planos, dependentes, cupons e pagamentos
│   └── servico_assinatura.py    # Orquestrador determinístico de adesão ao plano
└── tests/                       # Suíte de Testes Unitários
    ├── __init__.py
    ├── conftest.py              # Fixtures compartilhadas para testes
    ├── test_modelos.py          # Testes unitários defensivos dos modelos (Aluno, Dependente)
    ├── test_motor_academia.py   # Testes de regras de negócio (EP, BVA, Adivinhação de Erros)
    └── test_servico_assinatura.py # Testes integrados ponta a ponta do serviço
```

---

## 🚀 Como Executar o Projeto

O projeto é gerenciado de forma rápida pelo **uv**.

### 1. Pré-requisitos
* Python 3.12+ instalado.
* `uv` instalado.

### 2. Sincronizar Dependências
```bash
uv sync
```

### 3. Execução dos Testes com Pytest
Para rodar a suíte completa de testes no modo detalhado:
```bash
uv run pytest -v
```

### 4. Verificação de Cobertura de Código e Ramificações (100% Branches)
Para comprovar que todas as linhas e todas as ramificações lógicas das regras de negócio foram cobertas:
```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing
```

---

## 🧪 Técnicas de Teste Aplicadas

### 1. Padrão AAA (Arrange, Act, Assert)
Todos os testes possuem divisão visual clara e padronizada:
```python
# Arrange: Aluno Bronze, Livre, Mensal, Sem dependentes, PIX
assinatura = EntradaAssinatura(
    aluno=aluno_valido,
    plano=Plano.BRONZE,
    horario=HorarioAcesso.LIVRE,
    periodicidade=Periodicidade.MENSAL,
    dependentes=[],
    cupom=None,
    metodo_pagamento=MetodoPagamento.PIX,
    parcelas=1,
)

# Act: Processa o cálculo determinístico
resumo = processar_assinatura(assinatura)

# Assert: Valida aplicação precisa das regras
assert resumo.mensalidade_final == 90.00
assert resumo.primeiro_pagamento_total == 161.50
assert resumo.status == "ATIVO"
```

### 2. Particionamento de Equivalência (EP)
Divisão dos domínios de entrada em classes de equivalência válidas e inválidas:
* **Planos**: `BRONZE` (R$ 90,00), `PRATA` (R$ 140,00) e `OURO` (R$ 200,00).
* **Horários**: `FORA_PICO` (-15%), `LIVRE` (0%) e `PICO_VIP` (+R$ 30,00).
* **Periodicidades**: `MENSAL` (0%), `SEMESTRAL` (5%) e `ANUAL` (12%).
* **Formas de Pagamento**: PIX (à vista), Boleto (à vista, semestral/anual) e Cartão de Crédito (1 a 12x).

### 3. Análise do Valor Limite (BVA)
Foco cirúrgico nas fronteiras das regras:
* **Idades**: 11 anos (bloqueado) vs 12 anos (mínimo válido); 100 anos (máximo válido) vs 101 anos (bloqueado).
* **Dependentes**: 0 dependente (0%), 1 dependente (0%), 2 dependentes (10%), 3 dependentes (20%), 5 dependentes (limite máximo) vs 6 dependentes (`ErroLimiteDependentesExcedido`).
* **Parcelas do Cartão**: 0 (erro), 1 a 6 (sem juros), 7 a 12 (com 5% de juros), 13 (erro).
* **Pontos de Fidelidade**: R$ 19,99 (0 pts) vs R$ 20,00 (1 pt) no Bronze; R$ 14,99 vs R$ 15,00 no Prata; R$ 9,99 vs R$ 10,00 no Ouro.

### 4. Adivinhação de Erros (Error Guessing)
Previsão empírica de falhas em situações de uso anômalo:
* Cupom `MATRICULAGRATIS` aplicado a plano `BRONZE` (lança `ErroCupomInvalido`).
* Cupom `AMIGO20` aplicado a plano sem dependentes (lança `ErroCupomInvalido`).
* Boletos em contratos mensais ou com mais de 1 parcela (lança `ErroMetodoPagamentoInvalido`).
* CPFs com todos os dígitos iguais ou comprimentos inválidos.
* Nomes e parentescos com espaços em branco ou vazios.

---

## 📹 Roteiro Sugerido para a Gravação do Vídeo (Até 4 Minutos)

| Tempo | Etapa / Tela a Exibir | O que Falar (Locução) |
|---|---|---|
| **0:00 - 0:50** | **Apresentação Inicial e PRD**<br>Exibir o arquivo `PRD.md` no editor. | *"Olá! Nesta atividade prática de Qualidade e Teste de Software (QTS), implementamos o FitPlan, um sistema determinístico de gestão e adesão de planos de academia. O sistema gerencia planos Bronze, Prata e Ouro, descontos de horários fora de pico, acréscimos VIP, pacote familiar com desconto progressivo por dependentes, cupons condicionais e formas de pagamento. Todas as regras e limites estão especificados no PRD.md."* |
| **0:50 - 1:40** | **Governança e Transparência de IA**<br>Exibir `AGENTS.md` e `AI_USAGE.md`. | *"Aqui apresentamos a governança e o relatório de transparência de IA. No AGENTS.md e no .cursorrules estabelecemos limites rigorosos: determinismo estrito, padrão AAA em todos os testes e a exigência de 100% de branch coverage. No AI_USAGE.md documentamos o uso da IA para propor matrizes de testes formais e como foi realizada a auditoria humana do código."* |
| **1:40 - 2:40** | **Suíte de Testes Formais**<br>Navegar pelos arquivos em `tests/`. | *"Na pasta tests/, temos uma suíte enxuta e robusta com testes unitários em test_modelos.py, test_motor_academia.py e test_servico_assinatura.py, totalmente em português. Demonstramos a aplicação de Particionamento de Equivalência, Análise do Valor Limite nas faixas de idade (11 vs 12, 100 vs 101), limites de dependentes (0 a 5 e exceção com 6), cupons restritivos e Adivinhação de Erros para CPFs repetidos e parcelamentos ilegais, sempre respeitando o padrão AAA."* |
| **2:40 - 3:45** | **Execução no Terminal**<br>Abrir terminal integrado da IDE. | *"Agora vamos ao terminal. Executamos `uv run pytest -v`. Todos os 56 testes passam instantaneamente. Em seguida, rodamos o comando oficial com cobertura de ramificações: `uv run pytest --cov=app --cov-branch --cov-report=term-missing`. Constatamos exatamente 100% de cobertura de código e 100% de branch coverage em todos os módulos!"* |
| **3:45 - 4:00** | **Conclusão e Encerramento**<br>Voltar para o `README.md`. | *"Concluímos demonstrando que a aplicação das técnicas formais de Engenharia de Testes garantiu total confiabilidade, simplicidade e qualidade ao domínio do software. Obrigado!"* |

---

## 👨‍💻 Autoria e Licença
Projeto desenvolvido para a disciplina de **Qualidade e Teste de Software (QTS)**. Licença MIT.
