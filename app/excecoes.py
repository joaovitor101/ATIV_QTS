"""Exceções de domínio do sistema FitPlan em português."""


class ErroFitPlan(Exception):
    """Exceção base para todas as falhas de domínio do FitPlan."""

    pass


class ErroAlunoInvalido(ErroFitPlan):
    """Lançada quando os dados cadastrais do aluno são inconsistentes."""

    pass


class ErroDependenteInvalido(ErroFitPlan):
    """Lançada quando os dados de um dependente são inconsistentes."""

    pass


class ErroLimiteDependentesExcedido(ErroFitPlan):
    """Lançada quando a quantidade de dependentes excede o teto contratual."""

    pass


class ErroCupomInvalido(ErroFitPlan):
    """Lançada quando um cupom é inválido, expirado ou não cumpre regras de ativação."""

    pass


class ErroMetodoPagamentoInvalido(ErroFitPlan):
    """Lançada quando a forma de pagamento ou parcelamento é inválida."""

    pass
