from supabase import create_client, Client

def create_client_jwt(supabase_url: str, jwt: str) -> Client:
    return create_client(supabase_url, jwt)