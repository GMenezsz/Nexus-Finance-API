import sqlite3

transacoes = """
    CREATE TABLE IF NOT EXISTS transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL, 
    categoria TEXT NOT NULL,
    valor TEXT NOT NULL,
    data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pago',
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
)"""

usuario = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        sobrenome TEXT NOT NULL,
        usuario TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        foto TEXT DEFAULT NULL
    )
"""

metas = """
    CREATE TABLE IF NOT EXISTS metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    salario_liquido REAL NOT NULL DEFAULT 0,
    meta REAL NOT NULL,
    parcelas_concluidas TEXT NOT NULL DEFAULT '',
    anos INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
)"""

categorias_personalizadas = """
    CREATE TABLE IF NOT EXISTS categorias_personalizadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    nome TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
    UNIQUE (usuario_id, tipo, nome)
)"""

def criar_banco():
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(usuario)
    cursor.execute(metas)
    cursor.execute(transacoes)
    cursor.execute(categorias_personalizadas)
    conn.commit()


    try:
        cursor.execute("ALTER TABLE metas ADD COLUMN parcelas_concluidas TEXT NOT NULL DEFAULT ''")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE metas ADD COLUMN anos INTEGER NOT NULL DEFAULT 1")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()

def verificar_usuario(usuario):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, senha, foto, sobrenome FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def buscar_id_por_usuario(usuario: str):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def atualizar_foto_usuario(usuario_id, foto_base64):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET foto = ? WHERE id = ?", 
        (foto_base64, usuario_id)
    )
    conn.commit()
    conn.close()

def buscar_senha_por_usuario(usuario: str):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, senha FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def inserir_usuario(nome, sobrenome, usuario, senha):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nome, sobrenome, usuario, senha) VALUES (?, ?, ?, ?)", (nome, sobrenome, usuario, senha))
    conn.commit()
    usuario_id = cursor.lastrowid
    conn.close()
    return usuario_id

def inserir_transacao(usuario_id, tipo, categoria, valor, data, status):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transacoes (usuario_id, tipo, categoria, valor, data, status) VALUES (?, ?, ?, ?, ?, ?)", 
        (usuario_id, tipo, categoria, str(valor), data, status) 
    )
    conn.commit()
    conn.close()

def atualizar_transacao(id, tipo, categoria, valor, data, status):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transacoes SET tipo = ?, categoria = ?, valor = ?, data = ?, status = ? WHERE id = ?", 
        (tipo, categoria, valor, data, status, id)
    )
    conn.commit()
    conn.close()

def deletar_transacao(id):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def efetivar_transacoes_pendentes(usuario_id):
    """
    Toda transação (receita ou despesa) que estava com status 'pendente'
    e cuja data já chegou (data <= hoje) passa automaticamente a 'pago',
    entrando no saldo/receitas/despesas normalmente a partir de agora.
    """
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transacoes SET status = 'pago' "
        "WHERE usuario_id = ? AND status = 'pendente' AND data <= date('now')",
        (usuario_id,)
    )
    conn.commit()
    conn.close()

def listar_transacoes(usuario_id):
    efetivar_transacoes_pendentes(usuario_id)

    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transacoes WHERE usuario_id = ?", (usuario_id,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def atualizar_usuario(id, nome, sobrenome):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET nome = ?, sobrenome = ? WHERE id = ?", 
        (nome, sobrenome, id)
    )
    conn.commit()
    conn.close()

def atualizar_senha(id, nova_senha):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET senha = ? WHERE id = ?", 
        (nova_senha, id)
    )
    conn.commit()
    conn.close()

def excluir_conta(usuario_id):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()

def deletar_meta(usuario_id, titulo):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metas WHERE usuario_id = ? AND titulo = ?", (usuario_id, titulo))
    conn.commit()
    conn.close()


def listar_metas(usuario_id):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM metas WHERE usuario_id = ?", (usuario_id,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def inserir_meta(usuario_id, titulo, meta, anos):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO metas (usuario_id, titulo, salario_liquido, meta, anos) VALUES (?, ?, 0, ?, ?)",
        (usuario_id, titulo, meta, anos)
    )
    conn.commit()
    conn.close()

def atualizar_meta(usuario_id, titulo_antigo, titulo_novo, meta, anos):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE metas SET titulo = ?, meta = ?, anos = ?, parcelas_concluidas = '' WHERE usuario_id = ? AND titulo = ?",
        (titulo_novo, meta, anos, usuario_id, titulo_antigo)
    )
    conn.commit()
    conn.close()

def alternar_parcela_meta(usuario_id, titulo, indice):
    """Marca a parcela se ela ainda não estava concluída, ou desmarca se já estava."""
    parcelas_atuais = buscar_parcelas_meta(usuario_id, titulo)
    indices = sorted(set(int(p) for p in parcelas_atuais.split(",") if p != ""))

    if indice in indices:
        indices.remove(indice)
        marcada = False
    else:
        indices.append(indice)
        indices = sorted(set(indices))
        marcada = True

    nova_string = ",".join(str(i) for i in indices)
    atualizar_parcelas_meta(usuario_id, titulo, nova_string)
    return indices, marcada

def buscar_anos_meta(usuario_id, titulo):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT anos FROM metas WHERE usuario_id = ? AND titulo = ?",
        (usuario_id, titulo)
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def buscar_parcelas_meta(usuario_id, titulo):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT parcelas_concluidas FROM metas WHERE usuario_id = ? AND titulo = ?",
        (usuario_id, titulo)
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else ""

def atualizar_parcelas_meta(usuario_id, titulo, parcelas_concluidas):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE metas SET parcelas_concluidas = ? WHERE usuario_id = ? AND titulo = ?",
        (parcelas_concluidas, usuario_id, titulo)
    )
    conn.commit()
    conn.close()

def inserir_categoria_personalizada(usuario_id, tipo, nome):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categorias_personalizadas (usuario_id, tipo, nome) VALUES (?, ?, ?)",
            (usuario_id, tipo, nome)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  
    conn.close()

def listar_categorias_personalizadas(usuario_id, tipo=None):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    if tipo:
        cursor.execute(
            "SELECT nome FROM categorias_personalizadas WHERE usuario_id = ? AND tipo = ? ORDER BY id",
            (usuario_id, tipo)
        )
    else:
        cursor.execute(
            "SELECT tipo, nome FROM categorias_personalizadas WHERE usuario_id = ? ORDER BY id",
            (usuario_id,)
        )
    dados = cursor.fetchall()
    conn.close()
    return dados

def reiniciar_dados_usuario(usuario_id):
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE usuario_id = ?", (usuario_id,))
    cursor.execute("DELETE FROM metas WHERE usuario_id = ?", (usuario_id,))
    conn.commit()
    conn.close()
