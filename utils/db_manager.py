import json
import os

# Caminhos dos arquivos
FICHA_PATH = "database/fichas.json"
VANT_PATH = "data/vantagens.json"
DESV_PATH = "data/desvantagens.json"
ITENS_PATH = "database/items.json"


def carregar_fichas():
    if not os.path.exists(FICHA_PATH) or os.stat(FICHA_PATH).st_size == 0:
        return {}
    with open(FICHA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_fichas(dados):
    # Garante que 'dados' seja um dicionário, mesmo que vazio
    if dados is None:
        dados = {}
    
    with open(FICHA_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def deletar_fichas(usuario_id):
    """Remove a ficha de um usuário e garante a integridade do JSON."""
    fichas = carregar_fichas()
    uid = str(usuario_id)
    
    if uid in fichas:
        del fichas[uid]
        
        # Se após deletar não sobrar nada, garantimos que salvamos um dicionário vazio
        if not fichas:
            fichas = {}
            
        salvar_fichas(fichas)
        return True
    return False

def carregar_caracteristicas(tipo):
    """Carrega vantagens ou desvantagens."""
    path = VANT_PATH if tipo == "vantagens" else DESV_PATH
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def carregar_itens():
    if not os.path.exists(ITENS_PATH) or os.stat(ITENS_PATH).st_size == 0:
        return {}
    with open(ITENS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
def salvar_itens(dados):
    with open(ITENS_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
