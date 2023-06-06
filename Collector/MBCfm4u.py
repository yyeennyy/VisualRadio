import json, re
import urllib.request as urllib2
tmp = urllib2.urlopen('https://sminiplay.imbc.com/aacplay.ashx?channel=mfm&protocol=M3U8&agent=webapp&callback=__aacplay').read().decode('utf-8')
url = tmp.split('"')[3]
print(url)