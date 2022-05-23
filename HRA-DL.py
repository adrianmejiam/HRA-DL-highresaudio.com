#!/usr/bin/env python3

# Standard
import os
import re
import sys
import json
import time
import platform
import traceback

# Third party
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"})

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
			os.system('title HRA-DL R1a (by Sorrow446)')
	else:
		if x == "p":
			os.system("read -rsp $\"\"")
		elif x == "c":
			os.system('clear')
		elif x == "t":
			sys.stdout.write("\x1b]2;HRA-DL R1a (by Sorrow446)\x07")

def login(email, pwd):
	r = session.get(f'https://streaming.highresaudio.com:8182/vault3/user/login?password={pwd}&username={email}')
	if r.status_code == 200:
		if "has_subscription" in r.json():
			print("Signed in successfully.\n")
			return r.text
		else:
			print("Account has no subscription.")
			osCommands('p')
		
	else:
		print(f"Failed to sign in. Response from API: {r.text}")
		osCommands('p')

# The API doesn't initially return album IDs, so we need to fetch it from the html.
def fetchAlbumId(url):
	soup = BeautifulSoup(session.get(url).text, "html.parser")
	return soup.find(attrs={"data-id": True})['data-id']

def fetchMetadata(albumId, userData):
	r = session.get(f'https://streaming.highresaudio.com:8182/vault3/vault/album/?album_id={albumId}&userData={userData}')
	if r.status_code != 200:
		print(f"Failed to fetch album metadata. Response from API: {r.text}")
		osCommands('p')
	else:
		return r.json()

def dirSetup(albumFolder):
	if not os.path.isdir(albumFolder):
		os.makedirs(albumFolder)
	return albumFolder

def fileSetup(fname):
	if os.path.isfile(fname):
		os.remove(fname)
		
def fetchTrack(albumId, albumFolder, fname, spec, trackNum, trackTitle, trackTotal, url):
	session.headers.update({"range":"bytes=0-", "referer":f"https://stream-app.highresaudio.com/album/{albumId}"})
	print(f"Downloading track {trackNum} of {trackTotal}: {trackTitle} - {spec}")
	# Would have liked to have used pySmartDL instead, 
	# but it causes 403s for this specific site, so we'll use requests instead.		
	r = session.get(url, stream=True)
	size = int(r.headers.get('content-length', 0))
	# if r.status_code != 200:
		# print(f"Failed to fetch track. Response from API: {r.text}")
		# osCommands('p')
	with open(fname, 'wb') as f:
		with tqdm(total=size, unit='B',
			unit_scale=True, unit_divisor=1024,
			initial=0, miniters=1) as bar:		
				for chunk in r.iter_content(32 * 1024):
					if chunk:
						f.write(chunk)
						bar.update(len(chunk))
		
def fetchBooklet(url, dest, albumId):
	fileSetup(dest)
	r = session.get(url, stream=True)
	size = int(r.headers.get('content-length', 0))
	# if r.status_code != 200:
		# print(f"Failed to fetch track. Response from API: {r.text}")
		# osCommands('p')
	# Don't really need to iter booklets, but oh well.
	with open(dest, 'wb') as f:
		with tqdm(total=size, unit='B',
			unit_scale=True, unit_divisor=1024,
			initial=0, miniters=1) as bar:		
				for chunk in r.iter_content(32 * 1024):
					if chunk:
						f.write(chunk)
						bar.update(len(chunk))
	
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
	osCommands('c')
	albumId = fetchAlbumId(url)
	metadata = fetchMetadata(albumId, userData)
	albumFolder = f"{metadata['data']['results']['artist']} - {metadata['data']['results']['title']}"
	print(f"{albumFolder}\n")
	albumFolderS = dirSetup(f"/data/data/com.termux/files/home/storage/music/{sanitizeFname(albumFolder)}")
	for tracks in [x for x in metadata['data']['results']['tracks']]:
		preFname = f"/data/data/com.termux/files/home/storage/music/{sanitizeFname(albumFolder)}/{str(tracks['trackNumber']).zfill(2)}.flac"
		postFname = f"/data/data/com.termux/files/home/storage/music/{sanitizeFname(albumFolder)}/{str(tracks['trackNumber']).zfill(2)}. {sanitizeFname(tracks['title'])}.flac"
		fileSetup(preFname)
		fileSetup(postFname)
		fetchTrack(albumId, sanitizeFname(albumFolder), preFname, f"{tracks['format']} kHz FLAC", str(tracks['trackNumber']).zfill(2), tracks['title'], str(len([x for x in metadata['data']['results']['tracks']])).zfill(2), tracks['url'])
		os.rename(preFname, postFname)
	if "booklet" in metadata['data']['results']:
		print("Booklet available. Downloading...")
		fetchBooklet(f"https://{metadata['data']['results']['booklet']}", f"{albumFolderS}/booklet.pdf", albumId)
	print("Returning to URL input screen...")
	time.sleep(1)
	osCommands('c')
		
if __name__ == '__main__':
	osCommands('t')
	with open("config.json") as f:
		config = json.load(f)
		userData = login(config["email"], config["password"])	
		try:
			while True:
				main(userData)
		except (KeyboardInterrupt, SystemExit):
			sys.exit()
		except:
			traceback.print_exc()
			input("\nAn exception has occurred. Press enter to exit.")
		sys.exit()
