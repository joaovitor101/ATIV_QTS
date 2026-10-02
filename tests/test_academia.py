import pytest
from app.academia import AvaliadorAcademia


# ================= Testes parametrizados =====================
@pytest.mark.unit
@pytest.mark.parametrize(
    "valor_base, dependentes, cupom_desconto, valor_dependente, esperado",
    [
        (100.0, 1, 0.0, 50.0, 150.0),
        (100.0, 2, 0.0, 50.0, 200.0),
        (200.0, 1, 10.0, 50.0, 225.0),
        (150.0, 3, 20.0, 50.0, 240.0),
    ]
)

# ================= Padrão AAA =======================
def test_calcular_mensalidade_sucesso(valor_base, dependentes, cupom_desconto, valor_dependente, esperado):
    # Arrange & Act
    resultado = AvaliadorAcademia.calcular_mensalidade(valor_base, dependentes, cupom_desconto, valor_dependente)
    
    # Assert
    assert resultado == esperado

# ================= Testes parametrizados =====================

@pytest.mark.unit
@pytest.mark.parametrize(
    "valor_base, dependentes, cupom_desconto, expected_categoria",
    [
        (200.0, 0, 0.0, "Plano Ouro"),
        (1000.0, 0, 0.0, "Plano Ouro"),
        (199.0, 0, 0.0, "Plano Prata"),
        (120.0, 0, 0.0, "Plano Prata"),
        (119.0, 0, 0.0, "Plano Bronze"),
        (60.0, 0, 0.0, "Plano Bronze"),
    ]
)

# ================= Análise de Limites ======================
def test_determinar_categoria_limites_e_ep(valor_base, dependentes, cupom_desconto, expected_categoria):
    # Arrange
    mensalidade = AvaliadorAcademia.calcular_mensalidade(valor_base, dependentes, cupom_desconto)
    
    # Act
    categoria = AvaliadorAcademia.determinar_categoria_plano(mensalidade)
    
    # Assert
    assert categoria == expected_categoria


# ===================== Error Guessing ==========================
@pytest.mark.unit
@pytest.mark.parametrize(
    "valor_base, dependentes, cupom_desconto",
    [
        (59.9, 0, 0.0),
        (1000.1, 0, 0.0),
        (100.0, -1, 0.0),
        (100.0, 6, 0.0),
        (100.0, 0, -0.1),
        (100.0, 0, 50.1),
    ]
)
def test_error_guessing_valores_fora_dos_limites(valor_base, dependentes, cupom_desconto):
    with pytest.raises(ValueError):
        AvaliadorAcademia.calcular_mensalidade(valor_base, dependentes, cupom_desconto)


@pytest.mark.unit
@pytest.mark.parametrize(
    "valor_base, dependentes, cupom_desconto",
    [
        ("100", 0, 0.0),
        (100.0, "2", 0.0),
        (100.0, 1.5, 0.0),
        (100.0, 0, None),
        (None, 0, 0.0),
        (100.0, 0, [10.0]),
    ]
)
def test_error_guessing_tipos_invalidos_mensalidade(valor_base, dependentes, cupom_desconto):
    with pytest.raises(TypeError):
        AvaliadorAcademia.calcular_mensalidade(valor_base, dependentes, cupom_desconto)


@pytest.mark.unit
@pytest.mark.parametrize(
    "valor_dependente, tipo_erro",
    [
        (-10.0, ValueError),
        (0.0, ValueError),
        ("50", TypeError),
    ]
)
def test_error_guessing_valor_dependente_invalido(valor_dependente, tipo_erro):
    with pytest.raises(tipo_erro):
        AvaliadorAcademia.calcular_mensalidade(100.0, 1, valor_dependente=valor_dependente)


@pytest.mark.unit
@pytest.mark.parametrize(
    "mensalidade_invalida",
    [-0.1, 59.9, 1000.1, "150.0", None]
)
def test_error_guessing_categoria_invalida(mensalidade_invalida):
    if isinstance(mensalidade_invalida, str) or mensalidade_invalida is None:
        with pytest.raises(TypeError):
            AvaliadorAcademia.determinar_categoria_plano(mensalidade_invalida)
    else:
        with pytest.raises(ValueError):
            AvaliadorAcademia.determinar_categoria_plano(mensalidade_invalida)
