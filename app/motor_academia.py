"""Motor determinístico de cálculo de mensalidades, taxas e descontos do FitPlan."""

from typing import Optional

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

PRECO_BASE_PLANO = {
    Plano.BRONZE: 90.0,
    Plano.PRATA: 140.0,
    Plano.OURO: 200.0,
}

CUSTO_UNITARIO_DEPENDENTE = {
    Plano.BRONZE: 60.0,
    Plano.PRATA: 90.0,
    Plano.OURO: 130.0,
}

TAXA_MATRICULA_PADRAO = 80.0


def calcular_mensalidade_titular(plano: Plano, horario: HorarioAcesso) -> tuple[float, float]:
    """Calcula a mensalidade base do titular e o ajuste pelo horário de acesso."""
    base = PRECO_BASE_PLANO[plano]

    if horario == HorarioAcesso.FORA_PICO:
        ajuste = -round(base * 0.15, 2)
    elif horario == HorarioAcesso.PICO_VIP:
        ajuste = 30.0
    else:  # HorarioAcesso.LIVRE
        ajuste = 0.0

    return base, ajuste


def calcular_dependentes(
    plano: Plano, dependentes: list[Dependente]
) -> tuple[float, float, float]:
    """Calcula o custo bruto, desconto de pacote família e custo líquido dos dependentes."""
    total_deps = len(dependentes)
    if total_deps > 5:
        raise ErroLimiteDependentesExcedido("Máximo permitido de 5 dependentes por plano.")

    if total_deps == 0:
        return 0.0, 0.0, 0.0

    custo_unit = CUSTO_UNITARIO_DEPENDENTE[plano]
    bruto = round(total_deps * custo_unit, 2)

    if total_deps == 2:
        desconto = round(bruto * 0.10, 2)
    elif total_deps >= 3:
        desconto = round(bruto * 0.20, 2)
    else:
        desconto = 0.0

    liquido = round(bruto - desconto, 2)
    return bruto, desconto, liquido


def calcular_desconto_periodicidade(
    subtotal_mensal: float, periodicidade: Periodicidade
) -> float:
    """Calcula desconto contratual concedido por fidelidade de periodicidade."""
    if periodicidade == Periodicidade.SEMESTRAL:
        return round(subtotal_mensal * 0.05, 2)
    if periodicidade == Periodicidade.ANUAL:
        return round(subtotal_mensal * 0.12, 2)
    return 0.0


def calcular_taxa_matricula_e_cupom(
    cupom: Optional[str], plano: Plano, total_mensal: float, qtd_dependentes: int
) -> tuple[float, float, Optional[str]]:
    """Calcula taxa de matrícula e descontos promocionais aplicados por cupom."""
    if not cupom or not cupom.strip():
        return TAXA_MATRICULA_PADRAO, 0.0, None

    codigo = cupom.strip().upper()

    if codigo == "MATRICULAGRATIS":
        if plano == Plano.BRONZE:
            raise ErroCupomInvalido("Cupom MATRICULAGRATIS válido apenas para planos PRATA ou OURO.")
        return 0.0, 0.0, codigo

    if codigo == "VERAO10":
        desconto = round(total_mensal * 0.10, 2)
        return TAXA_MATRICULA_PADRAO, desconto, codigo

    if codigo == "AMIGO20":
        if qtd_dependentes == 0:
            raise ErroCupomInvalido("Cupom AMIGO20 exige ao menos 1 dependente.")
        desconto = round(total_mensal * 0.20, 2)
        return TAXA_MATRICULA_PADRAO, desconto, codigo

    raise ErroCupomInvalido(f"Cupom '{cupom}' inválido ou expirado.")


def calcular_ajuste_pagamento(
    metodo: MetodoPagamento,
    parcelas: int,
    periodicidade: Periodicidade,
    valor_base: float,
) -> tuple[float, float]:
    """Calcula desconto ou acréscimo de juros pelo método e parcelamento selecionados."""
    if metodo == MetodoPagamento.PIX:
        if parcelas != 1:
            raise ErroMetodoPagamentoInvalido("PIX permite apenas 1 parcela.")
        desconto = round(valor_base * 0.05, 2)
        return -desconto, round(valor_base - desconto, 2)

    if metodo == MetodoPagamento.BOLETO:
        if parcelas != 1:
            raise ErroMetodoPagamentoInvalido("Boleto permite apenas 1 parcela.")
        if periodicidade == Periodicidade.MENSAL:
            raise ErroMetodoPagamentoInvalido(
                "Boleto disponível apenas para planos semestrais ou anuais."
            )
        desconto = round(valor_base * 0.03, 2)
        return -desconto, round(valor_base - desconto, 2)

    # MetodoPagamento.CARTAO_CREDITO
    if not isinstance(parcelas, int) or parcelas < 1 or parcelas > 12:
        raise ErroMetodoPagamentoInvalido("Cartão de crédito aceita de 1 a 12 parcelas.")

    if parcelas <= 6:
        return 0.0, valor_base

    juros = round(valor_base * 0.05, 2)
    return juros, round(valor_base + juros, 2)


def calcular_pontos_fidelidade(plano: Plano, valor_pago: float) -> int:
    """Calcula pontos de fidelidade acumulados com base no valor pago e plano."""
    if plano == Plano.BRONZE:
        return int(valor_pago // 20)
    if plano == Plano.PRATA:
        return int(valor_pago // 15)
    return int(valor_pago // 10)
