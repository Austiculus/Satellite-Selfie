# Satellite Selfie

A daily satellite "selfie" of Southeast and Central Texas. Every day, this project pulls yesterday's true-color satellite image from NASA and archives it in Google Drive. It runs automatically on GitHub Actions, so no computer needs to stay on.

Sample satellite selfie of Southeast Texas

How it works

Satellite Selfie pipeline

GitHub Actions starts the script once a day on a schedule.
NASA GIBS returns yesterday's Terra MODIS Corrected Reflectance (true color) image for a fixed area, from about Del Rio to the Louisiana line and from the Gulf coast up toward Abilene and Tyler.
Verify: the script checks that the response is actually an image. WMS servers can return an XML error message with an HTTP 200 status, so a status check alone isn't enough. If it isn't an image, the run stops and reports the error.
Google Drive: the image is uploaded to a Drive folder as a long-term archive.

The image is downloaded once and kept in memory, so nothing is written to disk.

Built with
Python 3.12
requests for the NASA call
Google Drive API (google-api-python-client, google-auth-oauthlib) with the limited drive.file scope
GitHub Actions for scheduling
Setup
1. Google Drive
In Google Cloud Console, create a project and enable the Google Drive API.
Create OAuth credentials of type Desktop app and download the JSON file.
On the OAuth consent screen page, set the app to In production. Apps left in Testing mode issue tokens that expire after 7 days.
Run the script once locally. A browser window opens for sign-in, and a token.json file is created.
2. Run it locally
pip install -r requirements.txt
python selfie.py
3. Run it on GitHub Actions

In the repo, go to Settings → Secrets and variables → Actions and add:

Secret	Value
GOOGLE_TOKEN_JSON	The full contents of token.json

The workflow in .github/workflows/selfie.yml runs daily and can also be started by hand from the Actions tab with Run workflow.

Security

token.json and the OAuth client file (selfieCredentials.json) are listed in .gitignore and never committed. On GitHub, the token lives only in an encrypted repository secret.

Roadmap

Moving the project to AWS as the first module of a personal portfolio site:

[ ] Run the script on an EC2 instance that boots once a day, runs the job, and shuts itself down
[ ] Upload each image to S3, as latest.jpg plus a dated copy for history
[ ] Show the latest image on a static website hosted in S3
[ ] Add NASA DONKI space weather data as a second module
Credits

Imagery courtesy of NASA's Global Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS).