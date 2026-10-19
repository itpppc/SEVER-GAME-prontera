import urllib.request
import re

req = urllib.request.Request('http://www.bmatraffic.com/index.aspx', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8', 'ignore')
print("Camera mentions:", re.findall(r'.{0,50}showimage.{0,50}', html)[:5])
print("video mentions:", re.findall(r'.{0,50}video.{0,50}', html, re.I)[:5])
print("m3u8 mentions:", re.findall(r'.{0,50}m3u8.{0,50}', html, re.I)[:5])
print("streaming mentions:", re.findall(r'.{0,50}stream.{0,50}', html, re.I)[:5])
