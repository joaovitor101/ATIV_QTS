# Uso de Inteligência Artificial no Projeto

Relatório sobre como utilizei inteligência artificial como apoio no desenvolvimento desta atividade prática de Qualidade e Teste de Software (QTS).

## 1. Ferramentas

* **Assistente e IDE**: Google Antigravity (Antigravity IDE).
* **Ambiente e Pacotes**: uv com Python 3.14.

## 2. Como a IA me Ajudou

Usei o Antigravity como suporte nas seguintes partes:

* **Regras de Negócio**: Apoio para definir as faixas de mensalidade da academia, regras para dependentes e as categorias dos planos (Bronze, Prata e Ouro).
* **Código Principal**: Auxílio na escrita da classe `AvaliadorAcademia` com funções simples e tratamento de erros (`ValueError` e `TypeError`).
* **Criação dos Testes**: Ajuda na montagem da suíte de testes com `@pytest.mark.parametrize`, aplicando o padrão AAA, limites numéricos (BVA) e testes com dados inválidos (Error Guessing).

## 3. Validação dos Resultados

Revisei o código gerado linha por linha para garantir que a lógica e as contas estavam certas. Por fim, rodei os testes no terminal para confirmar que todos passavam com 100% de cobertura:

```bash
uv run pytest -v
uv run pytest --cov=app --cov-branch --cov-report=term-missing
```
