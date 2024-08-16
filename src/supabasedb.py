from supabase import create_client, Client
from .utils import supabase_url, supabase_key

supabase: Client = create_client(supabase_url, supabase_key)

