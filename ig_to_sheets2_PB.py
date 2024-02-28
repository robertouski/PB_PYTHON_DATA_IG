import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de Instagram API
ACCESS_TOKEN = 'EAAFKUx7Tl00BOynzu0FWwpUfdIcqAqcawxpQdCnA5t1HXFAwUZCtPrJEdjnDdjryT45or0WqpOjgYeUPCaJZApQyF8ITkAnJ0nt39QQgCSmvg1e3UHMqUgVfc5Q68DFdllfuYZApct8Ws9GpNUILiG5HA8f4yryZCGY6SZAcqruli48YVGyyGaLw9yag6KZAyitd6owKzti2HZBpyNJeAMOhtqMqnkhTfUZD'
INSTAGRAM_BUSINESS_ACCOUNT_ID = '17841449053633062'

def get_extra_instagram_data():
    # Ajusta esta solicitud para incluir datos sobre likes y comentarios
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media?fields=id,like_count,comments_count&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a la API: {e}")
        return None

# Obtener datos adicionales de Instagram
extra_datos_instagram = get_extra_instagram_data()

# Procesar con pandas
if extra_datos_instagram:
    df_extra = pd.json_normalize(extra_datos_instagram['data'])

    # Configuración de Google Sheets
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
    client = gspread.authorize(creds)

    # Seleccionar la hoja específica para los datos adicionales
    sheet_name = "HOJA"
    sheet = client.open(sheet_name).get_worksheet(1)  # Asume que '1' es el índice para sheet2

    # Preparar y enviar datos adicionales a Google Sheets
    datos_extra_para_google_sheets = df_extra.values.tolist()
    datos_extra_para_google_sheets.insert(0, df_extra.columns.to_list())
    datos_extra_para_google_sheets = [[str(item) for item in row] for row in datos_extra_para_google_sheets]
    sheet.update('A1', datos_extra_para_google_sheets)
    print("Datos adicionales enviados a Google Sheets con éxito.")
else:
    print("No se pudieron obtener los datos adicionales de Instagram.")
