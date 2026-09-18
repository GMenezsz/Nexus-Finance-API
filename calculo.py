from datetime import date
from decimal import Decimal

def calcular_transacoes(transacoes, mes_filtro=None, ano_filtro=None):
    saldo = Decimal("0.00")
    total_receitas = Decimal("0.00")
    total_despesas = Decimal("0.00")
    resumo_categoria = {}

    tipos_receita = ["receita", "entrada", "ganhos"]
    tipos_despesa = ["despesa", "saida", "saída", "gasto"]

    hoje = date.today()
    mes_alvo = f"{mes_filtro:02d}" if mes_filtro is not None else f"{hoje.month:02d}"
    ano_alvo = str(ano_filtro) if ano_filtro is not None else str(hoje.year)
    periodo_alvo = f"{ano_alvo}-{mes_alvo}"

    for t in transacoes:
        tipo = t[2]
        categoria = t[3].strip().capitalize()
        valor = Decimal(str(t[4]))
        data_transacao = t[5]
        status = t[6] if len(t) > 6 else "pago"

        if data_transacao.startswith(periodo_alvo):
            if status.lower() == "pago":
                resumo_categoria.setdefault(categoria, Decimal("0.00"))

                if tipo.lower() in tipos_receita:
                    saldo += valor
                    total_receitas += valor
                    resumo_categoria[categoria] += valor

                elif tipo.lower() in tipos_despesa:
                    saldo -= valor
                    total_despesas += valor
                    resumo_categoria[categoria] -= valor

    return {
        "mes_referencia": periodo_alvo,
        "saldo": saldo,
        "receitas": total_receitas,
        "despesas": total_despesas,
        "resumo_categoria": resumo_categoria,
    }
