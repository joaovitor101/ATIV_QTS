"""Testes unitários dos modelos de dados e validações defensivas do FitPlan."""

import pytest
from app.excecoes import (
    ErroAlunoInvalido,
    ErroDependenteInvalido,
    ErroLimiteDependentesExcedido,
)
from app.modelos import (
    Aluno,
    Dependente,
    EntradaAssinatura,
    HorarioAcesso,
    MetodoPagamento,
    Periodicidade,
    Plano,
    ResumoAssinatura,
)


@pytest.mark.unit
class TestModeloDependente:
    """Validações defensivas para a entidade Dependente (RF02).

    Técnicas: Particionamento de Equivalência, BVA e Adivinhação de Erros.
    Regras:
    - Nome: mínimo 2 caracteres não vazios
    - Parentesco: preenchido obrigatoriamente
    - Idade: entre 12 e 100 anos (limite operacional da academia)
    """

    def test_criar_dependente_valido(self):
        """Objetivo: Validar instanciação com sucesso de um dependente com dados válidos."""
        # Arrange & Act: Cria dependente com dados válidos
        dep = Dependente(nome="Beatriz Lima", parentesco="Filha", idade=15)

        # Assert: Confirma a integridade dos atributos
        assert dep.nome == "Beatriz Lima"
        assert dep.parentesco == "Filha"
        assert dep.idade == 15

    def test_dependente_nome_invalido_adivinhacao_erros(self):
        """Objetivo: Adivinhação de Erros para nome vazio de dependente (< 2 caracteres)."""
        # Arrange, Act & Assert: String vazia deve disparar ErroDependenteInvalido
        with pytest.raises(ErroDependenteInvalido, match="Nome do dependente deve ter no mínimo 2 caracteres."):
            Dependente(nome="", parentesco="Irmão", idade=20)

    def test_dependente_parentesco_invalido(self):
        """Objetivo: Validar que campo de parentesco não pode ser vazio ou nulo."""
        # Arrange, Act & Assert: Parentesco vazio dispara erro
        with pytest.raises(ErroDependenteInvalido, match="Parentesco deve ser preenchido."):
            Dependente(nome="Carlos", parentesco="", idade=20)

    @pytest.mark.parametrize("idade_invalida", [11, 101])
    def test_dependente_idade_limites_bva(self, idade_invalida: int):
        """Objetivo: BVA nas fronteiras inválidas de idade (11 anos = muito jovem; 101 anos = acima do teto)."""
        # Arrange, Act & Assert: Idades fora de [12, 100] disparam erro
        with pytest.raises(ErroDependenteInvalido, match="Idade do dependente deve estar entre 12 e 100 anos."):
            Dependente(nome="Carlos", parentesco="Irmão", idade=idade_invalida)

    @pytest.mark.parametrize("idade_valida", [12, 100])
    def test_dependente_idade_fronteiras_validas_bva(self, idade_valida: int):
        """Objetivo: BVA nas fronteiras válidas de idade (12 anos = limite inferior; 100 anos = limite superior)."""
        # Arrange & Act: Cria dependente nas idades extremas válidas
        dep = Dependente(nome="Carlos", parentesco="Irmão", idade=idade_valida)

        # Assert: Dependente deve ser criado com a idade exata
        assert dep.idade == idade_valida


@pytest.mark.unit
class TestModeloAluno:
    """Validações defensivas para a entidade Aluno Titular (RF01).

    Técnicas: Particionamento de Equivalência, BVA e Adivinhação de Erros.
    Regras:
    - Nome: mínimo 2 caracteres não vazios
    - CPF: 11 dígitos numéricos, não nulo e sem dígitos todos iguais
    - E-mail: formato sintático válido (com @ e domínio)
    - Idade: entre 12 e 100 anos
    """

    def test_criar_aluno_valido(self):
        """Objetivo: Validar instanciação com sucesso de um aluno titular válido."""
        # Arrange & Act: Cria aluno com dados válidos e formatação com pontuação
        aluno = Aluno(nome="Mariana Castro", cpf="123.456.789-01", email="mariana@email.com", idade=30)

        # Assert: CPF deve ser sanitizado (apenas números) e e-mail em minúsculas
        assert aluno.nome == "Mariana Castro"
        assert aluno.cpf == "12345678901"
        assert aluno.email == "mariana@email.com"
        assert aluno.idade == 30

    def test_aluno_nome_invalido_adivinhacao_erros(self):
        """Objetivo: Adivinhação de Erros para nome de aluno vazio ou com apenas espaços em branco."""
        # Arrange, Act & Assert: Dispara ErroAlunoInvalido
        with pytest.raises(ErroAlunoInvalido, match="Nome do aluno deve ter no mínimo 2 caracteres."):
            Aluno(nome="", cpf="12345678901", email="teste@email.com", idade=25)

    def test_aluno_cpf_vazio(self):
        """Objetivo: Validar que CPF nulo é rejeitado defensivamente."""
        # Arrange, Act & Assert: CPF nulo dispara erro
        with pytest.raises(ErroAlunoInvalido, match="CPF não pode ser vazio."):
            Aluno(nome="Aluno Teste", cpf=None, email="teste@email.com", idade=25)

    @pytest.mark.parametrize("cpf_tamanho_invalido", ["1234567890", "123456789012"])
    def test_aluno_cpf_comprimento_invalido_bva(self, cpf_tamanho_invalido: str):
        """Objetivo: BVA no tamanho do CPF (10 dígitos = curto demais; 12 dígitos = longo demais)."""
        # Arrange, Act & Assert: Tamanho diferente de 11 dígitos numéricos dispara erro
        with pytest.raises(ErroAlunoInvalido, match="CPF deve conter exatamente 11 dígitos numéricos."):
            Aluno(nome="Aluno Teste", cpf=cpf_tamanho_invalido, email="teste@email.com", idade=25)

    def test_aluno_cpf_digitos_iguais_adivinhacao_erros(self):
        """Objetivo: Adivinhação de Erros para CPFs com dígitos todos repetidos (ex.: '11111111111')."""
        # Arrange, Act & Assert: CPF de dígitos repetidos deve ser rejeitado
        with pytest.raises(ErroAlunoInvalido, match="CPF não pode conter todos os dígitos iguais."):
            Aluno(nome="Aluno Teste", cpf="11111111111", email="teste@email.com", idade=25)

    def test_aluno_email_invalido(self):
        """Objetivo: Validar rejeição de e-mail malformado sem estrutura de domínio."""
        # Arrange, Act & Assert: E-mail sem '@' dispara erro
        with pytest.raises(ErroAlunoInvalido, match="Formato de e-mail inválido."):
            Aluno(nome="Aluno Teste", cpf="12345678901", email="sem_arroba.com", idade=25)

    @pytest.mark.parametrize("idade_invalida", [11, 101])
    def test_aluno_idade_invalida_bva(self, idade_invalida: int):
        """Objetivo: BVA nas fronteiras inválidas de idade do aluno (11 anos e 101 anos)."""
        # Arrange, Act & Assert: Idade fora do intervalo permitido dispara erro
        with pytest.raises(ErroAlunoInvalido, match="Idade do aluno deve estar entre 12 e 100 anos."):
            Aluno(nome="Aluno Teste", cpf="12345678901", email="teste@email.com", idade=idade_invalida)

    @pytest.mark.parametrize("idade_valida", [12, 100])
    def test_aluno_idade_fronteiras_validas_bva(self, idade_valida: int):
        """Objetivo: BVA nas fronteiras válidas de idade do aluno (12 anos e 100 anos)."""
        # Arrange & Act: Cria aluno com idades extremas permitidas
        aluno = Aluno(nome="Aluno Teste", cpf="12345678901", email="teste@email.com", idade=idade_valida)

        # Assert: Instanciação bem-sucedida
        assert aluno.idade == idade_valida


@pytest.mark.unit
class TestModeloEntradaAssinatura:
    """Validações do modelo de entrada de assinatura e limite de dependentes (RF02).

    Técnica: Análise do Valor Limite (BVA).
    Regra: Cada aluno pode incluir até no máximo 5 dependentes no contrato.
    """

    def test_limite_maximo_dependentes_bva_sucesso(self, aluno_valido: Aluno):
        """Objetivo: BVA no limite superior permitido de dependentes (exatamente 5 dependentes)."""
        # Arrange: Cria lista com 5 dependentes válidos
        deps = [
            Dependente(nome=f"Dep {i}", parentesco="Filho", idade=18)
            for i in range(1, 6)
        ]

        # Act: Cria o objeto de assinatura
        assinatura = EntradaAssinatura(
            aluno=aluno_valido,
            plano=Plano.OURO,
            horario=HorarioAcesso.LIVRE,
            periodicidade=Periodicidade.MENSAL,
            dependentes=deps,
            metodo_pagamento=MetodoPagamento.PIX,
        )

        # Assert: A lista deve conter exatamente 5 dependentes
        assert len(assinatura.dependentes) == 5

    def test_limite_maximo_dependentes_bva_estourado(self, aluno_valido: Aluno):
        """Objetivo: BVA no valor imediatamente superior ao limite permitido (6 dependentes)."""
        # Arrange: Cria lista com 6 dependentes (estoura o limite contratual)
        deps = [
            Dependente(nome=f"Dep {i}", parentesco="Filho", idade=18)
            for i in range(1, 7)
        ]

        # Act & Assert: Deve lançar ErroLimiteDependentesExcedido
        with pytest.raises(ErroLimiteDependentesExcedido, match="Máximo permitido de 5 dependentes por plano."):
            EntradaAssinatura(
                aluno=aluno_valido,
                plano=Plano.OURO,
                horario=HorarioAcesso.LIVRE,
                periodicidade=Periodicidade.MENSAL,
                dependentes=deps,
                metodo_pagamento=MetodoPagamento.PIX,
            )


@pytest.mark.unit
class TestModeloResumoAssinatura:
    """Validação da estrutura do resumo financeiro emitido após a adesão."""

    def test_resumo_assinatura_campos_e_status(self):
        """Objetivo: Garantir que o resumo contenha todos os atributos financeiros e status 'ATIVO'."""
        # Arrange & Act: Instancia o resumo com valores consolidados
        resumo = ResumoAssinatura(
            aluno_nome="Carlos Silva",
            plano=Plano.BRONZE,
            mensalidade_base_titular=90.0,
            ajuste_horario=0.0,
            valor_dependentes_bruto=0.0,
            desconto_pacote_familia=0.0,
            valor_dependentes_liquido=0.0,
            desconto_periodicidade=0.0,
            desconto_cupom=0.0,
            codigo_cupom=None,
            taxa_matricula=80.0,
            mensalidade_final=90.0,
            ajuste_pagamento=-8.50,
            primeiro_pagamento_total=161.50,
            pontos_fidelidade=8,
        )

        # Assert: Confirma atributos chave
        assert resumo.aluno_nome == "Carlos Silva"
        assert resumo.plano == Plano.BRONZE
        assert resumo.taxa_matricula == 80.0
        assert resumo.primeiro_pagamento_total == 161.50
        assert resumo.pontos_fidelidade == 8
        assert resumo.status == "ATIVO"
