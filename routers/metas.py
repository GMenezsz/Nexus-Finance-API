from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from bancodados import (
    listar_metas,
    inserir_meta,
    atualizar_meta,
    deletar_meta,
    buscar_id_por_usuario,
    buscar_parcelas_meta,
    atualizar_parcelas_meta,
    buscar_anos_meta,
    alternar_parcela_meta,
)

router = APIRouter(prefix="/metas", tags=["Metas"])

MESES_POR_ANO = 12
ANOS_MINIMO = 1
ANOS_MAXIMO = 40

class MetaSchema(BaseModel):
    usuario: str
    titulo: str
    meta_total: float
    anos: int

class AtualizarMetaSchema(BaseModel):
    usuario: str
    titulo_antigo: str
    titulo_novo: str
    meta_total: float
    anos: int

class ParcelaSchema(BaseModel):
    usuario: str
    titulo: str
    indice: int

def _parse_parcelas(parcelas_str: str) -> List[int]:
    if not parcelas_str:
        return []
    return sorted(set(int(p) for p in parcelas_str.split(",") if p != ""))

def _meta_valida(meta_total: float) -> bool:
    return meta_total is not None and meta_total > 0

def _anos_valido(anos: int) -> bool:
    return isinstance(anos, int) and ANOS_MINIMO <= anos <= ANOS_MAXIMO

@router.post("/criar")
def criar_meta(dados: MetaSchema):
    usuario_id = buscar_id_por_usuario(dados.usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")

    titulo_formatado = dados.titulo.strip().title()

    if not _meta_valida(dados.meta_total):
        raise HTTPException(status_code=400, detail="Valor da meta inválido. Deve ser maior que zero.")

    if not _anos_valido(dados.anos):
        raise HTTPException(status_code=400, detail=f"Quantidade de anos inválida. Deve ser entre {ANOS_MINIMO} e {ANOS_MAXIMO}.")

    inserir_meta(usuario_id, titulo_formatado, dados.meta_total, dados.anos)

    total_parcelas = dados.anos * MESES_POR_ANO
    return {
        "mensagem": "Meta criada com sucesso!",
        "usuario": dados.usuario,
        "titulo": titulo_formatado,
        "meta_total": dados.meta_total,
        "anos": dados.anos,
        "total_parcelas": total_parcelas,
        "valor_parcela": dados.meta_total / total_parcelas,
    }

@router.put("/atualizar")
def atualizar_meta_existente(dados: AtualizarMetaSchema):
    usuario_id = buscar_id_por_usuario(dados.usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")

    titulo_antigo_formatado = dados.titulo_antigo.strip().title()
    titulo_formatado = dados.titulo_novo.strip().title()

    if not _meta_valida(dados.meta_total):
        raise HTTPException(status_code=400, detail="Valor da meta inválido. Deve ser maior que zero.")

    if not _anos_valido(dados.anos):
        raise HTTPException(status_code=400, detail=f"Quantidade de anos inválida. Deve ser entre {ANOS_MINIMO} e {ANOS_MAXIMO}.")

    # Editar a meta sempre zera as parcelas já marcadas (o valor de cada
    # parcela muda junto com o valor total/prazo da meta).
    atualizar_meta(usuario_id, titulo_antigo_formatado, titulo_formatado, dados.meta_total, dados.anos)

    total_parcelas = dados.anos * MESES_POR_ANO
    return {
        "mensagem": "Meta atualizada com sucesso! As parcelas guardadas foram zeradas.",
        "parcelas_zeradas": True,
        "usuario": dados.usuario,
        "titulo": titulo_formatado,
        "meta_total": dados.meta_total,
        "anos": dados.anos,
        "total_parcelas": total_parcelas,
        "valor_parcela": dados.meta_total / total_parcelas,
    }

@router.get("/listar")
def obter_metas(usuario: str):
    usuario_id = buscar_id_por_usuario(usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")

    dados = listar_metas(usuario_id)
    metas_lista = []
    for m in dados:
        anos = m[6] if len(m) > 6 and m[6] else ANOS_MINIMO
        meta_total = m[4]
        total_parcelas = anos * MESES_POR_ANO
        metas_lista.append({
            "id": m[0],
            "usuario_id": m[1],
            "titulo": m[2],
            "meta_total": meta_total,
            "anos": anos,
            "total_parcelas": total_parcelas,
            "valor_parcela": meta_total / total_parcelas if total_parcelas else 0,
            "parcelas": _parse_parcelas(m[5] if len(m) > 5 else "")
        })
    return {"metas": metas_lista}

@router.put("/parcela")
def marcar_parcela(dados: ParcelaSchema):

    usuario_id = buscar_id_por_usuario(dados.usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")

    titulo_formatado = dados.titulo.strip().title()

    anos = buscar_anos_meta(usuario_id, titulo_formatado) or ANOS_MINIMO
    total_parcelas = anos * MESES_POR_ANO

    if dados.indice < 0 or dados.indice >= total_parcelas:
        raise HTTPException(status_code=400, detail=f"Índice de parcela inválido. Deve ser entre 0 e {total_parcelas - 1}.")

    # Alterna: se já estava marcada, desmarca; se não estava, marca.
    parcelas_atualizadas, marcada = alternar_parcela_meta(usuario_id, titulo_formatado, dados.indice)

    return {
        "mensagem": "Parcela marcada como concluída!" if marcada else "Parcela desmarcada.",
        "marcada": marcada,
        "parcelas": parcelas_atualizadas
    }

@router.delete("/deletar")
def excluir_meta(usuario: str, titulo: str):
    usuario_id = buscar_id_por_usuario(usuario.strip().lower())
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")
    
    deletar_meta(usuario_id, titulo.strip().title())
    return {"mensagem": f"Meta '{titulo}' excluída com sucesso."}
