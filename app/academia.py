"""Módulo de cálculo de planos e mensalidades da academia."""


class AvaliadorAcademia:
    """Calcula mensalidades e define a categoria do plano do aluno."""

    @staticmethod
    def calcular_mensalidade(
        valor_base: float,
        dependentes: int = 0,
        cupom_desconto: float = 0.0,
        valor_dependente: float = 50.0,
    ) -> float:
        """Calcula o valor final da mensalidade com adicionais e desconto."""
        # Validação dos tipos de entrada
        if type(valor_base) not in (int, float):
            raise TypeError("O valor base do plano deve ser numérico.")
        if type(dependentes) is not int:
            raise TypeError("A quantidade de dependentes deve ser um número inteiro.")
        if type(cupom_desconto) not in (int, float):
            raise TypeError("O cupom de desconto deve ser numérico.")
        if type(valor_dependente) not in (int, float):
            raise TypeError("O valor por dependente deve ser numérico.")

        # Validação dos limites permitidos
        if valor_base < 60.0 or valor_base > 1000.0:
            raise ValueError("O valor base deve ficar entre R$ 60,00 e R$ 1.000,00.")
        if dependentes < 0 or dependentes > 5:
            raise ValueError("A quantidade de dependentes deve ser de 0 a 5.")
        if cupom_desconto < 0.0 or cupom_desconto > 50.0:
            raise ValueError("O cupom de desconto deve ser de 0% a 50%.")
        if valor_dependente <= 0.0:
            raise ValueError("O valor por dependente deve ser maior que zero.")

        # Cálculo do valor final
        total_bruto = valor_base + (dependentes * valor_dependente)
        desconto = total_bruto * (cupom_desconto / 100.0)
        total_liquido = total_bruto - desconto

        return round(total_liquido, 2)

    @staticmethod
    def determinar_categoria_plano(mensalidade: float) -> str:
        """Classifica o plano entre Bronze, Prata ou Ouro com base no valor."""
        # Validação do tipo e limites
        if type(mensalidade) not in (int, float):
            raise TypeError("A mensalidade deve ser um valor numérico.")
        if mensalidade < 60.0 or mensalidade > 1000.0:
            raise ValueError("A mensalidade deve ficar entre R$ 60,00 e R$ 1.000,00.")

        # Faixas de classificação
        if mensalidade >= 200.0:
            return "Plano Ouro"
        if mensalidade >= 120.0:
            return "Plano Prata"
        return "Plano Bronze"
