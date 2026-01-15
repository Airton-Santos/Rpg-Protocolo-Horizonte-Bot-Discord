import os
from supabase import create_client, Client
import json  # <--- ADICIONE ESTA LINHA AQUI!

# --- CONFIGURAÇÃO DO SUPABASE ---
# Essas variáveis você deve colocar no painel do Railway (Variables)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializa o cliente apenas se as chaves existirem
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNÇÕES ADAPTADAS ---

def carregar_fichas():
    """Busca todas as fichas no Supabase e transforma em dicionário."""
    if not supabase:
        print("⚠️ Supabase não configurado. Verifique as variáveis.")
        return {}

    try:
        # Puxa todas as linhas da tabela 'fichas'
        resposta = supabase.table("fichas").select("*").execute()
        
        # Converte a lista do Supabase de volta para o formato de dicionário {uid: dados}
        fichas_dict = {}
        for row in resposta.data:
            fichas_dict[row['id']] = row['dados']
        return fichas_dict
    except Exception as e:
        print(f"❌ Erro ao carregar do Supabase: {e}")
        return {}

def salvar_fichas(dados_completos):
    """Salva ou Atualiza as fichas no Supabase (Upsert)."""
    if not supabase: return

    try:
        # Preparamos os dados para o formato do Supabase
        lista_para_upsert = []
        for uid, dados in dados_completos.items():
            lista_para_upsert.append({"id": str(uid), "dados": dados})

        # O 'upsert' insere se não existir ou atualiza se já existir o ID
        supabase.table("fichas").upsert(lista_para_upsert).execute()
    except Exception as e:
        print(f"❌ Erro ao salvar no Supabase: {e}")

def deletar_fichas(usuario_id):
    """Remove a ficha do banco de dados remoto."""
    if not supabase: return False
    try:
        supabase.table("fichas").delete().eq("id", str(usuario_id)).execute()
        return True
    except Exception as e:
        print(f"❌ Erro ao deletar no Supabase: {e}")
        return False

# --- ITENS E OUTROS (Podemos manter local ou subir pro Supabase depois) ---
def carregar_itens():
    if not supabase: return {}
    try:
        res = supabase.table("itens_globais").select("*").execute()
        if res.data:
            return res.data[0]['dados'] # Supondo que salvamos tudo em uma linha
        return {}
    except:
        return {}

def salvar_itens(dados):
    if not supabase: return
    try:
        supabase.table("itens_globais").upsert({"id": 1, "dados": dados}).execute()
    except:
        pass

def carregar_caracteristicas(tipo):
    # tipo será 'vantagens' ou 'desvantagens'
    # Esse arquivo fica na pasta 'data' dentro do seu projeto no Railway
    try:
        with open(f"data/{tipo}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler catálogo de {tipo}: {e}")
        return {}