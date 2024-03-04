import os
import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID del entorno
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

# Calcular fechas para el rango de 28 días antes del día actual
end_date = datetime.now()
start_date = end_date - timedelta(days=28)

# Formatear fechas para la API
start_date_formatted = start_date.strftime('%Y-%m-%d')
end_date_formatted = end_date.strftime('%Y-%m-%d')

# Función para obtener nuevos seguidores
def get_new_followers(start_date, end_date):
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/insights?metric=follower_count&period=day&since={start_date}&until={end_date}&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()['data'][0]['values']
        return data
    else:
        print(f"Error al obtener datos de seguidores de Instagram: {response.status_code}")
        return None

# Obtener los datos de seguidores
followers_data = get_new_followers(start_date_formatted, end_date_formatted)

if followers_data:
    # Convertir los datos a DataFrame
    df_followers = pd.DataFrame(followers_data)
    df_followers['end_time'] = pd.to_datetime(df_followers['end_time']).dt.date
    df_followers.rename(columns={'value': 'Seguidores Nuevos', 'end_time': 'Fecha'}, inplace=True)
    df_followers = df_followers[['Fecha', 'Seguidores Nuevos']]
    
    # Configuración de Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
    client = gspread.authorize(creds)

    # Seleccionar la hoja específica en Google Sheets
    sheet_name = "HOJA_PB"
    sheet = client.open(sheet_name).get_worksheet(6)  # Asume que '6' es el índice correcto para la hoja

    # Preparar los datos para Google Sheets
    datos_para_google_sheets = [df_followers.columns.values.tolist()] + df_followers.values.tolist()

    # Enviar los datos a Google Sheets
    sheet.update('A1', datos_para_google_sheets, value_input_option='USER_ENTERED')
    print("Datos de nuevos seguidores de Instagram enviados a Google Sheets con éxito.")
else:
    print("No se pudieron obtener los datos de seguidores de Instagram.")
