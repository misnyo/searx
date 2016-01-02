"""
 Torrentz (Videos, Music, Files)

 @website     https://torrentz.eu/
 @provide-api no (nothing found)

 @using-api   no
 @results     HTML (using search portal)
 @stable      yes (HTML can change)
 @parse       url, title, content, seed, leech, magnetlink
"""

from urlparse import urljoin
from urllib import quote
from lxml import html
from operator import itemgetter
from searx.engines.xpath import extract_text
from searx.poolrequests import get as http_get

# engine dependent config
categories = ['videos', 'music', 'files']
paging = True

# search-url
url = 'https://torrentz.eu/'
search_url = url + 'search?q={search_term}&p={pageno}'


# do search-request
def request(query, params):
    params['url'] = search_url.format(search_term=quote(query),
                                      pageno=params['pageno'])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    search_res = dom.xpath('//div[@class="results"]//dl')

    # return empty array if nothing is found
    if not search_res:
        return []

    # parse results
    for result in search_res:
        link = result.xpath('.//dt/a')
        if len(link) == 0:
            continue
        link = link[0]
        href = urljoin(url, link.attrib['href'])
        title = extract_text(link)
        content = ""
        seed = result.xpath('.//dd/span[@class="u"]/text()')[0]
        leech = result.xpath('.//dd/span[@class="d"]/text()')[0]
        size_data = result.xpath('.//dd/span[@class="s"]/text()')

        # convert seed to int if possible
        if seed.isdigit():
            seed = int(seed)
        else:
            seed = 0

        # convert leech to int if possible
        if leech.isdigit():
            leech = int(leech)
        else:
            leech = 0

        # convert filesize to byte if possible
        try:
            filesize, filesize_multiplier = size_data[0].split()
            filesize = float(filesize)

            # convert filesize to byte
            if filesize_multiplier == 'TB':
                filesize = int(filesize * 1024 * 1024 * 1024 * 1024)
            elif filesize_multiplier == 'GB':
                filesize = int(filesize * 1024 * 1024 * 1024)
            elif filesize_multiplier == 'MB':
                filesize = int(filesize * 1024 * 1024)
            elif filesize_multiplier == 'KB':
                filesize = int(filesize * 1024)
        except:
            filesize = None

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'seed': seed,
                        'leech': leech,
                        'filesize': filesize,
                        'template': 'torrent.html'})

    # return results sorted by seeder
    return sorted(results, key=itemgetter('seed'), reverse=True)
