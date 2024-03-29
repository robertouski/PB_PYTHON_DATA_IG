import os
import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

from datetime import datetime, timedelta

# Calcular la fecha de inicio (hace 30 días)
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

# Formatear las fechas en el formato YYYY-MM-DD
since_date = start_date.strftime('%Y-%m-%d')
until_date = end_date.strftime('%Y-%m-%d')

# Configuración de Instagram API


# Obtener ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID del entorno
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
def get_audience_demographics():
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/insights?metric=follower_count&period=day&since={since_date}&until={until_date}&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        demographics_data = response.json()['data']
        return demographics_data
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a la API: {e}")
        return None

# Obtener datos demográficos de la audiencia
demographics_data = get_audience_demographics()

# Procesamiento y preparación de datos para Google Sheets, si se obtienen datos demográficos
if demographics_data:
    # Ejemplo de cómo podrías procesar los datos demográficos para un formato tabular simple
    demographics_list = []
    for item in demographics_data:
        for value in item['values']:
            demographics_list.append({
                'follower_count': value['value'],  # Cambio de 'value' a 'follower_count'
                'end_time': value['end_time']
            })
    
    df_demographics = pd.DataFrame(demographics_list)

    # Configuración de Google Sheets
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
    client = gspread.authorize(creds)

    # Nombre de tu hoja de cálculo y seleccionar la hoja específica
    sheet_name = "HOJA_PB"
    sheet = client.open(sheet_name).get_worksheet(2)  # Asume que '2' es el índice para sheet3

    # Preparar datos para enviar a Google Sheets
    datos_para_google_sheets = df_demographics.values.tolist()
    datos_para_google_sheets.insert(0, df_demographics.columns.to_list())

    sheet.update('A1', datos_para_google_sheets)
    print("Datos de follower_count enviados a Google Sheets con éxito.")
else:
    print("No se pudieron obtener los datos de follower_count de la audiencia.")
