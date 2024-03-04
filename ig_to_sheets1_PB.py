import os
import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# Obtener ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID del entorno
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

def get_instagram_post_insights():
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media?fields=id,media_id,caption,media_type,media_url,permalink,timestamp,username, like_count,plays,insights.metric(impressions,reach,saved,video_views,likes,follows,comments, shares, plays, profile_activity, profile_visits)&access_token={ACCESS_TOKEN}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a la API: {e}")
        return None

# Obtener datos de Instagram
datos_instagram = get_instagram_post_insights()

# Procesar con pandas
if datos_instagram:
    df = pd.json_normalize(datos_instagram['data'])

    # Expandir los insights.data a columnas separadas
    def expand_insights(row):
        insights_data = row.get('insights.data', [])
        insights_dict = {item['name']: item['values'][0]['value'] for item in insights_data}
        return pd.Series(insights_dict)
    
    # Aplicar la función para expandir los insights y unirlos al DataFrame principal
    insights_expanded = df.apply(expand_insights, axis=1)
    df = pd.concat([df.drop(columns=['insights.data']), insights_expanded], axis=1)
    
    df.fillna(value="", inplace=True)

    # Configuración de Google Sheets
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
    client = gspread.authorize(creds)

    # Nombre de tu hoja de cálculo y seleccionar la primera hoja
    sheet = client.open("HOJA_PB").get_worksheet(0)

    # Preparar datos para enviar a Google Sheets
    datos_para_google_sheets = df.values.tolist()
    datos_para_google_sheets.insert(0, df.columns.to_list())

    datos_para_google_sheets = [[str(item) for item in row] for row in datos_para_google_sheets]
    sheet.update('A1', datos_para_google_sheets)
    print("Datos enviados a Google Sheets con éxito.")
else:
    print("No se pudieron obtener los datos de Instagram.")
