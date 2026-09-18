from datetime import date, timedelta
from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field
from bancodados import (
    inserir_transacao,
    atualizar_transacao,
    deletar_transacao,
    listar_transacoes,
    buscar_id_por_usuario,
    inserir_categoria_personalizada,
    listar_categorias_personalizadas,
)

from autenticacoes import autenticar_transacao, autenticar_categoria, CATEGORIAS_RECEITA, CATEGORIAS_DESPESA
from calculo import calcular_transacoes

from typing import Optional

router = APIRouter(tags=["Transações"])

class CategoriaSchema(BaseModel):
    usuario: str
    tipo: str
    nome: str

class TransacaoSchema(BaseModel):
    usuario: str
    tipo: str
    categoria: str
    valor: float
    data: Optional[str] = Field(default_factory=lambda: date.today().isoformat())
    status: str = "pago"

class AtualizarTransacaoSchema(BaseModel):
    usuario: str
    transacao_id: int
    tipo: str
    categoria: str
    valor: float
    data: Optional[str] = Field(default_factory=lambda: date.today().isoformat())
    status: str = "pago"

class DeletarTransacaoSchema(BaseModel):
    usuario: str
    transacao_id: int

@router.get("/categorias")
def obter_categorias(usuario: Optional[str] = None):
    personalizadas_receita = []
    personalizadas_despesa = []

    if usuario:
        usuario_id = buscar_id_por_usuario(usuario.strip().lower())
        if usuario_id:
            for tipo, nome in listar_categorias_personalizadas(usuario_id):
                if tipo == "receita":
                    personalizadas_receita.append(nome)
                elif tipo == "despesa":
                    personalizadas_despesa.append(nome)

    return {
        "receita": CATEGORIAS_RECEITA + personalizadas_receita,
        "despesa": CATEGORIAS_DESPESA + personalizadas_despesa,
        "personalizadas": {
            "receita": personalizadas_receita,
            "despesa": personalizadas_despesa,
        },
    }

@router.post("/categorias/criar")
def criar_categoria_personalizada(dados: CategoriaSchema):
    usuario_id = buscar_id_por_usuario(dados.usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")

    tipo = dados.tipo.strip().lower()
    nome_formatado = dados.nome.strip().capitalize()

    if not autenticar_categoria(tipo, nome_formatado):
        raise HTTPException(status_code=400, detail="Nome de categoria inválido.")

    categorias_fixas = CATEGORIAS_RECEITA if tipo in ["receita", "entrada", "ganhos"] else CATEGORIAS_DESPESA
    if nome_formatado in categorias_fixas:
        raise HTTPException(status_code=400, detail="Essa categoria já existe.")

    tipo_normalizado = "receita" if tipo in ["receita", "entrada", "ganhos"] else "despesa"
    inserir_categoria_personalizada(usuario_id, tipo_normalizado, nome_formatado)

    return {
        "mensagem": "Categoria criada com sucesso!",
        "tipo": tipo_normalizado,
        "nome": nome_formatado,
    }

@router.post("/transacoes/criar")
def criar_transacao(dados: TransacaoSchema):

    categoria_formatada = dados.categoria.strip().capitalize()

    usuario_id = buscar_id_por_usuario(dados.usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")
    
    if not autenticar_transacao(dados.valor):
        raise HTTPException(status_code=400, detail="Valor da transação inválido.")

    if not autenticar_categoria(dados.tipo, dados.categoria):
        raise HTTPException(status_code=400, detail=f"Categoria '{dados.categoria}' inválida para o tipo '{dados.tipo}'.")

    inserir_transacao(usuario_id, dados.tipo, categoria_formatada, dados.valor, dados.data, dados.status)

    return {
        "usuario": dados.usuario,
        "valor": dados.valor,
        "tipo": dados.tipo,
        "categoria": categoria_formatada,
        "data": dados.data,
        "status": dados.status
    }

@router.get("/transacoes/listar")
def obter_transacoes(usuario: str):
    
    usuario_id = buscar_id_por_usuario(usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")
    
    dados = listar_transacoes(usuario_id)
    transacoes_lista = [
        {
            "id": t[0], "tipo": t[2], "categoria": t[3], 
            "valor": t[4], "data": t[5], "status": t[6]
        } for t in dados
    ]
    return {"transacoes": transacoes_lista}

@router.get("/transacoes/resumo")
def obter_resumo(usuario: str):

    usuario_id = buscar_id_por_usuario(usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")
    
    dados = listar_transacoes(usuario_id)
    return calcular_transacoes(dados)

@router.put("/transacoes/atualizar")
def atualizar_transacao_endpoint(dados: AtualizarTransacaoSchema):

    categoria_formatada = dados.categoria.strip().capitalize()

    usuario_id = buscar_id_por_usuario(dados.usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")
    
    if not autenticar_transacao(dados.valor):
        raise HTTPException(status_code=400, detail="Valor inválido.")

    if not autenticar_categoria(dados.tipo, categoria_formatada):
        raise HTTPException(status_code=400, detail="Categoria inválida.")

    atualizar_transacao(dados.transacao_id, dados.tipo, categoria_formatada, dados.valor, dados.data, dados.status)

    return {
        "transacao_id": dados.transacao_id, 
        "valor": dados.valor, 
        "tipo": dados.tipo, 
        "categoria": categoria_formatada, 
        "data": dados.data, 
        "status": dados.status
    }

@router.delete("/transacoes/deletar")
def deletar_transacao_endpoint(dados: DeletarTransacaoSchema):
    usuario_id = buscar_id_por_usuario(dados.usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")
    
    deletar_transacao(dados.transacao_id)
    return {"transacao_id": dados.transacao_id, "mensagem": "Transação excluída com sucesso."}
