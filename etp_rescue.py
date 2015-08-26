#!/usr/bin/env python3

from csv import DictWriter
from collections import OrderedDict

import requests

from bs4 import BeautifulSoup

def rescue():
    '''Obtain the most recent available copy from the Internet Archive and extract data.'''

    r = requests.get('https://web.archive.org/web/20091126015235/http://etp.classics.umass.edu/cgi-bin/query.pl')
    soup = BeautifulSoup(r.text, 'html5lib')

    docs = soup.find_all('div', class_='document')
    doclist = []
    for doc in docs:
        contents = [content for content in doc.contents if content != '\n']
        docd = OrderedDict()
        for con in contents:
            if con.name == 'h3':
                docd['etp_id'], docd['desc'] = [s.strip() for s in con.string.split(':', 1)]
            if con.name == 'div':
                try:
                    con['class']
                except KeyError:
                    pass
                else:
                    if con['class'][0] == 'text':
                        docd['text'] = con.encode_contents().strip().decode()
                if con.contents[0].startswith('Citation:'):
                    docd['citation'] = con.string.split(':')[1].strip()
                if con.contents[0].startswith('Editor:'):
                    docd['editor'] = con.a.string
                if con.contents[0].startswith('Type:'):
                    docd['type'] = con.a.string
                if con.contents[0].startswith('Location:'):
                    docd['location'] = con.a.string
                if con.contents[0].startswith('Date:'):
                    docd['from'], docd['to'] = [year.split('=')[1] for year in con.a['href'].split('?')[1].split('&')]
                if con.contents[0].startswith('Notes:'):
                    docd['notes'] = con.encode_contents()[8:].strip().decode()
                if con.contents[0].startswith('Bibliography:'):
                    docd['bibliography'] = con.encode_contents()[14:].strip().decode()
        doclist.append(docd)

    with open('etp-export.csv', 'w') as save:
        dw = DictWriter(save, fieldnames=doclist[0].keys())
        dw.writeheader()
        dw.writerows(doclist)

if __name__ == '__main__':
    rescue()
