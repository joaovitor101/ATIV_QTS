"""Testes integrados de ponta a ponta do serviço de assinaturas (FitPlan).

Este módulo valida o orquestrador `processar_assinatura`, testando cenários
completos de contratação que combinam múltiplos motores determinísticos:
preços base, horários de acesso, dependentes, periodicidade, cupons e pagamentos.
"""

import pytest
from app.modelos import (
    Aluno,
    Dependente,
    EntradaAssinatura,
    HorarioAcesso,
    MetodoPagamento,
    Periodicidade,
    Plano,
)
from app.servico_assinatura import processar_assinatura


@pytest.mark.unit
class TestServicoAssinatura:
    """Validação da orquestração completa do ciclo de assinatura e matrícula."""

    def test_fluxo_simples_bronze_pix_mensal(self, aluno_valido: Aluno):
        """Cenário 1: Fluxo Básico de Entrada
        - Plano: Bronze (R$ 90,00)
        - Horário: Livre (0% de ajuste)
        - Periodicidade: Mensal (0% de desconto)
        - Dependentes: Nenhum
        - Cupom: Nenhum (Taxa de matrícula padrão: R$ 80,00)
        - Pagamento: PIX (5% de desconto financeiro no 1º pagamento)
        - Fidelidade: Bronze (1 ponto a cada R$ 20,00)
        """
        # Arrange: Configura a requisição de assinatura básica
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

        # Act: Orquestra o processamento completo da adesão
        resumo = processar_assinatura(assinatura)

        # Assert:
        # 1. Mensalidade titular: 90.00
        # 2. Taxa de matrícula: 80.00
        # 3. Base do 1º pagamento: 90.00 + 80.00 = 170.00
        # 4. Desconto PIX 5%: 5% de 170.00 = 8.50
        # 5. Total a pagar no 1º pagamento: 170.00 - 8.50 = 161.50
        # 6. Pontos Bronze: 161.50 // 20 = 8 pontos
        assert resumo.aluno_nome == aluno_valido.nome
        assert resumo.plano == Plano.BRONZE
        assert resumo.mensalidade_base_titular == 90.00
        assert resumo.ajuste_horario == 0.00
        assert resumo.valor_dependentes_bruto == 0.00
        assert resumo.desconto_pacote_familia == 0.00
        assert resumo.valor_dependentes_liquido == 0.00
        assert resumo.desconto_periodicidade == 0.00
        assert resumo.desconto_cupom == 0.00
        assert resumo.codigo_cupom is None
        assert resumo.taxa_matricula == 80.00
        assert resumo.mensalidade_final == 90.00
        assert resumo.ajuste_pagamento == -8.50
        assert resumo.primeiro_pagamento_total == 161.50
        assert resumo.pontos_fidelidade == 8
        assert resumo.status == "ATIVO"

    def test_fluxo_ouro_vip_com_dependentes_anual_matriculagratis_boleto(
        self, aluno_valido: Aluno
    ):
        """Cenário 2: Fluxo Avançado Premium
        - Plano: Ouro (R$ 200,00) + Horário VIP (+R$ 30,00) = R$ 230,00
        - Dependentes: 3 dependentes (3 * R$ 130,00 = R$ 390,00) com desconto família 20% (-R$ 78,00) = R$ 312,00
        - Subtotal mensal: R$ 230,00 + R$ 312,00 = R$ 542,00
        - Periodicidade: Anual (12% de desconto no valor mensal = -R$ 65,04) -> Mensalidade: R$ 476,96
        - Cupom: MATRICULAGRATIS (taxa de matrícula zerada: R$ 0,00)
        - Pagamento: Boleto à vista em contrato anual (3% de desconto = -R$ 14,31)
        - Fidelidade: Ouro (1 ponto a cada R$ 10,00 pagos)
        """
        # Arrange: 3 dependentes e contrato anual no plano Ouro
        deps = [
            Dependente(nome=f"Dep {i}", parentesco="Filho", idade=16 + i)
            for i in range(1, 4)
        ]
        assinatura = EntradaAssinatura(
            aluno=aluno_valido,
            plano=Plano.OURO,
            horario=HorarioAcesso.PICO_VIP,
            periodicidade=Periodicidade.ANUAL,
            dependentes=deps,
            cupom="MATRICULAGRATIS",
            metodo_pagamento=MetodoPagamento.BOLETO,
            parcelas=1,
        )

        # Act: Orquestra o processamento completo
        resumo = processar_assinatura(assinatura)

        # Assert:
        # Base 1º pagamento: 476.96 + 0.00 = 476.96
        # Desconto Boleto 3%: 3% de 476.96 = 14.31
        # Total a pagar: 476.96 - 14.31 = 462.65
        # Pontos Ouro: 462.65 // 10 = 46 pontos
        assert resumo.mensalidade_base_titular == 200.00
        assert resumo.ajuste_horario == 30.00
        assert resumo.valor_dependentes_bruto == 390.00
        assert resumo.desconto_pacote_familia == 78.00
        assert resumo.valor_dependentes_liquido == 312.00
        assert resumo.desconto_periodicidade == 65.04
        assert resumo.taxa_matricula == 0.00
        assert resumo.codigo_cupom == "MATRICULAGRATIS"
        assert resumo.mensalidade_final == 476.96
        assert resumo.ajuste_pagamento == -14.31
        assert resumo.primeiro_pagamento_total == 462.65
        assert resumo.pontos_fidelidade == 46

    def test_fluxo_prata_fora_pico_com_amigo20_cartao_sem_juros(
        self, aluno_valido: Aluno, dependente_valido: Dependente
    ):
        """Cenário 3: Fluxo Familiar Semestral com Cupom Condicional
        - Plano: Prata (R$ 140,00) + Fora de Pico (-15% = -R$ 21,00) = R$ 119,00
        - Dependentes: 1 dependente (R$ 90,00, 0% desconto pacote) = R$ 90,00
        - Subtotal mensal: R$ 119,00 + R$ 90,00 = R$ 209,00
        - Periodicidade: Semestral (5% de desconto = -R$ 10,45) -> R$ 198,55
        - Cupom: AMIGO20 (20% de desconto sobre mensalidade = -R$ 39,71) -> Mensalidade final: R$ 158,84
        - Taxa de matrícula: R$ 80,00
        - Pagamento: Cartão de Crédito em 4x (dentro do limite de 6x sem juros = 0%)
        - Fidelidade: Prata (1 ponto a cada R$ 15,00 pagos)
        """
        # Arrange: 1 dependente, cupom AMIGO20 e cartão em 4x
        assinatura = EntradaAssinatura(
            aluno=aluno_valido,
            plano=Plano.PRATA,
            horario=HorarioAcesso.FORA_PICO,
            periodicidade=Periodicidade.SEMESTRAL,
            dependentes=[dependente_valido],
            cupom="AMIGO20",
            metodo_pagamento=MetodoPagamento.CARTAO_CREDITO,
            parcelas=4,
        )

        # Act: Orquestra o processamento
        resumo = processar_assinatura(assinatura)

        # Assert:
        # Base 1º pagamento: 158.84 + 80.00 = 238.84
        # Cartão 4x sem juros: ajuste = 0.00; total = 238.84
        # Pontos Prata: 238.84 // 15 = 15 pontos
        assert resumo.mensalidade_base_titular == 140.00
        assert resumo.ajuste_horario == -21.00
        assert resumo.valor_dependentes_bruto == 90.00
        assert resumo.desconto_pacote_familia == 0.00
        assert resumo.valor_dependentes_liquido == 90.00
        assert resumo.desconto_periodicidade == 10.45
        assert resumo.desconto_cupom == 39.71
        assert resumo.codigo_cupom == "AMIGO20"
        assert resumo.taxa_matricula == 80.00
        assert resumo.mensalidade_final == 158.84
        assert resumo.ajuste_pagamento == 0.00
        assert resumo.primeiro_pagamento_total == 238.84
        assert resumo.pontos_fidelidade == 15

    def test_fluxo_prata_verao10_cartao_com_juros(
        self, aluno_valido: Aluno
    ):
        """Cenário 4: Fluxo com Cupom Geral e Parcelamento com Juros
        - Plano: Prata (R$ 140,00) + Horário Livre (R$ 0,00) = R$ 140,00
        - Dependentes: Nenhum (R$ 0,00)
        - Periodicidade: Mensal (0% de desconto) = R$ 140,00
        - Cupom: VERAO10 (10% de desconto = -R$ 14,00) -> Mensalidade final: R$ 126,00
        - Taxa de matrícula: R$ 80,00
        - Base 1º pagamento: R$ 126,00 + R$ 80,00 = R$ 206,00
        - Pagamento: Cartão de Crédito em 10x (faixa de 7 a 12x aplica 5% de juros = +R$ 10,30)
        - Fidelidade: Prata (1 ponto a cada R$ 15,00 pagos)
        """
        # Arrange: Cartão em 10 parcelas com cupom VERAO10
        assinatura = EntradaAssinatura(
            aluno=aluno_valido,
            plano=Plano.PRATA,
            horario=HorarioAcesso.LIVRE,
            periodicidade=Periodicidade.MENSAL,
            dependentes=[],
            cupom="VERAO10",
            metodo_pagamento=MetodoPagamento.CARTAO_CREDITO,
            parcelas=10,
        )

        # Act: Orquestra o processamento
        resumo = processar_assinatura(assinatura)

        # Assert:
        # Total a pagar: 206.00 + 10.30 = 216.30
        # Pontos Prata: 216.30 // 15 = 14 pontos
        assert resumo.desconto_cupom == 14.00
        assert resumo.codigo_cupom == "VERAO10"
        assert resumo.taxa_matricula == 80.00
        assert resumo.mensalidade_final == 126.00
        assert resumo.ajuste_pagamento == 10.30
        assert resumo.primeiro_pagamento_total == 216.30
        assert resumo.pontos_fidelidade == 14
