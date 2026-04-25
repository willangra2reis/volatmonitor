import os
from flask import g
from werkzeug.local import LocalProxy
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Supabase
url = os.environ.get("SUPABASE_URL", "")
key = os.environ.get("SUPABASE_KEY", "")

def get_supabase() -> Client:
    if "supabase" not in g:
        g.supabase = create_client(url, key)
    return g.supabase

supabase: Client = LocalProxy(get_supabase)
