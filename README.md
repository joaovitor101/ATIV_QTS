# FitPlan - Sistema de Planos de Academia

Projeto desenvolvido para a disciplina de **Qualidade e Teste de Software (QTS)** na **FATEC**. 

O **FitPlan** é uma aplicação simples para calcular o valor da mensalidade de uma academia (com adicionais por dependente e descontos de cupons) e classificar o plano do aluno entre Bronze, Prata e Ouro.

---

## 💡 Sobre o Projeto

O foco principal do trabalho é a aplicação prática de técnicas de testes unitários:

* **Padrão AAA**: organização dos testes em *Arrange* (preparação), *Act* (execução) e *Assert* (validação).
* **Particionamento de Equivalência (EP) e Análise de Limites (BVA)**: validação das fronteiras numéricas entre os planos Bronze, Prata e Ouro.
* **Adivinhação de Erros (Error Guessing)**: testes com valores fora dos limites permitidos e tipos inválidos (`ValueError` e `TypeError`).
* **100% de Cobertura**: todas as linhas e ramificações (*branches*) do código foram testadas e validadas.

---

## 📁 Estrutura do Projeto

```text
ATIV_QTS/
├── app/
│   ├── __init__.py
│   └── academia.py          # Lógica de cálculo e categorias (AvaliadorAcademia)
├── tests/
│   ├── __init__.py
│   └── test_academia.py     # Arquivo único com os 30 testes parametrizados
├── AI_USAGE.md              # Transparência sobre o uso de IA no projeto
├── PRD.md                   # Requisitos e regras de negócio explicadas
├── pyproject.toml           # Configuração do projeto e do pytest
└── README.md                # Apresentação do projeto
```

---

## 🚀 Como Rodar o Projeto

O projeto utiliza o **uv** para gerenciar dependências e o ambiente virtual.

### 1. Instalar as dependências
```bash
uv sync
```

### 2. Rodar os testes
Para rodar todos os testes de forma detalhada:
```bash
uv run pytest -v
```

Para rodar exibindo a tabela completa de cobertura de código e ramificações:
```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing
```

---

## 📋 Regras Resumidas

* **Mensalidade Base**: de R$ 60,00 a R$ 1.000,00.
* **Dependentes**: de 0 a 5 dependentes (R$ 50,00 por dependente).
* **Cupom de Desconto**: de 0% a 50%.
* **Categorias**:
  * **Plano Bronze**: de R$ 60,00 a R$ 119,99
  * **Plano Prata**: de R$ 120,00 a R$ 199,99
  * **Plano Ouro**: a partir de R$ 200,00
