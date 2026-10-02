"""Módulo de cálculo e avaliação de planos de academia (FitPlan)."""


class AvaliadorAcademia:
    """Motor simplificado para avaliação determinística de planos de academia."""

    @staticmethod
    def calcular_mensalidade(
        valor_base: float,
        dependentes: int = 0,
        cupom_desconto: float = 0.0,
        valor_dependente: float = 50.0,
    ) -> float:
        """Calcula o valor da mensalidade considerando dependentes e cupom de desconto.

        Args:
            valor_base: Valor base da mensalidade do plano (R$ 60,00 a R$ 1.000,00).
            dependentes: Quantidade de dependentes inclusos (0 a 5).
            cupom_desconto: Percentual de desconto de cupom promocional (0.0% a 50.0%).
            valor_dependente: Custo adicional por dependente (padrão R$ 50,00).

        Returns:
            Valor final da mensalidade arredondado em 2 casas decimais.
        """
        # ================= Validações de Tipo (TypeError) =================
        if type(valor_base) not in (int, float):
            raise TypeError("O valor base do plano deve ser numérico.")
        if type(dependentes) is not int:
            raise TypeError("A quantidade de dependentes deve ser um número inteiro.")
        if type(cupom_desconto) not in (int, float):
            raise TypeError("O cupom de desconto deve ser numérico.")
        if type(valor_dependente) not in (int, float):
            raise TypeError("O valor por dependente deve ser numérico.")

        # ================= Validações de Limite (ValueError) =================
        if valor_base < 60.0 or valor_base > 1000.0:
            raise ValueError("O valor base do plano deve estar entre R$ 60.0 e R$ 1000.0.")
        if dependentes < 0 or dependentes > 5:
            raise ValueError("A quantidade de dependentes deve estar entre 0 e 5.")
        if cupom_desconto < 0.0 or cupom_desconto > 50.0:
            raise ValueError("O cupom de desconto deve estar entre 0.0% e 50.0%.")
        if valor_dependente <= 0.0:
            raise ValueError("O valor por dependente deve ser maior que zero.")

        total_bruto = valor_base + (dependentes * valor_dependente)
        desconto = total_bruto * (cupom_desconto / 100.0)
        total_liquido = total_bruto - desconto

        return round(total_liquido, 2)

    @staticmethod
    def determinar_categoria_plano(mensalidade: float) -> str:
        """Determina a categoria do plano com base no valor da mensalidade.

        Args:
            mensalidade: Valor da mensalidade final calculada.

        Returns:
            Categoria correspondente: 'Plano Ouro', 'Plano Prata' ou 'Plano Bronze'.
        """
        # ================= Validações de Tipo (TypeError) =================
        if type(mensalidade) not in (int, float):
            raise TypeError("A mensalidade deve ser numérica.")

        # ================= Validações de Limite (ValueError) =================
        if mensalidade < 60.0 or mensalidade > 1000.0:
            raise ValueError("A mensalidade deve estar entre R$ 60.0 e R$ 1000.0.")

        if mensalidade >= 200.0:
            return "Plano Ouro"
        if mensalidade >= 120.0:
            return "Plano Prata"
        return "Plano Bronze"
