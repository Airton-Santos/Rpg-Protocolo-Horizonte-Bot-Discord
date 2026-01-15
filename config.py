import os
from dotenv import load_dotenv

# 1. O Carregador de Segredos
load_dotenv()

# 2. A Identidade do Bot (Token)
TOKEN = os.getenv("TOKEN")

# 3. O Gatilho dos Comandos (Prefixo)
PREFIXO = "!"