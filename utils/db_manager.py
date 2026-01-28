import os
from supabase import create_client, Client
import json

# --- CONFIGURAÇÃO DO SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializa o cliente com verificação
if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ ALERTA: Variáveis de ambiente do Supabase não encontradas!")
    supabase: Client = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNÇÕES DE FICHAS ---

def carregar_fichas():
    """Busca todas as fichas no Supabase."""
    if not supabase: return {}
    try:
        # Puxa todas as linhas da tabela 'fichas'
        resposta = supabase.table("fichas").select("*").execute()
        
        fichas_dict = {}
        for row in resposta.data:
            # O Supabase já decodifica o JSON da coluna 'dados' automaticamente
            fichas_dict[str(row['id'])] = row['dados']
        return fichas_dict
    except Exception as e:
        print(f"❌ Erro ao carregar fichas: {e}")
        return {}

def salvar_fichas(dados_para_salvar):
    """
    Recebe um dicionário {uid: dados} e salva no banco.
    Pode enviar apenas uma ficha ou várias de uma vez.
    """
    if not supabase: return

    try:
        lista_para_upsert = []
        for uid, dados in dados_para_salvar.items():
            lista_para_upsert.append({"id": str(uid), "dados": dados})

        # Upsert garante que se o ID existir, ele atualiza; se não, cria.
        supabase.table("fichas").upsert(lista_para_upsert).execute()
    except Exception as e:
        print(f"❌ Erro ao salvar no Supabase: {e}")

def deletar_fichas(usuario_id):
    """Remove a ficha do banco de dados remoto."""
    if not supabase: return False
    try:
        resposta = supabase.table("fichas").delete().eq("id", str(usuario_id)).execute()
        return True if resposta.data else False
    except Exception as e:
        print(f"❌ Erro ao deletar no Supabase: {e}")
        return False

# --- FUNÇÕES DE ITENS (CATÁLOGO GLOBAL) ---

def carregar_itens():
    """Carrega o catálogo de itens globais."""
    if not supabase: return {}
    try:
        # Buscamos a linha única (id: 1) que guarda o dicionário de itens
        res = supabase.table("itens_globais").select("dados").eq("id", 1).execute()
        if res.data:
            return res.data[0]['dados']
        return {}
    except Exception as e:
        print(f"❌ Erro ao carregar itens globais: {e}")
        return {}

def salvar_itens(dados_itens):
    """Salva o catálogo de itens globais na linha única."""
    if not supabase: return
    try:
        # Mantemos sempre o ID 1 para ser o registro único do catálogo
        supabase.table("itens_globais").upsert({"id": 1, "dados": dados_itens}).execute()
    except Exception as e:
        print(f"❌ Erro ao salvar itens globais: {e}")

# --- CARACTERÍSTICAS (JSON LOCAL) ---

def carregar_caracteristicas(tipo):
    """Lê vantagens/desvantagens dos arquivos JSON locais."""
    caminho = f"data/{tipo}.json"
    if not os.path.exists(caminho):
        print(f"⚠️ Arquivo {caminho} não encontrado!")
        return {}
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler {tipo}: {e}")
        return {}