import os
from dotenv import load_dotenv
from twelvedata import TDClient
import requests

load_dotenv()

if not os.getenv("TWELVEDATA_API_KEY"):
    raise ValueError("ERROR: TWELVEDATA_API_KEY not found. Did you create a .env file?")

td = TDClient(apikey=os.getenv("TWELVEDATA_API_KEY"))

url = ""
response = requests.get(url)
response.raise_for_status() # Raises an error for bad HTTP statuses (401, 429, etc.)
    

data = response.json()