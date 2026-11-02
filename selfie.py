"""
Satellite Selfie
================
Fetches a daily true-color satellite image of Southeast/Central Texas
from NASA GIBS (Terra MODIS Corrected Reflectance), uploads it to
Google Drive, and sends it to Telegram.

Flow:
    1. Request yesterday's image from the GIBS WMS endpoint
    2. Verify the response is an image (WMS can return XML errors with HTTP 200)
    3. Send the image to Telegram as a document (full resolution)
    4. Upload the image to a Google Drive folder

Configuration (environment variables, or a local .env file):
    TELEGRAM_TOKEN      Telegram bot token from @BotFather
    TELEGRAM_CHAT_ID    Chat ID to send the image to
    token.json          Google OAuth token (drive.file scope)

Runs daily via GitHub Actions (.github/workflows/selfie.yml).

Imagery: NASA Global Imagery Browse Services (GIBS), part of NASA's
Earth Science Data and Information System (ESDIS).
"""



import requests
from datetime import date, timedelta

from dotenv import load_dotenv

import io
import os.path
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

day = (date.today() - timedelta(days=1)).isoformat()  # yesterday's pass is complete
params = {
    "SERVICE": "WMS", "REQUEST": "GetMap", "VERSION": "1.3.0",
    "LAYERS": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "CRS": "EPSG:4326",
    "BBOX": "28.7233,-101.6389,33.9862,-92.9241",   # minLat,minLon,maxLat,maxLon
    "WIDTH": 3872, "HEIGHT":2338,
    "FORMAT": "image/jpeg", "TIME": day,
}
load_dotenv()
chat_id = os.environ["TELEGRAM_CHAT_ID"] #Zine
token = os.environ["TELEGRAM_TOKEN"]
message_caption = f"Satellite Selfie {day}!"
def send_telegram(data):
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendDocument",
        data={"chat_id": chat_id,
              "caption": message_caption,
              },
        files={"document": (f"Houston_{day}.jpeg", data)},
        )

def upload_basic(data):
    ### Initializing credits and token for drive
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "SelfieCredentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        ###CALL FOR DRIVE
        file_metadata = {"name": f"Houston_{day}.jpeg", "parents":["1kEa8zkLH7z61Owmy2mzfA7qwF6mqwSwC"]}
        media = MediaIoBaseUpload(io.BytesIO(data), mimetype="image/jpeg")
        file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
        )

    except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")

def main():
    

    r = requests.get("https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi", params=params)
    r.raise_for_status()
    if not r.headers.get("Content-Type", "").startswith("image/"):
        raise RuntimeError(f"GIBS didn't return an image:\n{r.text[:500]}")
    else:
        send_telegram(r.content)
        upload_basic(r.content)
    #open(f"houston_{day}.jpg", "wb").write(r.content)

if __name__ == "__main__":
    main()