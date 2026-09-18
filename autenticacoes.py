def autenticar_nome(nome):
    if len(nome) >= 3:
        return True
    else:
        return False

def autenticar_sobrenome(sobrenome):
    if len(sobrenome) >= 3:
        return True
    else:
        return False

def autenticar_usuario(usuario):
    if len(usuario) >= 3:
        return True
    else:
        return False

def autenticar_senha(senha):
    if len(senha) >= 6:
        return True
    else:
        return False

def autenticar_transacao(valor):
    if valor < 0:
        return False
    else:
        return True

CATEGORIAS_RECEITA = ["Salário", "Pix", "Bonificação", "Freelance", "Investimentos", "Outros"]
CATEGORIAS_DESPESA = ["Alimentação", "Transporte", "Moradia", "Lazer", "Contas", "Saúde", "Outros"]

TIPOS_RECEITA = ["receita", "entrada", "ganhos"]
TIPOS_DESPESA = ["despesa", "saida", "saída", "gasto"]

def autenticar_categoria(tipo, categoria):
    tipo = tipo.lower()
    categoria_limpa = categoria.strip()

    if tipo in TIPOS_RECEITA or tipo in TIPOS_DESPESA:
        return len(categoria_limpa) > 0
    else:
        return False

def salario_liquido(salario_liquido):
    if salario_liquido <= 0:
        return False
    else:
        return True

def meta_valida(meta):
    if meta <= 0:
        return False
    else:
        return True
