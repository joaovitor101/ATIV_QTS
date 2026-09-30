"""Testes unitários do motor de regras do FitPlan (EP, BVA e Adivinhação de Erros).

Este módulo valida o cálculo determinístico de mensalidades, adicionais de
dependentes, cupons de desconto, regras de pagamento e conversão de fidelidade.
"""

import pytest
from app.excecoes import (
    ErroCupomInvalido,
    ErroLimiteDependentesExcedido,
    ErroMetodoPagamentoInvalido,
)
from app.modelos import (
    Dependente,
    HorarioAcesso,
    MetodoPagamento,
    Periodicidade,
    Plano,
)
from app.motor_academia import (
    calcular_ajuste_pagamento,
    calcular_dependentes,
    calcular_desconto_periodicidade,
    calcular_mensalidade_titular,
    calcular_pontos_fidelidade,
    calcular_taxa_matricula_e_cupom,
)


@pytest.mark.unit
class TestCalcularMensalidadeTitular:
    """Testes de equivalência e regras de preço para planos e horários (RF03).

    Técnica: Particionamento de Equivalência (EP).
    Verifica se cada categoria de plano e modalidade de acesso aplicam
    o preço base e o percentual de desconto/acréscimo correto.
    """

    @pytest.mark.parametrize(
        "plano, horario, base_esperada, ajuste_esperado",
        [
            # Caso 1: Plano Bronze com desconto de 15% para horário fora de pico
            (Plano.BRONZE, HorarioAcesso.FORA_PICO, 90.0, -13.50),
            # Caso 2: Plano Prata com acréscimo fixo de R$ 30,00 para horário VIP de pico
            (Plano.PRATA, HorarioAcesso.PICO_VIP, 140.0, 30.0),
            # Caso 3: Plano Ouro com horário livre (sem desconto ou acréscimo)
            (Plano.OURO, HorarioAcesso.LIVRE, 200.0, 0.0),
        ],
    )
    def test_calculo_mensalidade_titular_e_ajuste_horario(
        self, plano: Plano, horario: HorarioAcesso, base_esperada: float, ajuste_esperado: float
    ):
        """Objetivo: Garantir que o valor base e o ajuste de horário sejam calculados com precisão."""
        # Arrange & Act: Invoca o cálculo passando a combinação de plano e horário
        base, ajuste = calcular_mensalidade_titular(plano, horario)

        # Assert: Valida se o preço base e o ajuste financeiro batem com o esperado
        assert base == base_esperada
        assert ajuste == ajuste_esperado


@pytest.mark.unit
class TestCalcularDependentes:
    """Testes de limites e descontos progressivos do Pacote Família (RF04).

    Técnica: Análise do Valor Limite (BVA) e Particionamento de Equivalência.
    Regras:
    - 0 ou 1 dependente: 0% de desconto
    - 2 dependentes: 10% de desconto
    - 3 a 5 dependentes: 20% de desconto
    - 6 ou mais dependentes: Exceção (limite contratual estourado)
    """

    def test_zero_dependentes(self):
        """Objetivo: Validar que lista vazia de dependentes resulta em custo zero."""
        # Arrange: Aluno titular sem nenhum dependente
        deps = []

        # Act: Executa o cálculo de dependentes para plano Prata
        bruto, desc, liquido = calcular_dependentes(Plano.PRATA, deps)

        # Assert: Todos os valores devem ser estritamente R$ 0,00
        assert bruto == 0.0
        assert desc == 0.0
        assert liquido == 0.0

    def test_um_dependente_sem_desconto_bva(self, dependente_valido: Dependente):
        """Objetivo: Validar que 1 único dependente não tem desconto de pacote família (0%)."""
        # Arrange: 1 dependente no plano Bronze (R$ 60,00 unitário)
        deps = [dependente_valido]

        # Act: Executa o cálculo para 1 dependente
        bruto, desc, liquido = calcular_dependentes(Plano.BRONZE, deps)

        # Assert: Bruto e líquido devem ser R$ 60,00 com R$ 0,00 de desconto
        assert bruto == 60.0
        assert desc == 0.0
        assert liquido == 60.0

    def test_dois_dependentes_desconto_10_porcento_bva(self):
        """Objetivo: Validar a transição do limite inferior para 10% de desconto (exatamente 2 dependentes)."""
        # Arrange: 2 dependentes no plano Prata (R$ 90,00 cada = R$ 180,00 bruto)
        deps = [
            Dependente(nome="Dep 1", parentesco="Irmão", idade=20),
            Dependente(nome="Dep 2", parentesco="Irmã", idade=22),
        ]

        # Act: Executa o cálculo
        bruto, desc, liquido = calcular_dependentes(Plano.PRATA, deps)

        # Assert: 10% de 180.00 = 18.00; líquido final esperado = 162.00
        assert bruto == 180.0
        assert desc == 18.0
        assert liquido == 162.0

    def test_tres_dependentes_desconto_20_porcento_bva(self):
        """Objetivo: Validar a transição do limite para a faixa máxima de 20% de desconto (a partir de 3 dependentes)."""
        # Arrange: 3 dependentes no plano Ouro (R$ 130,00 cada = R$ 390,00 bruto)
        deps = [
            Dependente(nome=f"Dep {i}", parentesco="Filho", idade=15)
            for i in range(3)
        ]

        # Act: Executa o cálculo
        bruto, desc, liquido = calcular_dependentes(Plano.OURO, deps)

        # Assert: 20% de 390.00 = 78.00; líquido final esperado = 312.00
        assert bruto == 390.0
        assert desc == 78.0
        assert liquido == 312.0

    def test_limite_dependentes_excedido_bva(self):
        """Objetivo: Validar que ultrapassar o teto máximo de 5 dependentes lança exceção (BVA: 6 dependentes)."""
        # Arrange: 6 dependentes (estoura o limite contratual máximo de 5)
        deps = [
            Dependente(nome=f"Dep {i}", parentesco="Filho", idade=15)
            for i in range(6)
        ]

        # Act & Assert: Deve lançar ErroLimiteDependentesExcedido
        with pytest.raises(ErroLimiteDependentesExcedido, match="Máximo permitido de 5 dependentes"):
            calcular_dependentes(Plano.BRONZE, deps)


@pytest.mark.unit
class TestCalcularDescontoPeriodicidade:
    """Testes de desconto por fidelidade de periodicidade do contrato (RF05).

    Técnica: Particionamento de Equivalência (EP).
    Regras:
    - MENSAL: 0% de desconto
    - SEMESTRAL: 5% de desconto
    - ANUAL: 12% de desconto
    """

    @pytest.mark.parametrize(
        "periodicidade, subtotal, desconto_esperado",
        [
            (Periodicidade.MENSAL, 100.0, 0.0),       # Mensal: sem desconto
            (Periodicidade.SEMESTRAL, 200.0, 10.0),   # Semestral: 5% de R$ 200 = R$ 10,00
            (Periodicidade.ANUAL, 200.0, 24.0),        # Anual: 12% de R$ 200 = R$ 24,00
        ],
    )
    def test_descontos_por_periodicidade(
        self, periodicidade: Periodicidade, subtotal: float, desconto_esperado: float
    ):
        """Objetivo: Garantir aplicação correta do percentual de desconto contratual."""
        # Arrange & Act: Calcula o desconto para a periodicidade informada
        desc = calcular_desconto_periodicidade(subtotal, periodicidade)

        # Assert: O valor do desconto deve ser exato
        assert desc == desconto_esperado


@pytest.mark.unit
class TestCalcularTaxaMatriculaECupom:
    """Testes de aplicação da taxa de matrícula e cupons promocionais (RF06).

    Técnicas: Particionamento de Equivalência, BVA e Adivinhação de Erros.
    Cupons:
    - MATRICULAGRATIS: Zera matrícula (exclusivo para PRATA ou OURO)
    - VERAO10: 10% de desconto na mensalidade
    - AMIGO20: 20% de desconto na mensalidade (exige >= 1 dependente)
    """

    def test_cupom_vazio_ou_nulo(self):
        """Objetivo: Quando o cupom for nulo/vazio, cobra matrícula cheia (R$ 80,00) sem desconto promocional."""
        # Arrange & Act: Sem cupom informado
        taxa, desc, cod = calcular_taxa_matricula_e_cupom(None, Plano.BRONZE, 100.0, 0)

        # Assert: Taxa padrão R$ 80,00, R$ 0,00 de desconto de cupom
        assert taxa == 80.0
        assert desc == 0.0
        assert cod is None

    def test_cupom_matricula_gratis_plano_bronze_invalido(self):
        """Objetivo: MATRICULAGRATIS no plano Bronze deve ser rejeitado com erro (restrição de elegibilidade)."""
        # Arrange, Act & Assert: Lança erro de cupom inválido para plano Bronze
        with pytest.raises(ErroCupomInvalido, match="válido apenas para planos PRATA ou OURO"):
            calcular_taxa_matricula_e_cupom("MATRICULAGRATIS", Plano.BRONZE, 100.0, 0)

    def test_cupom_matricula_gratis_sucesso(self):
        """Objetivo: MATRICULAGRATIS no plano Prata/Ouro deve zerar a taxa de matrícula (R$ 0,00)."""
        # Arrange & Act: Aplica cupom para plano elegível (Prata)
        taxa, desc, cod = calcular_taxa_matricula_e_cupom("MATRICULAGRATIS", Plano.PRATA, 140.0, 0)

        # Assert: Taxa de matrícula zerada com sucesso
        assert taxa == 0.0
        assert desc == 0.0
        assert cod == "MATRICULAGRATIS"

    def test_cupom_verao10_sucesso(self):
        """Objetivo: VERAO10 deve conceder 10% de desconto sobre o valor da mensalidade."""
        # Arrange: Mensalidade de R$ 200,00
        # Act: Aplica o cupom VERAO10
        taxa, desc, cod = calcular_taxa_matricula_e_cupom("verao10", Plano.OURO, 200.0, 0)

        # Assert: Taxa de R$ 80 mantida e R$ 20,00 (10%) de desconto na mensalidade
        assert taxa == 80.0
        assert desc == 20.0
        assert cod == "VERAO10"

    def test_cupom_amigo20_sem_dependentes_erro(self):
        """Objetivo: AMIGO20 exige ao menos 1 dependente. Sem dependentes, deve lançar erro."""
        # Arrange, Act & Assert: Qtd dependentes = 0
        with pytest.raises(ErroCupomInvalido, match="Cupom AMIGO20 exige ao menos 1 dependente."):
            calcular_taxa_matricula_e_cupom("AMIGO20", Plano.PRATA, 230.0, 0)

    def test_cupom_amigo20_com_dependente_sucesso(self):
        """Objetivo: AMIGO20 com 1 ou mais dependentes concede 20% de desconto na mensalidade."""
        # Arrange: Mensalidade de R$ 230,00 com 1 dependente
        # Act: Aplica o cupom AMIGO20
        taxa, desc, cod = calcular_taxa_matricula_e_cupom("AMIGO20", Plano.PRATA, 230.0, 1)

        # Assert: 20% de R$ 230,00 = R$ 46,00 de desconto
        assert taxa == 80.0
        assert desc == 46.00
        assert cod == "AMIGO20"

    def test_cupom_inexistente_adivinhacao_erros(self):
        """Objetivo: Adivinhação de Erros para códigos de cupons desconhecidos ou expirados."""
        # Arrange, Act & Assert: Cupom não cadastrado dispara erro
        with pytest.raises(ErroCupomInvalido, match="inválido ou expirado"):
            calcular_taxa_matricula_e_cupom("CUPOM_FALSO", Plano.PRATA, 150.0, 1)


@pytest.mark.unit
class TestCalcularAjustePagamento:
    """Testes das regras de pagamento, parcelamento e juros/descontos (RF07).

    Técnicas: Particionamento de Equivalência, BVA e Adivinhação de Erros.
    Regras:
    - PIX: 5% de desconto à vista (1 parcela apenas)
    - Boleto: 3% de desconto à vista (apenas semestral/anual)
    - Cartão: 1 a 6x sem juros; 7 a 12x com 5% de juros
    """

    def test_pix_uma_parcela_desconto_5_porcento(self):
        """Objetivo: Pagamento via PIX em 1x concede 5% de desconto financeiro."""
        # Arrange: R$ 200,00 base
        # Act: Executa o cálculo para PIX
        ajuste, total = calcular_ajuste_pagamento(
            MetodoPagamento.PIX, 1, Periodicidade.MENSAL, 200.0
        )

        # Assert: 5% de 200 = R$ 10,00 de desconto; total a pagar = R$ 190,00
        assert ajuste == -10.0
        assert total == 190.0

    def test_pix_parcelas_invalidas(self):
        """Objetivo: PIX parcelado em mais de 1x deve ser bloqueado com erro."""
        # Arrange, Act & Assert: Tentativa de 2 parcelas no PIX
        with pytest.raises(ErroMetodoPagamentoInvalido, match="PIX permite apenas 1 parcela."):
            calcular_ajuste_pagamento(MetodoPagamento.PIX, 2, Periodicidade.MENSAL, 200.0)

    def test_boleto_uma_parcela_sucesso_semestral(self):
        """Objetivo: Boleto em contrato semestral/anual concede 3% de desconto."""
        # Arrange: R$ 200,00 base com plano semestral
        # Act: Executa cálculo para Boleto
        ajuste, total = calcular_ajuste_pagamento(
            MetodoPagamento.BOLETO, 1, Periodicidade.SEMESTRAL, 200.0
        )

        # Assert: 3% de 200 = R$ 6,00 de desconto; total a pagar = R$ 194,00
        assert ajuste == -6.0
        assert total == 194.0

    def test_boleto_parcelas_invalidas(self):
        """Objetivo: Boleto parcelado em mais de 1x deve ser bloqueado com erro."""
        # Arrange, Act & Assert: Tentativa de 2 parcelas no boleto
        with pytest.raises(ErroMetodoPagamentoInvalido, match="Boleto permite apenas 1 parcela."):
            calcular_ajuste_pagamento(MetodoPagamento.BOLETO, 2, Periodicidade.SEMESTRAL, 200.0)

    def test_boleto_plano_mensal_invalido(self):
        """Objetivo: Boleto não é permitido para planos mensais (exclusivo para semestral/anual)."""
        # Arrange, Act & Assert: Tentativa de boleto em plano mensal
        with pytest.raises(ErroMetodoPagamentoInvalido, match="apenas para planos semestrais ou anuais"):
            calcular_ajuste_pagamento(MetodoPagamento.BOLETO, 1, Periodicidade.MENSAL, 200.0)

    @pytest.mark.parametrize("parcelas_invalidas", [0, 13])
    def test_cartao_credito_parcelas_fora_do_limite_bva(self, parcelas_invalidas: int):
        """Objetivo: BVA nas fronteiras de parcelamento do cartão (limite válido: 1 a 12x)."""
        # Arrange, Act & Assert: Parcelas 0 e 13 disparam erro
        with pytest.raises(ErroMetodoPagamentoInvalido, match="aceita de 1 a 12 parcelas."):
            calcular_ajuste_pagamento(
                MetodoPagamento.CARTAO_CREDITO, parcelas_invalidas, Periodicidade.MENSAL, 200.0
            )

    def test_cartao_credito_sem_juros_bva(self):
        """Objetivo: BVA no limite superior de isenção de juros (6 parcelas = 0% juros)."""
        # Arrange & Act: 6 parcelas
        ajuste, total = calcular_ajuste_pagamento(
            MetodoPagamento.CARTAO_CREDITO, 6, Periodicidade.MENSAL, 200.0
        )

        # Assert: Ajuste de juros deve ser R$ 0,00 e valor total inalterado
        assert ajuste == 0.0
        assert total == 200.0

    def test_cartao_credito_com_juros_5_porcento_bva(self):
        """Objetivo: BVA no limite inferior de cobrança de juros (7 parcelas = 5% juros)."""
        # Arrange: 7 parcelas com base de R$ 200,00
        # Act: Executa cálculo
        ajuste, total = calcular_ajuste_pagamento(
            MetodoPagamento.CARTAO_CREDITO, 7, Periodicidade.MENSAL, 200.0
        )

        # Assert: 5% de juros sobre 200 = R$ 10,00; total = R$ 210,00
        assert ajuste == 10.0
        assert total == 210.0


@pytest.mark.unit
class TestCalcularPontosFidelidade:
    """Testes de conversão de fidelidade por categoria de plano (RF08).

    Técnica: Análise do Valor Limite (BVA).
    Regras:
    - Bronze: 1 ponto a cada R$ 20,00 gastos
    - Prata: 1 ponto a cada R$ 15,00 gastos
    - Ouro: 1 ponto a cada R$ 10,00 gastos
    """

    @pytest.mark.parametrize(
        "plano, valor_pago, pontos_esperados",
        [
            # Limite inferior Bronze: R$ 19,99 não atinge 1 ponto
            (Plano.BRONZE, 19.99, 0),
            # Fronteira exata Bronze: R$ 20,00 converte para 1 ponto
            (Plano.BRONZE, 20.00, 1),
            # Fronteira Prata: R$ 15,00 converte para 1 ponto
            (Plano.PRATA, 15.00, 1),
            # Fronteira Ouro: R$ 10,00 converte para 1 ponto
            (Plano.OURO, 10.00, 1),
        ],
    )
    def test_pontos_fidelidade_bva(self, plano: Plano, valor_pago: float, pontos_esperados: int):
        """Objetivo: Garantir conversão inteira precisa de pontos por plano e valor efetivamente pago."""
        # Arrange & Act: Converte valor pago em pontos de fidelidade
        pontos = calcular_pontos_fidelidade(plano, valor_pago)

        # Assert: Quantidade de pontos inteiros acumulados
        assert pontos == pontos_esperados
