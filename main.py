import requests, json, subprocess, os
from fastapi import FastAPI
import xml.etree.ElementTree as ET
import time

app = FastAPI()

verif = ['.FRENCH.', '.TRUEFRENCH.', '.MULTI.', '.MULTi.', '.VFQ', ' FRENCH ', ' TRUEFRENCH ', ' MULTI ', ' MULTi ', ' VFQ ']
nonverif = ['BLUERAY', 'BLURAY', 'BLU-RAY', 'BLU RAY', 'BLU-RAY', 'DVD', 'BDRip', '2160', 'WEBRip', 'WebRip']

ns = {'atom': 'http://www.w3.org/2005/Atom', 'torznab': 'http://torznab.com/schemas/2015/feed'}

api = "REAL-DEBRID-API-KEY"

jackettUrl = "JACKETT-URL"
jackettApiKey = "JACKETT-API-KEY"
jackettCatFilm = "JACKETT-CAT"
jackettCatSeries = "JACKETT-CAT"

def getNum(s):
    if s < 9:
        entier_formatte = f"{s:02}"
    else:
        entier_formatte = str(s)
    
    return entier_formatte

def add_torrent(magnet_link):
    response = requests.post(
        f"https://api.real-debrid.com/rest/1.0/torrents/addMagnet",
        headers={"Authorization": f"Bearer {api}"},
        data={"magnet": magnet_link}
    )
    torrent_id = response.json().get("id")
    return torrent_id

def get_torrent_info(torrent_id):
    response = requests.get(
        f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}",
        headers={"Authorization": f"Bearer {api}"}
    )
    return response.json()

def wait_for_conversion(torrent_id):
    while True:
        file_info = get_torrent_info(torrent_id)
        file_status = file_info.get("status")
        if file_status != "magnet_conversion":
            break
        time.sleep(15)

def select_biggest_file(torrent_info):
    files = torrent_info.get("files", [])
    biggest_file_index = max(range(len(files)), key=lambda i: files[i].get("bytes", 0))
    return biggest_file_index + 1

def select_biggest_file_season(se, torrent_info):
    files = torrent_info.get("files", [])    
    fichiers = []
    for file in files:
        if se in file['path']:
            fichiers.append(file)
    biggest_file_index = max(range(len(fichiers)), key=lambda i: fichiers[i].get("bytes", 0))
    ok = fichiers[biggest_file_index]['id']
    biggest_file_index = ok
    return biggest_file_index

def wait_for_links(torrent_id):
    while True:
        file_info = get_torrent_info(torrent_id)
        number_links = len(file_info.get("links", []))
        if number_links >= 1:
            break
        time.sleep(5)

def download_torrent(api, torrent_id):
    file_info = get_torrent_info(torrent_id)
    rd_link = file_info.get("links", [])[0]
    response = requests.post(
        f"https://api.real-debrid.com/rest/1.0/unrestrict/link",
        headers={"Authorization": f"Bearer {api}"},
        data={"link": rd_link}
    )
    download_link = response.json().get("download")
    return download_link

@app.get("/film/{id}")
def film(id: str):
    response = requests.get(f"https://cinemeta-live.strem.io/meta/movie/{id}.json")
    film = json.loads(response.text)["meta"]["name"]
    response = requests.get(f"{jackettUrl}/api/v2.0/indexers/all/results/torznab/api?apikey={jackettApiKey}&t=search&cat={jackettCatFilm}&q={film}")
    root = ET.fromstring(response.text)
    resultat = []
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        if any(x in title for x in verif):
            if not any(x in title for x in nonverif):
                resultat.append(title)
                resultat.append(link)
    response = requests.get(resultat[1])
    with open("./torrent.torrent", 'wb') as torrent_file:
            torrent_file.write(response.content)
    command = 'aria2c --show-files=true --bt-metadata-only=true --bt-save-metadata=true -d "test" torrent.torrent'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    magnet_uri_line = [line for line in output.decode('utf-8').split('\n') if 'Magnet URI' in line]
    magnet_uri = magnet_uri_line[0].split(':', 1)[1].strip()
    torrent_id = add_torrent(magnet_uri)
    wait_for_conversion(torrent_id)

    torrent_info = get_torrent_info(torrent_id)
    biggest_file_index = select_biggest_file(torrent_info)

    selected_file_id = requests.post(
        f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}",
        headers={"Authorization": f"Bearer {api}"},
        data={"files": biggest_file_index}
    )

    wait_for_links(torrent_id)

    media_link = download_torrent(api, torrent_id)
    return {'link': media_link, 'name': resultat[0]}

@app.get("/serie/{id}")
def serie(id: str):
    id = id.split(":")
    serie = id[0]
    saison = getNum(int(id[1]))
    episode = getNum(int(id[2]))
    se = f'S{saison}E{episode}'
    response = requests.get(f"https://v3-cinemeta.strem.io/meta/tv/{serie}.json")
    serie = json.loads(response.text)['meta']['name']
    url = f'{jackettUrl}/api/v2.0/indexers/all/results/torznab/api?apikey={jackettApiKey}&t=search&cat={jackettCatSeries}&q={serie}+{se}'
    response = requests.get(url)
    root = ET.fromstring(response.text)
    resultat = []
    isSeasonFile = False
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        if se in title:
            if any(x in title for x in verif):
                if not any(x in title for x in nonverif):
                    if int(item.find('.//torznab:attr[@name="seeders"]', ns).attrib['value']) > 1:
                        resultat.append(title)
                        resultat.append(link)
                        break
                    else:
                        isSeasonFile = True
        else:
            isSeasonFile = True
        if isSeasonFile == True:
            if f"S{saison}" in title:
                url = f'{jackettUrl}/api/v2.0/indexers/all/results/torznab/api?apikey={jackettApiKey}&t=search&cat={jackettCatSeries}&q={serie.replace(" ", "+")}+S{saison}'
                response = requests.get(url)
                root = ET.fromstring(response.text)
                resultat = []
                for item in root.findall('.//item'):
                    title = item.find('title').text
                    link = item.find('link').text
                    if any(x in title for x in verif):
                        if not any(x in title for x in nonverif):
                            if int(item.find('.//torznab:attr[@name="seeders"]', ns).attrib['value']) > 1:
                                resultat.append(title)
                                resultat.append(link)
                                isSeasonFile = True
    if resultat == []:
        return {'link': 'Erreur', 'name': 'Aucun épisode trouvé'}
    if isSeasonFile != True:
        response = requests.get(resultat[1])
        with open("./torrent.torrent", 'wb') as torrent_file:
                torrent_file.write(response.content)
        command = 'aria2c --show-files=true --bt-metadata-only=true --bt-save-metadata=true -d "test" torrent.torrent'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output, error = process.communicate()
        magnet_uri_line = [line for line in output.decode('utf-8').split('\n') if 'Magnet URI' in line]
        magnet_uri = magnet_uri_line[0].split(':', 1)[1].strip()
        torrent_id = add_torrent(magnet_uri)
        wait_for_conversion(torrent_id)

        torrent_info = get_torrent_info(torrent_id)
        biggest_file_index = select_biggest_file(torrent_info)

        selected_file_id = requests.post(
            f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}",
            headers={"Authorization": f"Bearer {api}"},
            data={"files": biggest_file_index}
        )

        wait_for_links(torrent_id)

        media_link = download_torrent(api, torrent_id)
        return {'link': media_link, 'name': resultat[0]}
    else:
        response = requests.get(resultat[1])
        with open("./torrent.torrent", 'wb') as torrent_file:
                torrent_file.write(response.content)
        command = 'aria2c --show-files=true --bt-metadata-only=true --bt-save-metadata=true -d "test" torrent.torrent'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output, error = process.communicate()
        magnet_uri_line = [line for line in output.decode('utf-8').split('\n') if 'Magnet URI' in line]
        magnet_uri = magnet_uri_line[0].split(':', 1)[1].strip()
        torrent_id = add_torrent(magnet_uri)
        wait_for_conversion(torrent_id)

        torrent_info = get_torrent_info(torrent_id)
        biggest_file_index = select_biggest_file_season(se, torrent_info)
        selected_file_id = requests.post(
            f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}",
            headers={"Authorization": f"Bearer {api}"},
            data={"files": biggest_file_index}
        )
        wait_for_links(torrent_id)

        media_link = download_torrent(api, torrent_id)
        return {'link': media_link, 'name': resultat[0].replace(saison, se)}