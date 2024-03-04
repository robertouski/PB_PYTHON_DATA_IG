import os
import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID del entorno
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

# Función para obtener las impresiones en un rango de fechas específico
def get_impressions(since_date, until_date):
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/insights?metric=impressions&period=day&since={since_date}&until={until_date}&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data']
        impressions = sum(entry['values'][0]['value'] for entry in data)
        return impressions
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener las impresiones: {e}")
        return None

# Configuración de Google Sheets
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
client = gspread.authorize(creds)

# Nombre del documento y selección de la hoja específica
sheet_name = "HOJA_PB"
sheet_index = 3  # Índice de la hoja 4 (se cuenta desde 0)
sheet = client.open(sheet_name).get_worksheet(sheet_index)

# Obtener la fecha de hoy y la fecha de hace tres meses
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

# Dividir el período en intervalos de máximo 30 días
intervals = []
while start_date < end_date:
    interval_end_date = min(start_date + timedelta(days=30), end_date)
    intervals.append((start_date.strftime('%Y-%m-%d'), interval_end_date.strftime('%Y-%m-%d')))
    start_date = interval_end_date

# Obtener las impresiones para cada intervalo
impressions_total = 0
for interval in intervals:
    since_date, until_date = interval
    impressions = get_impressions(since_date, until_date)
    if impressions is not None:
        impressions_total += impressions
    else:
        print(f"No se pudieron obtener las impresiones desde {since_date} hasta {until_date}.")

# Actualizar la hoja de Google Sheets con las impresiones totales
sheet.update('A1', [['Impresiones totales'], [impressions_total]])
print("Impresiones totales enviadas a Google Sheets con éxito.")
