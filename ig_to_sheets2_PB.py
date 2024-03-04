import os
import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Obtener ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID del entorno
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

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

# Obtener la fecha actual
fecha_actual = datetime.today().strftime('%Y-%m-%d')

# Procesar con pandas y preparar para Google Sheets
if datos_perfil_instagram:
    df_datos_perfil = pd.json_normalize(datos_perfil_instagram)
    df_datos_perfil['reach'] = reach_instagram
    df_datos_perfil['profile_views'] = profile_views_instagram
    df_datos_perfil['impressions'] = impressions_instagram  # Añadir "impressions" al DataFrame

    # Añadir la fecha actual a los datos del perfil
    df_datos_perfil['fecha_activacion'] = fecha_actual

    # Configuración de Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
    client = gspread.authorize(creds)

    # Seleccionar la hoja específica para los datos del perfil
    sheet_name = "HOJA_PB"
    sheet = client.open(sheet_name).get_worksheet(1)  # Asume que '1' es el índice para la segunda hoja

    # Verificar si la fecha actual ya está en la hoja de Google Sheets
    fechas_registradas = sheet.col_values(1)
    if fecha_actual in fechas_registradas:
        # Si la fecha ya está registrada, actualizar los datos en esa fila
        fila_actualizacion = fechas_registradas.index(fecha_actual) + 1
        datos_perfil_para_google_sheets = df_datos_perfil.values.tolist()[0]
        sheet.update(f'A{fila_actualizacion}', datos_perfil_para_google_sheets)
        print(f"Datos del perfil actualizados para la fecha {fecha_actual}.")
    else:
        # Si la fecha no está registrada, agregar una nueva fila con los datos
        datos_perfil_para_google_sheets = df_datos_perfil.values.tolist()
        # Convertir todos los valores a cadenas
        datos_perfil_para_google_sheets = [[str(item) for item in row] for row in datos_perfil_para_google_sheets]
        sheet.append_rows(datos_perfil_para_google_sheets)
        print(f"Datos del perfil agregados para la fecha {fecha_actual}.")
else:
    print("No se pudieron obtener los datos del perfil de Instagram.")
