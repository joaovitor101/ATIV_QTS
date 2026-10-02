# FitPlan - Sistema de Gestão de Assinaturas de Academia (QTS)

Repositório da atividade prática avaliativa da disciplina **Qualidade e Teste de Software (QTS)** da **FATEC**. O projeto consiste em um motor determinístico simplificado para cálculo e avaliação de planos e mensalidades de academia (**FitPlan**), estruturado para aplicação direta e didática das técnicas formais de Engenharia de Testes de Software em um **único arquivo de teste**.

---

## 🎯 Destaques do Projeto

* **Domínio Determinístico e Simplificado**: Cálculo de mensalidade considerando valor base do plano, quantidade de dependentes e cupons promocionais de desconto, com classificação automática de categoria do plano (`Plano Ouro`, `Plano Prata`, `Plano Bronze`).
* **Suíte Única de Testes Formais (`tests/test_academia.py`)**:
  * Padrão **AAA (Arrange, Act, Assert)** explícito.
  * **Testes Parametrizados** com `@pytest.mark.parametrize` e marcação `@pytest.mark.unit`.
  * **Particionamento de Equivalência (EP)**.
  * **Análise do Valor Limite (BVA)** cobrindo todas as fronteiras numéricas.
  * **Adivinhação de Erros (Error Guessing)** cobrindo entradas fora dos limites e tipos incompatíveis (`ValueError` e `TypeError`).
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
│   ├── __init__.py              # Exportação da classe de domínio
│   └── academia.py              # AvaliadorAcademia com regras de negócio e validações
└── tests/                       # Suíte de Testes Unitários
    ├── __init__.py
    └── test_academia.py         # Arquivo único de testes com EP, BVA, AAA e Error Guessing
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

### 3. Execução dos Testes com Pytest e Verificação de 100% de Cobertura
Para rodar a suíte completa de testes no modo detalhado:
```bash
uv run pytest -v
```

Para rodar com relatório explícito de cobertura e ramificações:
```bash
uv run pytest --cov=app --cov-branch --cov-report=term-missing
```
*(Nota: As opções de cobertura e relatório já vêm pré-configuradas no `pyproject.toml`, portanto `uv run pytest -v` já gera o relatório de cobertura completo).*


---

## 🧪 Estrutura da Suíte de Testes (`tests/test_academia.py`)

O arquivo de testes está dividido nas seções formais exigidas pela disciplina:

### 1. Testes Parametrizados & Padrão AAA
```python
# ================= Testes parametrizados =====================
@pytest.mark.unit
@pytest.mark.parametrize(
    "valor_base, dependentes, cupom_desconto, valor_dependente, esperado",
    [
        (100.0, 0, 0.0, 50.0, 100.0),
        (100.0, 2, 0.0, 50.0, 200.0),
        (200.0, 1, 10.0, 50.0, 225.0),
        (150.0, 3, 20.0, 50.0, 240.0),
    ]
)
# ================= Padrão AAA =======================
def test_calcular_mensalidade_sucesso(valor_base, dependentes, cupom_desconto, valor_dependente, esperado):
    # Arrange & Act
    resultado = AvaliadorAcademia.calcular_mensalidade(valor_base, dependentes, cupom_desconto, valor_dependente)
    
    # Assert
    assert resultado == esperado
```

### 2. Análise de Limites (BVA) e Particionamento de Equivalência (EP)
```python
# ================= Análise de Limites ======================
@pytest.mark.unit
@pytest.mark.parametrize(
    "valor_base, dependentes, cupom_desconto, expected_categoria",
    [
        (200.0, 0, 0.0, "Plano Ouro"),
        (1000.0, 0, 0.0, "Plano Ouro"),
        (199.0, 0, 0.0, "Plano Prata"),
        (120.0, 0, 0.0, "Plano Prata"),
        (119.0, 0, 0.0, "Plano Bronze"),
        (60.0, 0, 0.0, "Plano Bronze"),
    ]
)
def test_determinar_categoria_limites_e_ep(valor_base, dependentes, cupom_desconto, expected_categoria):
    # Arrange
    mensalidade = AvaliadorAcademia.calcular_mensalidade(valor_base, dependentes, cupom_desconto)
    
    # Act
    categoria = AvaliadorAcademia.determinar_categoria_plano(mensalidade)
    
    # Assert
    assert categoria == expected_categoria
```

### 3. Adivinhação de Erros (Error Guessing)
```python
# ===================== Error Guessing ==========================
@pytest.mark.unit
@pytest.mark.parametrize(
    "valor_base, dependentes, cupom_desconto",
    [
        (59.9, 0, 0.0),
        (1000.1, 0, 0.0),
        (100.0, -1, 0.0),
        (100.0, 6, 0.0),
        (100.0, 0, -0.1),
        (100.0, 0, 50.1),
    ]
)
def test_error_guessing_valores_fora_dos_limites(valor_base, dependentes, cupom_desconto):
    with pytest.raises(ValueError):
        AvaliadorAcademia.calcular_mensalidade(valor_base, dependentes, cupom_desconto)
```
