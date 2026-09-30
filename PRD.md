# PRD - Documento de Requisitos do Produto (FitPlan)

## Sistema de Gestão de Planos e Assinaturas de Academia (Domínio Determinístico)

---

### 1. Visão Geral e Objetivos do Produto
O **FitPlan** é um motor determinístico de regras de negócio para cálculo e orquestração de matrículas e assinaturas de planos de academia. O sistema gerencia a adesão de alunos, inclusão de dependentes com pacote familiar, seleção de horários de acesso, descontos por periodicidade contratual, cupons promocionais de matrícula e acréscimos/descontos por meio de pagamento.

O objetivo acadêmico deste componente na disciplina **Qualidade e Teste de Software (QTS)** da **FATEC** é atuar como **SUT (Sistema Sob Teste)** 100% determinístico e livre de efeitos colaterais de rede ou banco de dados, servindo de base para aplicação prática e exaustiva de:
* **Particionamento de Equivalência (EP)**
* **Análise do Valor Limite (BVA)**
* **Adivinhação de Erros (Error Guessing)**
* **Padrão AAA (Arrange, Act, Assert)**
* **100% de Cobertura de Código e Ramificações (Branch Coverage)**

---

### 2. Personas e Atores do Sistema
* **Aluno Titular**: Usuário pagante identificado por CPF, e-mail e idade que contrata o plano para si e opcionalmente inclui dependentes.
* **Dependente**: Familiar vinculado ao titular que usufrui dos serviços da academia mediante acréscimo proporcional.
* **Motor FitPlan**: Módulo determinístico responsável por validar as regras cadastrais, calcular mensalidades, dependentes, cupons, condições de pagamento e pontos de fidelidade.

---

### 3. Requisitos Funcionais (RF)

#### RF01 - Validação Cadastral do Aluno Titular
* **RF01.1**: Nome do aluno deve ter no mínimo 2 caracteres não vazios.
* **RF01.2**: CPF deve conter exatamente 11 dígitos numéricos válidos e não pode conter todos os dígitos iguais.
* **RF01.3**: E-mail deve respeitar o formato válido de correio eletrônico (`usuario@dominio.com`).
* **RF01.4**: A idade do aluno deve estar entre 12 e 100 anos (limite operacional da academia).
* **Exceção**: Violações disparam `ErroAlunoInvalido`.

#### RF02 - Validação e Limites de Dependentes
* **RF02.1**: Cada dependente deve possuir nome válido (mínimo 2 caracteres), parentesco preenchido e idade entre 12 e 100 anos (`ErroDependenteInvalido` em caso de violação).
* **RF02.2**: O titular pode cadastrar de 0 até o limite máximo de 5 dependentes. Se ultrapassar 5 dependentes, dispara `ErroLimiteDependentesExcedido`.

#### RF03 - Planos e Horário de Acesso
* **RF03.1 (Tabela Base de Planos)**:
  * `BRONZE`: R$ 90,00 / mês (musculação básica).
  * `PRATA`: R$ 140,00 / mês (musculação + aulas coletivas).
  * `OURO`: R$ 200,00 / mês (acesso total + natação).
* **RF03.2 (Ajuste por Horário de Acesso do Titular)**:
  * `FORA_PICO` (09h às 16h): Concede 15% de desconto sobre a mensalidade base do titular.
  * `LIVRE`: Sem alteração no valor base (R$ 0,00).
  * `PICO_VIP` (acesso prioritário e armário exclusivo em horário de pico): Acréscimo fixo de R$ 30,00.

#### RF04 - Inclusão de Dependentes e Desconto Pacote Família
* **RF04.1**: O valor adicional unitário por dependente varia conforme o plano do titular:
  * Plano `BRONZE`: R$ 60,00 por dependente.
  * Plano `PRATA`: R$ 90,00 por dependente.
  * Plano `OURO`: R$ 130,00 por dependente.
* **RF04.2 (Desconto Pacote Família)**: Aplicado exclusivamente sobre o valor total dos dependentes:
  * 0 ou 1 dependente: 0% de desconto.
  * 2 dependentes: 10% de desconto sobre o valor dos dependentes.
  * 3 a 5 dependentes: 20% de desconto sobre o valor dos dependentes.

#### RF05 - Desconto por Periodicidade Contratual
Aplicado sobre a soma da mensalidade do titular e dos dependentes líquidos:
* `MENSAL`: 0% de desconto.
* `SEMESTRAL`: 5% de desconto no valor mensal.
* `ANUAL`: 12% de desconto no valor mensal.

#### RF06 - Taxa de Matrícula e Cupons Promocionais
* **RF06.1**: A taxa de matrícula padrão é de R$ 80,00 (cobrada no primeiro pagamento).
* **RF06.2 (Cupons Promocionais)**:
  * `MATRICULAGRATIS`: Zera a taxa de matrícula (R$ 0,00). **Regra de Ativação**: Válido exclusivamente para planos `PRATA` ou `OURO`. Se utilizado com plano `BRONZE`, lança `ErroCupomInvalido`.
  * `VERAO10`: Concede 10% de desconto sobre o valor da mensalidade final.
  * `AMIGO20`: Concede 20% de desconto sobre o valor da mensalidade final. **Regra de Ativação**: Exige a presença de ao menos 1 dependente no contrato. Caso contrário, lança `ErroCupomInvalido`.
  * Qualquer outro código preenchido lança `ErroCupomInvalido`. Se nulo ou vazio, nenhum cupom é aplicado.

#### RF07 - Condições de Pagamento e Ajustes Financeiros
Calculado sobre o valor do primeiro pagamento (mensalidade líquida + taxa de matrícula):
* **RF07.1 (PIX)**: Exige parcela única (`parcelas=1`). Concede 5% de desconto financeiro. Se `parcelas != 1`, lança `ErroMetodoPagamentoInvalido`.
* **RF07.2 (Boleto)**: Exige parcela única (`parcelas=1`) e permite apenas planos com periodicidade `SEMESTRAL` ou `ANUAL`. Se `parcelas != 1` ou se for periodicidade `MENSAL`, lança `ErroMetodoPagamentoInvalido`. Concede 3% de desconto financeiro.
* **RF07.3 (Cartão de Crédito)**: Permite de 1 a 12 parcelas (fora dessa faixa lança `ErroMetodoPagamentoInvalido`).
  * 1 a 6 parcelas: sem acréscimo de juros (0%).
  * 7 a 12 parcelas: acréscimo de 5% de juros sobre o valor do primeiro pagamento.

#### RF08 - Programa de Fidelidade
Acúmulo de pontos calculados no primeiro pagamento efetivo:
* `BRONZE`: 1 ponto a cada R$ 20,00 gastos (`int(valor_pago // 20)`).
* `PRATA`: 1 ponto a cada R$ 15,00 gastos (`int(valor_pago // 15)`).
* `OURO`: 1 ponto a cada R$ 10,00 gastos (`int(valor_pago // 10)`).

---

### 4. Matriz de Rastreabilidade e Técnicas de Teste

| Requisito | Técnica de Teste Aplicada | Cenários Chave e Limites (BVA / EP / Adivinhação de Erros) |
|---|---|---|
| **RF01 (Aluno)** | EP / BVA / Adivinhação de Erros | Idade 11 (erro), 12 (limite válido), 100 (limite válido), 101 (erro); Nome com 1 char e espaços vazios; CPFs válidos vs 10/12 dígitos e dígitos iguais; e-mail válido vs sem arroba/domínio. |
| **RF02 (Dependentes)** | EP / BVA / Adivinhação de Erros | 0 dependentes; 1 dependente; 5 dependentes (limite superior); 6 dependentes (`ErroLimiteDependentesExcedido`); idade inválida de dependente (<12 ou >100). |
| **RF03 (Planos & Horário)** | EP | Planos `BRONZE`, `PRATA`, `OURO`; Horários `FORA_PICO` (-15%), `LIVRE` (0%), `PICO_VIP` (+R$ 30,00). |
| **RF04 (Desconto Família)** | BVA / EP | 1 dependente (0%), 2 dependentes (10% limite transição), 3 dependentes (20% limite transição), 5 dependentes (20%). |
| **RF05 (Periodicidade)** | EP | `MENSAL` (0%), `SEMESTRAL` (5%), `ANUAL` (12%). |
| **RF06 (Cupons)** | EP / BVA / Adivinhação de Erros | `MATRICULAGRATIS` no Bronze (erro) vs Prata/Ouro (sucesso); `AMIGO20` com 0 dependentes (erro) vs 1 dependente (sucesso); `VERAO10`; cupom desconhecido; cupom nulo/vazio. |
| **RF07 (Pagamento)** | EP / BVA / Adivinhação de Erros | PIX com 1 vs 2 parcelas; Boleto com Mensal (erro) vs Semestral/Anual (sucesso) e parcelas > 1; Cartão parcelas 0 (erro), 1 a 6 (0%), 7 a 12 (5%), 13 (erro). |
| **RF08 (Fidelidade)** | EP / BVA | Gasto de R$ 19,99 vs R$ 20,00 no Bronze; R$ 14,99 vs R$ 15,00 no Prata; R$ 9,99 vs R$ 10,00 no Ouro. |
