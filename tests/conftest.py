"""Fixtures compartilhadas para a suíte de testes do FitPlan em português."""

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


@pytest.fixture
def aluno_valido() -> Aluno:
    """Fixture com dados válidos de um aluno titular."""
    return Aluno(
        nome="Lucas Andrade",
        cpf="12345678901",
        email="lucas.andrade@email.com",
        idade=28,
    )


@pytest.fixture
def dependente_valido() -> Dependente:
    """Fixture com dados válidos de um dependente."""
    return Dependente(
        nome="Camila Andrade",
        parentesco="Cônjuge",
        idade=26,
    )


@pytest.fixture
def assinatura_base(aluno_valido: Aluno) -> EntradaAssinatura:
    """Fixture com requisição de assinatura básica e válida."""
    return EntradaAssinatura(
        aluno=aluno_valido,
        plano=Plano.PRATA,
        horario=HorarioAcesso.LIVRE,
        periodicidade=Periodicidade.MENSAL,
        dependentes=[],
        cupom=None,
        metodo_pagamento=MetodoPagamento.PIX,
        parcelas=1,
    )
