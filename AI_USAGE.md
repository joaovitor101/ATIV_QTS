# AI_USAGE.md - Relatório de Transparência e Governança no Uso de IA

Este relatório documenta a utilização de ferramentas de Inteligência Artificial generativa no desenvolvimento do projeto **atividade-qts** (**FitPlan - Sistema de Gestão de Assinaturas de Academia**), atendendo aos requisitos de integridade acadêmica e transparência técnica da disciplina **Qualidade e Teste de Software (QTS)** da **FATEC**.

---

## 1. Ferramentas Utilizadas
* **IDE / Ambiente**: Antigravity IDE (desenvolvida pela equipe Google DeepMind).
* **Modelo Fundacional**: Gemini 3.8 Flash (High Reasoning).
* **Gerenciamento de Dependências**: `uv` (Astral).
* **Framework de Testes**: `pytest` com plugin `pytest-cov`.

---

## 2. Metodologia de Aplicação da IA

A Inteligência Artificial foi empregada como **Pair Programmer Autônomo e Assistente de Engenharia de Testes**, atuando nas seguintes etapas:

### 2.1. Concepção e Formalização do PRD
* A IA auxiliou na estruturação dos requisitos do sistema **FitPlan**, modelando um motor determinístico e enxuto com regras de negócio claras para planos (`BRONZE`, `PRATA`, `OURO`), horários de acesso (`FORA_PICO`, `LIVRE`, `PICO_VIP`), pacote familiar com até 5 dependentes, descontos por periodicidade (`MENSAL`, `SEMESTRAL`, `ANUAL`), cupons promocionais (`MATRICULAGRATIS`, `VERAO10`, `AMIGO20`) e formas de pagamento.

### 2.2. Implementação do Domínio Enxuto (SUT)
* Construção de uma arquitetura limpa em apenas 3 módulos centrais, totalmente em português (PT-BR):
  * [`app/modelos.py`](file:///c:/Users/fatec-dsm6/Documents/atividade-qts/app/modelos.py): Modelos Pydantic v2 com validações defensivas antecipadas (`mode="before"`).
  * [`app/motor_academia.py`](file:///c:/Users/fatec-dsm6/Documents/atividade-qts/app/motor_academia.py): Motor determinístico com fórmulas de cálculo de mensalidade, taxas e condições financeiras.
  * [`app/servico_assinatura.py`](file:///c:/Users/fatec-dsm6/Documents/atividade-qts/app/servico_assinatura.py): Orquestrador de adesão que consolida o resumo da assinatura.
  * [`app/excecoes.py`](file:///c:/Users/fatec-dsm6/Documents/atividade-qts/app/excecoes.py): Hierarquia tipada de exceções derivadas de `ErroFitPlan`.

### 2.3. Elaboração da Matriz e Suíte de Testes
* Mapeamento sistemático de técnicas formais:
  * **Particionamento de Equivalência (EP)**: Identificação de classes de planos, modalidades de horários, periodicidades e formas de pagamento.
  * **Análise do Valor Limite (BVA)**: Casos de teste nas fronteiras numéricas exatas (idades 11 vs 12, 100 vs 101; dependentes 0, 1, 2, 3, 5 e estouro em 6; parcelas de cartão 0, 1, 6, 7, 12, 13; conversão de pontos).
  * **Adivinhação de Erros (Error Guessing)**: Entradas anômalas, tipos incompatíveis, strings vazias, CPFs com dígitos repetidos e combinações de cupons ilegais.
* Estruturação formal de 100% dos testes no padrão **AAA (Arrange, Act, Assert)** com parametrização via `@pytest.mark.parametrize`.

---

## 3. Processo de Auditoria e Verificação Humana

Para assegurar a máxima integridade e confiabilidade do software:

1. **Auditoria Estática de Tipagem e Contratos**:
   * Verificação manual da aderência dos modelos e assinaturas de funções aos tipos estritos do Python e Pydantic.
   * Garantia de ausência de dependências externas ou efeitos colaterais de I/O / rede.

2. **Auditoria de Asserções e Padrão AAA**:
   * Inspeção visual do código dos testes para comprovar a presença explícita dos blocos `# Arrange`, `# Act` e `# Assert`.
   * Verificação de que as asserções conferem valores monetários e numéricos exatos, sem asserções vagas.

3. **Auditoria Dinâmica de Cobertura de Ramificações (Branch Coverage)**:
   * Execução de `uv run pytest --cov=app --cov-branch --cov-report=term-missing`.
   * Comprovação matemática de que **todas as 66 ramificações lógicas (branches) e 187 instruções executáveis foram exercitadas com 100% de sucesso em 56 testes**.

4. **Teste de Mutação Manual (Sanity Check)**:
   * Alteração deliberada de valores de asserção (ex.: forçar `assert base == 999`) para comprovar que os testes quebram imediatamente quando há inconsistência.

---

## 4. Declaração de Integridade
Todo o código gerado foi integralmente auditado, compreendido e validado, garantindo conformidade total com os objetivos pedagógicos da disciplina.
