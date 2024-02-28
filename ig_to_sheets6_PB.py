import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración inicial
ACCESS_TOKEN = 'EAAFKUx7Tl00BO5ZC80YRQZA52KCP7zExYesavBRCm24MhlKhqLZCymZBrLfq8cCzdnQAhH2wFz0WerGPswF3JjH2WisZCFdYgg5ZCzeFPzC7SVPndhoft1ZAWzgDxB0gT8IrgydPqELw9kfDiXnrrxZA0oiZBmJUNeZCtofMIKiYBXoGkjDopzFdGz1FgXH5xAaOFHgjidZAZB082fN6BxyK7G2SZAtUdEGhDZAB0ZD'
INSTAGRAM_BUSINESS_ACCOUNT_ID = '17841449053633062'

def get_instagram_metrics():
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media?fields=id,media_type,media_url,permalink,like_count,comments_count,timestamp&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data']
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de Instagram: {e}")
        return None

# Suponiendo un número de seguidores o alcance para calcular el engagement
numero_de_seguidores = 1000  # Ejemplo

# Obtener los datos de las publicaciones
posts_data = get_instagram_metrics()

if posts_data:
    # Convertir los datos a DataFrame para un mejor manejo
    df_posts = pd.json_normalize(posts_data)
    df_posts.fillna(value=0, inplace=True)

    # Calcular el engagement para cada publicación
    df_posts['engagement'] = ((df_posts['like_count'] + df_posts['comments_count']) / numero_de_seguidores) * 100

    # Configuración de Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
    client = gspread.authorize(creds)

    # Seleccionar la hoja específica en Google Sheets
    sheet_name = "HOJA_PB"
    sheet = client.open(sheet_name).get_worksheet(5)  # Asume que '5' es el índice correcto para la hoja

    # Preparar y enviar los datos a Google Sheets
    # Nota el cambio de lugar del 'timestamp' al final de la lista en la siguiente línea
    datos_para_google_sheets = df_posts[['id', 'media_type', 'media_url', 'permalink', 'like_count', 'comments_count', 'engagement', 'timestamp']].values.tolist()
    datos_para_google_sheets.insert(0, ['ID', 'Tipo de Media', 'URL de Media', 'Enlace Permanente', 'Likes', 'Comentarios', 'Engagement (%)', 'Timestamp'])
    sheet.update('A1', datos_para_google_sheets, value_input_option='USER_ENTERED')
    print("Datos de engagement de Instagram con timestamp al final enviados a Google Sheets con éxito.")
else:
    print("No se pudieron obtener los datos de Instagram.")
