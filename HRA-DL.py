#!/usr/bin/env python3

# Standard
import os
import re
import json
import time
import platform

# Third party
import requests
from bs4 import BeautifulSoup

def getOs():
	osPlatform = platform.system()
	if osPlatform == 'Windows':
		return True
	else:
		return False

def osCommands(x):
	if getOs():
		if x == "p":
			os.system('pause >nul')
		elif x == "c":
			os.system('cls')
		elif x == "t":
			os.system('title HRA-DL R1 (by Sorrow446)')
	else:
		if x == "p":
			os.system("read -rsp $\"\"")
		elif x == "c":
			os.system('clear')
		elif x == "t":
			sys.stdout.write("\x1b]2;HRA-DL R1 (by Sorrow446)\x07")

def login(email, pwd):
	loginGetReq = requests.get('https://streaming.highresaudio.com:8182/vault3/user/login?',
		headers={
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
			},
		params={
			"password":pwd,
			"username":email
			}
		)
	if loginGetReq.status_code == 200:
		loginGetReqJ = loginGetReq.json()
		if not loginGetReqJ['has_subscription']:
			print("Account has no subscription.")
			osCommands('p')
		else:
			print("Signed in successfully.\n")

			return loginGetReqJ['country'], loginGetReqJ['session_id'], loginGetReqJ['user_id'], loginGetReq.text
	else:
		print(f"Failed to sign in. Response from API: {loginGetReq.text}")
		osCommands('p')

# The API doesn't initially return album IDs, so we need to fetch it from the html.
def fetchAlbumId(url):
	soup = BeautifulSoup(requests.get(url, headers={
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"}).text, "html.parser")
	return soup.find(attrs={"data-id": True})['data-id']

def fetchMetadata(albumId, userData):
	metaGetReq = requests.get('https://streaming.highresaudio.com:8182/vault3/vault/album/?',
		params={
		"album_id":albumId,
		"userData":userData
		}
	)
	if metaGetReq.status_code != 200:
		print(f"Failed to fetch album metadata. Response from API: {metaGetReq.text}")
		osCommands('p')
	else:
		return metaGetReq.json()

def dirSetup(albumFolder):
	if not os.path.isdir(albumFolder):
		os.makedirs(albumFolder)

def fileSetup(fname):
	if os.path.isfile(fname):
		os.remove(fname)
		
def fetchTrack(albumId, albumFolder, fname, spec, trackNum, trackTitle, trackTotal, url):
	headers={
	"range": "bytes=0-",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
	"referer": f"https://stream-app.highresaudio.com/album/{albumId}"
	}
	print(f"Downloading track {trackNum} of {trackTotal}: {trackTitle} - {spec}")
	# Would have liked to have used pySmartDL instead, 
	# but it causes 403s for this specific site, so we'll use requests instead.
	with open(fname, 'wb') as f:
		f.write(requests.get(url, headers=headers).content)
		
def fetchBooklet(url, dest):
	headers={
	"range": "bytes=0-",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
	"referer": f"https://stream-app.highresaudio.com/album/{albumId}"
	}
	fileSetup(dest)
	with open(dest, 'wb') as f:
		f.write(requests.get(url, headers=headers).content)
	
def sanitizeFname(fname):
	if getOs():
		return re.sub(r'[\\/:*?"><|]', '-', fname)
	else:
		return re.sub('/', '-', fname)
	
def main(userData):	
	url = input("Input HIGHRESAUDIO Store URL:")
	if not url.strip():
		osCommands('c')
		return
	elif not re.match(r"https?://(?:www\.)?highresaudio\.com/[a-z]{2}/album/view/(\w{6})/-?(?:\w*-?)*", url):
		print("Invalid URL.")
		time.sleep(1)
		osCommands('c')
		return
	albumId = fetchAlbumId(url)
	metadata = fetchMetadata(albumId, userData)
	albumFolder = f"{metadata['data']['results']['artist']} - {metadata['data']['results']['title']}"
	print(f"{albumFolder}\n")
	albumFolderS = dirSetup(f"HRA-DL downloads/{sanitizeFname(albumFolder)}")
	for tracks in [x for x in metadata['data']['results']['tracks']]:
		preFname = f"HRA-DL downloads/{sanitizeFname(albumFolder)}/{str(tracks['trackNumber']).zfill(2)}.flac"
		postFname = f"HRA-DL downloads/{sanitizeFname(albumFolder)}/{str(tracks['trackNumber']).zfill(2)}. {tracks['title']}.flac"
		fileSetup(preFname)
		fileSetup(postFname)
		fetchTrack(albumId, sanitizeFname(albumFolder), preFname, f"{tracks['format']} kHz FLAC", str(tracks['trackNumber']).zfill(2), tracks['title'], str(len(tracks)).zfill(2), tracks['url'])
		os.rename(preFname, postFname)	
	if "booklet" in metadata['data']['results']:
		print("Booklet available. Downloading...")
		fetchBooklet(metadata['data']['results']['booklet'], f"HRA-DL downloads/{albumFolderS}/booklet.pdf")
	print("Returning to URL input screen...")
	time.sleep(1)
	osCommands('c')
		
if __name__ == '__main__':
	osCommands('t')
	with open("config.json") as f:
		config = json.load(f)
		userData = login(config["email"], config["password"])	
	while True:
		main(userData)
