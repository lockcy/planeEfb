#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/4 15:27
# @Author  : lockcy
# @File    : Spider.py

import requests
import json
from urllib import parse
import re
from bs4 import BeautifulSoup
import os
import shutil
import time
BASE_URL = 'http://skyvector.com'


class SkyRequest:
    def __init__(self):
        self.r = requests.session()

    def get_AP(self, icao):
        html = '''[{"url":"/airport/LAX/Los-Angeles-International-Airport","geom":["-118.40805","33.942497222"],"name":"LOS ANGELES INTL","chart":{"alaska":0,"type":"vfr","expires":23,"validfrom":"2021-12-30 09:01:00","edition":2113,"name":"World VFR","scale":3,"validto":"2022-01-27 09:01:00","lon":-118.40805,"protoid":301,"srs":{"xr":76.43702829,"lon_0":0,"y_0":20037508.3428,"yr":-76.43702829,"lat_1":0,"lat_2":0,"proj":"sm","lat_0":0,"x_0":-20037508.3428},"subtype":"Sectional","maxzoom":21,"width":524288,"height":524288,"tileservers":"https://t.skyvector.com/V7pMh4zRihflnr61,https://t.skyvector.com/V7pMh4zRihflnr61","lat":33.942497222},"type":"APT"}]'''
        # html = self.r.get(url='http://skyvector.com/api/search?q={}'.format(icao))
        html = json.loads(html)
        # html = json.loads(html.text)
        airport_link = parse.urljoin(BASE_URL, html[0].get('url'))
        return airport_link

    def get_Url(self, url):
        # html = self.r.get(url=url)
        # print(html.text)
        with open('klax.html', 'r', encoding='utf-8') as f:
            data = f.read()
        soup = BeautifulSoup(data, 'lxml')
        contents = soup.find_all("div", class_="aptdata")
        url = dict()
        for content in contents:
            g = list()
            content = str(content.contents)
            title = re.search(r'(?<=<div class="aptdatatitle">)(.*?)(?=</div>)', content).group()
            # print(title)
            if re.search(r'/files/.*?\.pdf?', content, re.IGNORECASE):
                graphs = re.findall(r'(/files/[\w|\d|/]+?\.PDF)">(.+)<br/>', content, re.IGNORECASE)
                # graphs = re.findall(r'/files/[\w|\d|/]+?\.PDF', content, re.IGNORECASE)
                for graph in graphs:
                    g.append(graph)
            url.__setitem__(title, g)
        return url

    def batch_download(self, icao):
        path = os.path.join(os.getcwd(), 'data', str(icao))
        if not os.path.exists(path):
            os.mkdir(path)
        url = self.get_AP(icao)
        datas = self.get_Url(url)
        for data in datas:
            d = h.get(data)
            if d:
                cwd = os.path.join(path, data)
                if not os.path.exists(cwd):
                    os.mkdir(cwd)
                for dd in d:
                    self.download_pdf(parse.urljoin(BASE_URL, dd[0]), os.path.join(cwd, dd[1]+'.pdf'))
                    print(parse.urljoin(BASE_URL, dd[0]), dd[1])
                    time.sleep(0.1)

    def download_pdf(self, file_url, filename):
        r = requests.get(file_url, stream=True)
        with open(filename, "wb") as pdf:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    pdf.write(chunk)


if __name__ == '__main__':
    s = SkyRequest()
    airport = s.get_AP('klax')
    h = s.get_Url(airport)
    # s.download_pdf('https://skyvector.com/files/tpp/2113/pdf/00237ANJLL.PDF', 'test.pdf')
    # s.batch_download('klax')

