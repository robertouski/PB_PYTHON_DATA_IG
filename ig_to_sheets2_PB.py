import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de Instagram API
ACCESS_TOKEN = 'EAAFKUx7Tl00BO9PyCnZCUm1n249OaTLOG9BTaDY5DHwHcFpNofLlZCRsKX9LYVJDOehqZB0v6vQwAWJZBgRLlRXJcxgMoZBLA7Iim77fpmo0btZB2R3WgQSZBbjAzQ3dNX2okM054BkcxZAsCH3dniVqXFGKqtgJMDZAQsI1E7zF8Uv7wZCE0xmZAuhkbxUtueQLyOg1hSCFVrUd9Wj7VmjzLZAZBK1KaVZBpaABQZD'
INSTAGRAM_BUSINESS_ACCOUNT_ID = '17841449053633062'

def get_instagram_profile_data():
    url_profile = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}?fields=username,name,followers_count,media_count,profile_picture_url,website&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url_profile)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud de datos del perfil: {e}")
        return None

def get_instagram_insights(metric):
    url_insights = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/insights?metric={metric}&period=day&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url_insights)
        response.raise_for_status()
        insights_data = response.json()
        value = insights_data['data'][0]['values'][0]['value'] if insights_data['data'] else 'No Data'
        return value
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud de insights para {metric}: {e}")
        return 'Error'
    except KeyError:
        print(f"No se encontró la métrica de {metric} en los datos.")
        return 'Error'

# Obtener datos del perfil de Instagram
datos_perfil_instagram = get_instagram_profile_data()

# Obtener "reach", "profile_views", e "impressions" de la cuenta de Instagram
reach_instagram = get_instagram_insights('reach')
profile_views_instagram = get_instagram_insights('profile_views')
impressions_instagram = get_instagram_insights('impressions')

# Procesar con pandas y preparar para Google Sheets
if datos_perfil_instagram:
    df_datos_perfil = pd.json_normalize(datos_perfil_instagram)
    df_datos_perfil['reach'] = reach_instagram
    df_datos_perfil['profile_views'] = profile_views_instagram
    df_datos_perfil['impressions'] = impressions_instagram  # Añadir "impressions" al DataFrame

    # Configuración de Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
    client = gspread.authorize(creds)

    # Seleccionar la hoja específica para los datos del perfil
    sheet_name = "HOJA_PB"
    sheet = client.open(sheet_name).get_worksheet(1)  # Asume que '1' es el índice para la segunda hoja

    # Preparar y enviar datos del perfil a Google Sheets
    datos_perfil_para_google_sheets = df_datos_perfil.values.tolist()
    datos_perfil_para_google_sheets.insert(0, df_datos_perfil.columns.to_list())
    datos_perfil_para_google_sheets = [[str(item) for item in row] for row in datos_perfil_para_google_sheets]
    sheet.update('A1', datos_perfil_para_google_sheets)
    print("Datos del perfil, incluyendo 'reach', 'profile_views' e 'impressions', enviados a Google Sheets con éxito.")
else:
    print("No se pudieron obtener los datos del perfil de Instagram.")
