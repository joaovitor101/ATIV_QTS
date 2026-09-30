"""Serviço de orquestração de matrículas e assinaturas do FitPlan em português."""

from app.modelos import EntradaAssinatura, ResumoAssinatura
from app.motor_academia import (
    calcular_ajuste_pagamento,
    calcular_dependentes,
    calcular_desconto_periodicidade,
    calcular_mensalidade_titular,
    calcular_pontos_fidelidade,
    calcular_taxa_matricula_e_cupom,
)


def processar_assinatura(dados: EntradaAssinatura) -> ResumoAssinatura:
    """Orquestra o ciclo completo de cálculo e validação da assinatura."""
    base_titular, ajuste_horario = calcular_mensalidade_titular(
        dados.plano, dados.horario
    )
    titular_ajustado = round(base_titular + ajuste_horario, 2)

    deps_bruto, deps_desconto, deps_liquido = calcular_dependentes(
        dados.plano, dados.dependentes
    )

    subtotal_mensal = round(titular_ajustado + deps_liquido, 2)

    desc_periodicidade = calcular_desconto_periodicidade(
        subtotal_mensal, dados.periodicidade
    )
    total_pos_period = round(subtotal_mensal - desc_periodicidade, 2)

    taxa_matricula, desc_cupom, codigo_cupom = calcular_taxa_matricula_e_cupom(
        dados.cupom, dados.plano, total_pos_period, len(dados.dependentes)
    )

    mensalidade_final = round(total_pos_period - desc_cupom, 2)
    base_primeiro_pagamento = round(mensalidade_final + taxa_matricula, 2)

    ajuste_pagamento, total_primeiro_pagamento = calcular_ajuste_pagamento(
        dados.metodo_pagamento,
        dados.parcelas,
        dados.periodicidade,
        base_primeiro_pagamento,
    )

    pontos = calcular_pontos_fidelidade(dados.plano, total_primeiro_pagamento)

    return ResumoAssinatura(
        aluno_nome=dados.aluno.nome,
        plano=dados.plano,
        mensalidade_base_titular=base_titular,
        ajuste_horario=ajuste_horario,
        valor_dependentes_bruto=deps_bruto,
        desconto_pacote_familia=deps_desconto,
        valor_dependentes_liquido=deps_liquido,
        desconto_periodicidade=desc_periodicidade,
        desconto_cupom=desc_cupom,
        codigo_cupom=codigo_cupom,
        taxa_matricula=taxa_matricula,
        mensalidade_final=mensalidade_final,
        ajuste_pagamento=ajuste_pagamento,
        primeiro_pagamento_total=total_primeiro_pagamento,
        pontos_fidelidade=pontos,
        status="ATIVO",
    )
