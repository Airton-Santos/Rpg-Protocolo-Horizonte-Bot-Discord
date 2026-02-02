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

def verificar_apocalipse():
    """Lê do banco se o mundo está em apocalipse ou não."""
    try:
        # Puxa o valor da linha id=1
        res = supabase.table("configuracoes").select("apocalipse_ativo").eq("id", 1).execute()
        if res.data:
            return res.data[0]['apocalipse_ativo']
        return False
    except Exception as e:
        print(f"Erro ao ler banco: {e}")
        return False

def alternar_apocalipse(novo_status: bool):
    """Grava no banco o novo estado do mundo."""
    try:
        supabase.table("configuracoes").update({"apocalipse_ativo": novo_status}).eq("id", 1).execute()
        return True
    except Exception as e:
        print(f"Erro ao gravar no banco: {e}")
        return False
    
def salvar_estado_player(usuario_id, novo_estado):
    """Atualiza apenas o campo 'estado' dentro do JSON de dados da ficha."""
    if not supabase: return False
    try:
        # 1. Busca a ficha atual para não sobrescrever outros dados (como inventário/atributos)
        res = supabase.table("fichas").select("dados").eq("id", str(usuario_id)).execute()
        
        if res.data:
            dados_atuais = res.data[0]['dados']
            # 2. Adiciona ou atualiza o campo estado
            dados_atuais['estado'] = novo_estado
            
            # 3. Salva a ficha atualizada
            supabase.table("fichas").update({"dados": dados_atuais}).eq("id", str(usuario_id)).execute()
            return True
        else:
            print(f"⚠️ Ficha do usuário {usuario_id} não encontrada para atualizar estado.")
            return False
    except Exception as e:
        print(f"❌ Erro ao salvar estado no Supabase: {e}")
        return False

def buscar_estado_player(usuario_id):
    """Busca o estado de saúde atual do player na ficha."""
    if not supabase: return "Desconhecido"
    try:
        res = supabase.table("fichas").select("dados").eq("id", str(usuario_id)).execute()
        if res.data:
            dados = res.data[0]['dados']
            # Retorna o estado ou 'OK' se o campo ainda não existir
            return dados.get('estado', 'OK')
        return "Sem Ficha"
    except Exception as e:
        print(f"❌ Erro ao buscar estado: {e}")
        return "Erro"

# --- NOVAS FUNÇÕES DE ECONOMIA E INFECÇÃO ---

def atualizar_fichas_supabase(usuario_id, novos_dados_internos):
    """
    Atualiza campos específicos dentro da coluna JSON 'dados'.
    Exemplo de novos_dados_internos: {"moedas": 50, "infecção": "10%"}
    """
    if not supabase: return False
    try:
        uid = str(usuario_id)
        # 1. Busca a ficha atual para pegar o que já existe (atributos, nome, etc)
        res = supabase.table("fichas").select("dados").eq("id", uid).execute()
        
        if res.data:
            dados_completos = res.data[0]['dados']
            
            # 2. Atualiza apenas os campos que enviamos (moedas, por exemplo)
            for chave, valor in novos_dados_internos.items():
                dados_completos[chave] = valor
            
            # 3. Salva o JSON inteiro atualizado de volta na coluna 'dados'
            supabase.table("fichas").update({"dados": dados_completos}).eq("id", uid).execute()
            return True
        return False
    except Exception as e:
        print(f"❌ Erro ao atualizar campos internos: {e}")
        return False

def adicionar_remover_moedas(usuario_id, quantidade, operacao="add"):
    """Função específica para somar ou subtrair moedas sem erro."""
    if not supabase: return False
    try:
        uid = str(usuario_id)
        res = supabase.table("fichas").select("dados").eq("id", uid).execute()
        
        if res.data:
            dados = res.data[0]['dados']
            saldo_atual = dados.get('moedas', 0)
            
            if operacao == "add":
                novo_saldo = saldo_atual + quantidade
            else:
                novo_saldo = max(0, saldo_atual - quantidade) # Impede saldo negativo
            
            dados['moedas'] = novo_saldo
            supabase.table("fichas").update({"dados": dados}).eq("id", uid).execute()
            return novo_saldo
        return None
    except Exception as e:
        print(f"❌ Erro na operação de moedas: {e}")
        return None