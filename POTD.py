#!/usr/bin/python

import urllib3, urlparse, os, os.path, datetime, time
from bs4 import BeautifulSoup
from gi.repository import Gio

BASE_URL="http://www.nationalgeographic.com/photography/photo-of-the-day/"
BG_DIR=os.path.expanduser("~/.photo_of_the_day/")
SCHEMA = 'org.gnome.desktop.background'
KEY = 'picture-uri'

http = urllib3.PoolManager()

if not os.path.isdir(BG_DIR):
    os.mkdir(BG_DIR)

def get_photo_info():
    """Get the url of today's photo from the National Geographic website"""
    url = ''
    title = ''
    r = http.request('GET', BASE_URL)
    if(r.status != 200):
        raise IOError("Failed to load url \'{}\'".format(BASE_URL))

    soup = BeautifulSoup(r.data)

    f = open(os.path.join(BG_DIR, 'page.html'), 'w');
    f.write(soup.prettify().encode('utf8'))
    f.close()

    for meta in soup.find_all('meta', property='og:image'):
        url = meta.get('content', '')
        if url != '':
            break

    for meta in soup.find_all('meta', property='og:title'):
        title = meta.get('content', '')
        if title != '':
            break

    if url.startswith("//"):
        url = "http:{}".format(url)

    if not url:
        raise RuntimeError("Could not find image url")

    return title.encode('utf-8'), url

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
    gsettings = Gio.Settings.new(SCHEMA)
    gsettings.set_string(KEY, "file://{}".format(fname))

def rm_other(keep):
    """Remove old images from the directory"""
    for f in os.listdir(BG_DIR):
        #don't delete the current image, or myself...
        if f != keep and os.path.join(BG_DIR, f) != keep and f != 'POTD.py':
            os.remove(os.path.join(BG_DIR, f))

def to_filename(title):
    keepcharacters = ('.','_')
    tail = "{}.jpg".format("".join(c for c in title if c.isalnum() or c in keepcharacters).rstrip())
    return os.path.join(BG_DIR, tail)

def update():
    """Show the latest photo as the desktop wallpaper"""
    title, url = get_photo_info()
    filename = to_filename(title)

    if not os.path.isfile(filename):
        print("New background: {}".format(title))
        fetch_image(url,filename)
        rm_other(filename)
    #in case someone else set it
    set_bg(filename)

if __name__ == '__main__':
    while True:
        update()
        time.sleep(3600)

