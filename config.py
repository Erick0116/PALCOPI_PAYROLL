import os
from flask import Flask
try:
    # If vendored supabase-py is inside utils/supabase_py
    from utils.supabase_py.supabase import create_client, Client
except ImportError:
    # Fallback if supabase-py is installed normally
    from supabase import create_client, Client

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey123")

# Load Supabase credentials from environment
SUPABASE_URL = os.environ.get("https://brwxzhaufjzjrvuplixi.supabase.co")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyd3h6aGF1Zmp6anJ2dXBsaXhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4MDQ1OTcsImV4cCI6MjA5MzM4MDU5N30.DS9fHaD9a_Bf_Qpp6WeEwFwgDPEaNUWGD3-_m6RnBmU")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase environment variables!")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
