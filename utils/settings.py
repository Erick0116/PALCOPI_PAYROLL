from config import supabase

def load_settings():
    response = supabase.table("settings").select("*").execute()
    settings = {}
    for s in response.data:
        try:
            settings[s["setting_name"]] = float(s["value"])
        except Exception:
            settings[s["setting_name"]] = s["value"]
    return settings
