from re import A
import win32com.client
import time
import requests
import base64
import spotipy.util as util
from PIL import Image

print("Starting SpotifySync...")
auraSdk = win32com.client.Dispatch("aura.sdk.1")
auraSdk.SwitchMode()
devices = auraSdk.Enumerate(0)

print("Devices initialized.")
client_id = 'CLIENT-ID'
client_secret = 'CLIENT-SECRET'
username="SPOTIFY-USERNAME"
scope = "user-read-playback-state"
redirect_uri = "REDIRECT-URL"

def refresh_token(): # refreshes token after 1 hour  // will add later
    token = util.refresh_access_token(refresh_token, client_id, client_secret)
    return token

def get_token(): # Gets Spotify access token
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    print("Token received.")
    return token

def rgb_to_hex(rgb): # Generates hex from rgb
    r, g, b = rgb
    hex_code = f'0x{b:02X}{g:02X}{r:02X}'
    return hex_code

def calculate_average_color(image): # Calculates average pixl rgb from album art
    resized_image = image.resize((100, 100))
    rgb_image = resized_image.convert('RGB')
    pixel_data = list(rgb_image.getdata())
    avg_color = tuple(int(sum(channel) / len(pixel_data)) for channel in zip(*pixel_data))
    hex_code = rgb_to_hex(avg_color)
    return hex_code

def calculate_average_color_from_url(image_url): # Gets image contents from Spotify's site
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    return calculate_average_color(image)

def Get_Color(token): # Gets currently playing from Spotfiy API
    if token:
        url = 'https://api.spotify.com/v1/me/player/currently-playing'
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 204:
            print('Waiting for song to play on Spotify...')
            return '0x000000'
        elif response.status_code == 401:
            print('Refreshing token...')
            token = refresh_token()
            return Get_Color()
        response = response.json()
        print(response['item']['name'])
        album_cover_url = response['item']['album']['images'][0]['url']
        average_color = calculate_average_color_from_url(album_cover_url)
        print(average_color)
        return average_color
    else:
        print("Can't get token")

token = get_token()

while True:    # Gets current color and changes RGB for all AuraSync devices
    current_color = int(Get_Color(token), 16)
    for dev in devices:
        for i in range(dev.Lights.Count):
            dev.Lights(i).color = current_color
        dev.Apply()
    time.sleep(5)
