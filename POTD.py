#!/usr/bin/python

import urllib3, urlparse, os, os.path, datetime, time
from bs4 import BeautifulSoup
from gi.repository import Gio

BASE_URL="http://photography.nationalgeographic.com/photo-of-the-day/"
BG_DIR=os.path.expanduser("~/.photo_of_the_day/")
SCHEMA = 'org.gnome.desktop.background'
KEY = 'picture-uri'

http = urllib3.PoolManager()

if not os.path.isdir(BG_DIR):
	os.mkdir(BG_DIR)

def get_photo_url():
	"""Get the url of today's photo from the National Geographic website"""
	url = ''
	r = http.request('GET', BASE_URL)
	if(r.status != 200):
		raise IOError("Failed to load url \'{}\'".format(BASE_URL))

	soup = BeautifulSoup(r.data)

	f = open(os.path.join(BG_DIR, 'page.html'), 'w');
	f.write(soup.prettify().encode('utf8'))
	f.close()
	
	for div in soup.find_all('div', class_='download_link'):
		url = div.find('a').get('href', '')
		break

	if not url:
		for div in soup.find_all('div', class_='primary_photo'):
			url = div.find('img').get('src', '')
			break

	if url.startswith("//"):
		url = "http:{}".format(url)

	if not url:
		raise RuntimeError("Could not find image url")
	
	return url

def fetch_image(url, fname):
	"""Fetch the image given by url and save it in fname"""
	r = http.request('GET', url);
	if(r.status != 200):
		raise IOError("Error fetching image \'{}\'".format(url))
	image = r.data
	f = open(fname, 'wb')
	f.write(image)
	return True

def set_bg(fname):
	"""Set the file fname as the desktop background"""
	print "Setting background \'{}\'".format(fname)
	gsettings = Gio.Settings.new(SCHEMA)
	gsettings.set_string(KEY, "file://{}".format(fname))

def rm_other(tail):
	"""Remove old images from the directory"""
	for f in os.listdir(BG_DIR):
		#don't delete the current image, or myself...
		if f != tail and f != 'POTD.py':
			os.remove(os.path.join(BG_DIR, f))

def update():
	"""Show the latest photo as the desktop wallpaper"""
	url = get_photo_url()
	path = urlparse.urlparse(url).path
	head, tail = os.path.split(path)
	filename = os.path.join(BG_DIR, tail)
	if not os.path.isfile(filename):
		fetch_image(url,filename)
	set_bg(filename)
	rm_other(tail)

if __name__ == '__main__':
	while True:
		update()
		time.sleep(3600)

