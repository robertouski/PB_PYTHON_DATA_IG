import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración inicial
ACCESS_TOKEN = 'EAAFKUx7Tl00BO5ZC80YRQZA52KCP7zExYesavBRCm24MhlKhqLZCymZBrLfq8cCzdnQAhH2wFz0WerGPswF3JjH2WisZCFdYgg5ZCzeFPzC7SVPndhoft1ZAWzgDxB0gT8IrgydPqELw9kfDiXnrrxZA0oiZBmJUNeZCtofMIKiYBXoGkjDopzFdGz1FgXH5xAaOFHgjidZAZB082fN6BxyK7G2SZAtUdEGhDZAB0ZD'
INSTAGRAM_BUSINESS_ACCOUNT_ID = '17841449053633062'

def get_hashtag_id(hashtag, access_token):
    url = f"https://graph.facebook.com/ig_hashtag_search?user_id={INSTAGRAM_BUSINESS_ACCOUNT_ID}&q={hashtag}&access_token={access_token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        hashtag_data = response.json()['data']
        if hashtag_data:
            return hashtag_data[0]['id']
    except requests.exceptions.RequestException as e:
        print(f"Error al buscar el ID del hashtag: {e}")
        return None

def get_hashtag_posts(hashtag_id, access_token):
    url = f"https://graph.facebook.com/{hashtag_id}/top_media?user_id={INSTAGRAM_BUSINESS_ACCOUNT_ID}&fields=id,caption,media_type,media_url,permalink,timestamp&access_token={access_token}&limit=100"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener publicaciones del hashtag: {e}")
        return None

# Lista de variaciones del hashtag
hashtags = 'GarageGuayasEs'

# Almacenar todos los resultados aquí
all_posts_data = []

for hashtag in hashtags:
    hashtag_id = get_hashtag_id(hashtag, ACCESS_TOKEN)
    if hashtag_id:
        posts_data = get_hashtag_posts(hashtag_id, ACCESS_TOKEN)
        if posts_data and 'data' in posts_data:
            all_posts_data.extend(posts_data['data'])

if all_posts_data:
    df_posts = pd.json_normalize(all_posts_data)
    df_posts.fillna(value="", inplace=True)

    # Configuración de Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('data-analyst-415118-c4756ee9fde6.json', scope)
    client = gspread.authorize(creds)

    # Seleccionar la hoja específica
    sheet_name = "HOJA"
    sheet = client.open(sheet_name).get_worksheet(4)  # Asume que '4' es el índice para la hoja #5

    # Preparar datos para Google Sheets
    datos_para_google_sheets = df_posts.values.tolist()
    datos_para_google_sheets.insert(0, df_posts.columns.to_list())
    datos_para_google_sheets = [[str(item) for item in row] for row in datos_para_google_sheets]
    sheet.update('A1', datos_para_google_sheets, value_input_option='USER_ENTERED')
    print("Datos de publicaciones con variaciones del hashtag enviados a Google Sheets con éxito.")
else:
    print("No se pudieron obtener los datos de las publicaciones del hashtag y sus variaciones.")
