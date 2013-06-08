#!/usr/bin/python

import urllib2, urlparse, os, os.path, datetime, time
from bs4 import BeautifulSoup
from gi.repository import Gio

BASE_URL="http://photography.nationalgeographic.com/photography/photo-of-the-day/"
BG_DIR=os.path.expanduser("~/.photo_of_the_day/")
SCHEMA = 'org.gnome.desktop.background'
KEY = 'picture-uri'

if not os.path.isdir(BG_DIR):
	os.mkdir(BG_DIR)

def get_photo_url():
	"""Get the url of today's photo from the National Geographic website"""
	url = ''
	try:
		u = urllib2.urlopen(BASE_URL)
		html = u.read()

		soup = BeautifulSoup(html, "html5lib")

		for div in soup.find_all('div'):
			if 'download_link' in div.get('class', ''):
				url = div.find('a').get('href', '')
				break

		if not url:
			for div in soup.find_all('div'):
				if 'primary_photo' in div.get('class', ''):
					url = div.find('img').get('src', '')
					break

	except urllib2.URLError as e:
		print "Error fetching page: {}".format(str(e))
	return url

def fetch_image(url, fname):
	"""Fetch the image given by url and save it in fname"""
	try:
		u = urllib2.urlopen(url)
		image = u.read()
		f = open(fname, 'wb')
		f.write(image)
	except urllib2.URLError as e:
		print "Error fetching image: {}".format(str(e))
		return False
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

