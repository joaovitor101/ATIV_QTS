# AGENTS.md - Diretrizes de Governança de Agentes Autônomos de IA

Este documento define os limites operacionais, diretrizes arquiteturais e critérios de qualidade a serem seguidos por agentes de IA e desenvolvedores que atuam no repositório `atividade-qts`.

---

## 1. Contexto do Repositório
* **Disciplina**: Qualidade e Teste de Software (QTS) - FATEC.
* **Escopo**: Motor determinístico de cálculo de assinaturas de academia, planos, dependentes, cupons e pagamentos com suíte formal de testes unitários.
* **Idioma do Projeto**: 100% em português (PT-BR) para arquivos, funções, classes, mensagens de erro e documentação.
* **Gerenciador de Pacotes**: `uv`.
* **Versão do Python**: Python 3.12+ (executando nativamente em Python 3.14).

---

## 2. Limites e Regras Operacionais para IA
1. **Determinismo Estrito**: Não adicionar chamadas a APIs externas, requisições HTTP (`requests`/`httpx`), ou geradores randômicos não seedados no código de produção.
2. **Design de Testes**:
   * O padrão **AAA (Arrange, Act, Assert)** é obrigatório e inegociável em todos os testes.
   * Não usar asserções genéricas como `assert result is not None` quando valores exatos podem ser calculados.
   * Utilizar técnicas formais de teste:
     * **EP (Particionamento de Equivalência)**: Classes válidas e inválidas para cada parâmetro.
     * **BVA (Análise do Valor Limite)**: Valores imediatamente anteriores, sobre e imediatamente superiores aos limites de transição de regra.
     * **Adivinhação de Erros (Error Guessing)**: Cenários de entradas aberrantes, tipos incorretos, valores negativos e nulos.
3. **Métrica de Aceitação**:
   * O comando `uv run pytest --cov=app --cov-branch --cov-report=term-missing` deve atingir impreterivelmente **100% de cobertura de linhas e branches**.

---

## 3. Protocolo de Auditoria Contínua
* Antes de aprovar qualquer alteração sugerida pela IA:
  1. Executar a suíte de testes unitários.
  2. Verificar se todas as ramificações `if/elif/else` possuem testes direcionados.
  3. Auditar a fidelidade das mensagens de erro e exceções tipadas em relação ao `PRD.md`.
