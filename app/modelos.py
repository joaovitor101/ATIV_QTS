"""Modelos de dados e validações defensivas do sistema FitPlan em português."""

import re
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.excecoes import (
    ErroAlunoInvalido,
    ErroDependenteInvalido,
    ErroLimiteDependentesExcedido,
)

PADRAO_EMAIL = r"^[\w\.-]+@[\w\.-]+\.\w+$"


class Plano(str, Enum):
    """Categorias de plano da academia."""

    BRONZE = "BRONZE"
    PRATA = "PRATA"
    OURO = "OURO"


class HorarioAcesso(str, Enum):
    """Modalidades de acesso por horário na academia."""

    FORA_PICO = "FORA_PICO"
    LIVRE = "LIVRE"
    PICO_VIP = "PICO_VIP"


class Periodicidade(str, Enum):
    """Periodicidade do contrato de assinatura."""

    MENSAL = "MENSAL"
    SEMESTRAL = "SEMESTRAL"
    ANUAL = "ANUAL"


class MetodoPagamento(str, Enum):
    """Métodos de pagamento disponíveis."""

    PIX = "PIX"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    BOLETO = "BOLETO"


class Dependente(BaseModel):
    """Representação de um dependente no contrato familiar."""

    nome: str
    parentesco: str
    idade: int

    @field_validator("nome", mode="before")
    @classmethod
    def validar_nome(cls, valor: Any) -> str:
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ErroDependenteInvalido("Nome do dependente deve ter no mínimo 2 caracteres.")
        return valor.strip()

    @field_validator("parentesco", mode="before")
    @classmethod
    def validar_parentesco(cls, valor: Any) -> str:
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ErroDependenteInvalido("Parentesco deve ser preenchido.")
        return valor.strip()

    @field_validator("idade", mode="before")
    @classmethod
    def validar_idade(cls, valor: Any) -> int:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 12 or valor > 100:
            raise ErroDependenteInvalido("Idade do dependente deve estar entre 12 e 100 anos.")
        return valor


class Aluno(BaseModel):
    """Dados cadastrais defensivos do aluno titular."""

    nome: str
    cpf: str
    email: str
    idade: int

    @field_validator("nome", mode="before")
    @classmethod
    def validar_nome(cls, valor: Any) -> str:
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ErroAlunoInvalido("Nome do aluno deve ter no mínimo 2 caracteres.")
        return valor.strip()

    @field_validator("cpf", mode="before")
    @classmethod
    def validar_cpf(cls, valor: Any) -> str:
        if not valor or not isinstance(valor, str):
            raise ErroAlunoInvalido("CPF não pode ser vazio.")
        digitos = re.sub(r"\D", "", valor)
        if len(digitos) != 11:
            raise ErroAlunoInvalido("CPF deve conter exatamente 11 dígitos numéricos.")
        if len(set(digitos)) == 1:
            raise ErroAlunoInvalido("CPF não pode conter todos os dígitos iguais.")
        return digitos

    @field_validator("email", mode="before")
    @classmethod
    def validar_email(cls, valor: Any) -> str:
        if not valor or not isinstance(valor, str) or not re.match(PADRAO_EMAIL, valor):
            raise ErroAlunoInvalido("Formato de e-mail inválido.")
        return valor.strip().lower()

    @field_validator("idade", mode="before")
    @classmethod
    def validar_idade(cls, valor: Any) -> int:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < 12 or valor > 100:
            raise ErroAlunoInvalido("Idade do aluno deve estar entre 12 e 100 anos.")
        return valor


class EntradaAssinatura(BaseModel):
    """Dados de entrada para processar a adesão de uma assinatura."""

    aluno: Aluno
    plano: Plano
    horario: HorarioAcesso
    periodicidade: Periodicidade
    dependentes: list[Dependente] = Field(default_factory=list)
    cupom: Optional[str] = None
    metodo_pagamento: MetodoPagamento
    parcelas: int = 1

    @field_validator("dependentes")
    @classmethod
    def validar_limite_dependentes(cls, lista_deps: list[Dependente]) -> list[Dependente]:
        if len(lista_deps) > 5:
            raise ErroLimiteDependentesExcedido("Máximo permitido de 5 dependentes por plano.")
        return lista_deps


class ResumoAssinatura(BaseModel):
    """Detalhamento financeiro e cadastral emitido após adesão."""

    aluno_nome: str
    plano: Plano
    mensalidade_base_titular: float
    ajuste_horario: float
    valor_dependentes_bruto: float
    desconto_pacote_familia: float
    valor_dependentes_liquido: float
    desconto_periodicidade: float
    desconto_cupom: float
    codigo_cupom: Optional[str]
    taxa_matricula: float
    mensalidade_final: float
    ajuste_pagamento: float
    primeiro_pagamento_total: float
    pontos_fidelidade: int
    status: str = "ATIVO"
