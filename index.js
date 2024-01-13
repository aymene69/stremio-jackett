import express from 'express';
import cors from 'cors';
import { parseString } from 'xml2js'
import fetch from 'node-fetch'
import torrent2magnet from "torrent2magnet-js";
import { Buffer } from "buffer";
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const app = express();
const port = process.env.PORT || 3000;

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


const noResults = { streams: [{ url: "#", title: "Aucun résultat trouvé" }] }

function getNum(s) {
    let entier_formatte;

    if (s < 9) {
        entier_formatte = `0${s}`;
    } else {
        entier_formatte = s.toString();
    }

    return entier_formatte;
}

function selectBiggestFileSeason(se, torrentInfo) {
    const files = torrentInfo["files"] || [];
    const filteredFiles = [];

    for (const file of files) {
        if (se && file['path'].includes(se)) {
            filteredFiles.push(file);
        }
    }
    const biggestFileIndex = filteredFiles.reduce((maxIndex, file, currentIndex, array) => {
        const currentBytes = file["bytes"] || 0;
        const maxBytes = array[maxIndex] ? array[maxIndex]["bytes"] || 0 : 0;

        return currentBytes > maxBytes ? currentIndex : maxIndex;
    }, 0);

    const biggestFileId = filteredFiles[biggestFileIndex] ? filteredFiles[biggestFileIndex]['id'] : null;

    return biggestFileId;
}

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

var respond = function (res, data) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', '*');
    res.setHeader('Content-Type', 'application/json');
    res.send(data);
};

app.use(cors());

// Route pour le manifeste
app.get('/:rdApi/:jackettUrl/:jackettApi/:jackettIndexer/:jackettMovieCat/:jackettSerieCat/:verif/:nonverif/manifest.json', (req, res) => {
    const manifest = {
        id: 'community.aymene69.jackett',
        version: '1.0.0',
        catalogs: [],
        resources: ['stream'],
        types: ['movie', 'series'],
        name: 'Jackett',
        description: 'Stremio Jackett Addon'
    };
    respond(res, manifest);
});

// Route pour le flux vidéo (OKTest)
app.get('/:rdApi/:jackettUrl/:jackettApi/:jackettIndexer/:jackettMovieCat/:jackettSerieCat/:verif/:nonverif/stream/:type/:id', async (req, res) => {
    const type = req.params.type;
    const id = req.params.id.replace(".json", "");
    const rdApi = req.params.rdApi;
    const jackettUrl = req.params.jackettUrl;
    const jackettApi = req.params.jackettApi;
    const jackettIndexer = req.params.jackettIndexer;
    const jackettMovieCat = req.params.jackettMovieCat;
    const jackettSerieCat = req.params.jackettSerieCat;
    const verif = req.params.verif.split(",");
    const nonverif = req.params.nonverif.split(",");
    const allParams = [type, id, rdApi, jackettUrl, jackettApi, jackettIndexer, jackettMovieCat, jackettSerieCat, verif, nonverif]
    for (const param of allParams) {
        if (param == 'undefined') {
            respond(res, { streams: [{ title: "Jackett misconfigured", url: "#" }] });
        }
    }
  // Simule un flux vidéo pour l'exemple
    if (type == 'movie') {
        let response = await fetch("https://v3-cinemeta.strem.io/meta/movie/" + id + ".json")
        let responseJson = await response.json()
        let filmName = responseJson.meta.name

        response = await fetch("http://" + jackettUrl + "/api/v2.0/indexers/" + jackettIndexer + "/results/torznab/api?apikey=" + jackettApi + "&t=search&cat=" + jackettMovieCat +"&q=" + filmName)
        responseJson = await response.text()
        let items
        parseString(responseJson, function (err, result) {
            items = Object.values(result)[0].channel[0].item
        })
        let result = []
        for(const element of items) {
            let title = element.title[0]
            let link = element.link[0]
            if(title.includes(filmName)) {
                if (verif.some(keyword => title.includes(keyword))) {
                    if (!nonverif.some(keyword => title.includes(keyword))) {
                        result.push(title)
                        result.push(link)
                        break
                    }
                }
            }
        };
        if (result.length == 0) {
            return noResults
        }

        let torrentName = result[0]
        let torrentLink = result[1]

        response = await fetch(torrentLink)

        const torrentBuffer = await response.arrayBuffer();
        const { success, infohash, magnet_uri, dn, xl, main_tracker, tracker_list, is_private, files } = torrent2magnet(Buffer.from(torrentBuffer));
        let magnet = magnet_uri + "&tr=" + main_tracker

        let apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/addMagnet`;
        let headers = {
        Authorization: `Bearer ${rdApi}`,
        };
        let body = new URLSearchParams();
        body.append('magnet', magnet);
    
        response = await fetch(apiUrl, { method: 'POST', headers, body })
        responseJson = await response.json()
        let torrentId = responseJson.id
        
        while (true) {
            apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
            headers = {
            Authorization: `Bearer ${rdApi}`,
            };
        
            response = await fetch(apiUrl, { method: 'GET', headers })
            responseJson = await response.json()
            let file_status = responseJson["status"]
            if (file_status != "magnet_conversion") {
                break
            }
            await wait(5000)
        }

        let torrentFiles = responseJson["files"]

        const maxIndex = torrentFiles.reduce((maxIndex, file, currentIndex, array) => {
            const currentBytes = file["bytes"] || 0;
            const maxBytes = array[maxIndex] ? array[maxIndex]["bytes"] || 0 : 0;
        
            return currentBytes > maxBytes ? currentIndex : maxIndex;
        }, 0);

        let torrentFileId = torrentFiles[maxIndex]["id"]

        apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/selectFiles/${torrentId}`;
        headers = {
        Authorization: `Bearer ${rdApi}`,
        };
        body = new URLSearchParams();
        body.append('files', torrentFileId);
        response = await fetch(apiUrl, { method: 'POST', headers, body })


        while (true) {
            apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
            headers = {
            Authorization: `Bearer ${rdApi}`,
            };
        
            response = await fetch(apiUrl, { method: 'GET', headers })
            responseJson = await response.json()
            let links = responseJson["links"]
            if (links.length >= 1) {
                break
            }
            await wait(5000)
        }

        let downloadLink = responseJson["links"][0]

        apiUrl = `https://api.real-debrid.com/rest/1.0/unrestrict/link`
        headers = {
        Authorization: `Bearer ${rdApi}`,
        };
        body = new URLSearchParams();
        body.append('link', downloadLink);
        response = await fetch(apiUrl, { method: 'POST', headers, body })
        responseJson = await response.json()
        let mediaLink = responseJson["download"]
        respond(res, { streams: [{ title: torrentName, url: mediaLink }] });
    }
    if (type == 'series') {
        let serieId = id.split(":")[0]
        let season = getNum(id.split(":")[1])
        let episode = getNum(id.split(":")[2])
        let seasonEpisode = "S" + season + "E" + episode
        let response = await fetch("https://v3-cinemeta.strem.io/meta/series/" + serieId + ".json")
        let responseJson = await response.json()
        let serieName = responseJson.meta.name
        response = await fetch("http://" + jackettUrl + "/api/v2.0/indexers/" + jackettIndexer + "/results/torznab/api?apikey=" + jackettApi + "&t=search&cat=" + jackettSerieCat + "&q=" + serieName + "+" + seasonEpisode)
        responseJson = await response.text()
        let items
        parseString(responseJson, function (err, result) {
            items = Object.values(result)[0].channel[0].item
        })
        let result = []
        let seasonFile = false
        if (items !== undefined) {
            for (const element of items) {
                let title = element.title[0]
                let link = element.link[0]
                if(title.includes(serieName)) {
                    if(title.includes(seasonEpisode)) {
                        if (verif.some(keyword => title.includes(keyword))) {
                            if (!nonverif.some(keyword => title.includes(keyword))) {
                                result.push(title)
                                result.push(link)
                                break
                            }
                        }
                    }
                    else {
                        response = await fetch("http://" + jackettUrl + "/api/v2.0/indexers/" + jackettIndexer + "/results/torznab/api?apikey=" + jackettApi + "&t=search&cat=" + jackettSerieCat + "&q=" + serieName + "+" + "S" + season)
                        responseJson = await response.text()
                        parseString(responseJson, function (err, result) {
                            items = Object.values(result)[0].channel[0].item
                        })
                        for (const element of items) {
                            title = element.title[0]
                            link = element.link[0]
                            if(title.includes(serieName)) {
                                if(title.includes(season)) {
                                    if (verif.some(keyword => title.includes(keyword))) {
                                        if (!nonverif.some(keyword => title.includes(keyword))) {
                                            result.push(title)
                                            result.push(link)
                                            seasonFile = true
                                            break
                                        }
                                    }
                                }
                            }
                        };
                    }
                }
            };
        }
        else {
            response = await fetch("http://" + jackettUrl + "/api/v2.0/indexers/" + jackettIndexer + "/results/torznab/api?apikey=" + jackettApi + "&t=search&cat=" + jackettSerieCat + "&q=" + serieName + "+" + "S" + season)
            responseJson = await response.text()
            let items
            parseString(responseJson, function (err, result) {
                items = Object.values(result)[0].channel[0].item
            })
            let title
            let link
            for (const element of items) {
                title = element.title[0]
                link = element.link[0]
                if(title.includes(serieName)) {
                    if(title.includes(season)) {
                        if (verif.some(keyword => title.includes(keyword))) {
                            if (!nonverif.some(keyword => title.includes(keyword))) {
                                result.push(title)
                                result.push(link)
                                seasonFile = true
                                break
                            }
                        }
                    }
                }
            };
        }
        if (result.length == 0) {
            respond(res, noResults)
        }
        if (!seasonFile) {
            let torrentName = result[0]
            let torrentLink = result[1]
            response = await fetch(torrentLink)

            const torrentBuffer = await response.arrayBuffer();
            const { success, infohash, magnet_uri, dn, xl, main_tracker, tracker_list, is_private, files } = torrent2magnet(Buffer.from(torrentBuffer));
            let magnet = magnet_uri + "&tr=" + main_tracker
    
    
    
            let apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/addMagnet`;
            let headers = {
            Authorization: `Bearer ${rdApi}`,
            };
            let body = new URLSearchParams();
            body.append('magnet', magnet);
        
            response = await fetch(apiUrl, { method: 'POST', headers, body })
            responseJson = await response.json()
            let torrentId = responseJson.id
    
            while (true) {
                apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
                headers = {
                Authorization: `Bearer ${rdApi}`,
                };
            
                response = await fetch(apiUrl, { method: 'GET', headers })
                responseJson = await response.json()
                let file_status = responseJson["status"]
                if (file_status != "magnet_conversion") {
                    break
                }
                await wait(5000)
            }
            
            let torrentFiles = responseJson["files"]
            const maxIndex = torrentFiles.reduce((maxIndex, file, currentIndex, array) => {
                const currentBytes = file["bytes"] || 0;
                const maxBytes = array[maxIndex] ? array[maxIndex]["bytes"] || 0 : 0;
            
                return currentBytes > maxBytes ? currentIndex : maxIndex;
            }, 0);
    
            let torrentFileId = torrentFiles[maxIndex]["id"]
    
            apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/selectFiles/${torrentId}`;
            headers = {
            Authorization: `Bearer ${rdApi}`,
            };
            body = new URLSearchParams();
            body.append('files', torrentFileId);
            response = await fetch(apiUrl, { method: 'POST', headers, body })
    
    
            while (true) {
                apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
                headers = {
                Authorization: `Bearer ${rdApi}`,
                };
            
                response = await fetch(apiUrl, { method: 'GET', headers })
                responseJson = await response.json()
                let links = responseJson["links"]
                if (links.length >= 1) {
                    break
                }
                await wait(5000)
            }
    
            let downloadLink = responseJson["links"][0]
    
            apiUrl = `https://api.real-debrid.com/rest/1.0/unrestrict/link`
            headers = {
            Authorization: `Bearer ${rdApi}`,
            };
            body = new URLSearchParams();
            body.append('link', downloadLink);
            response = await fetch(apiUrl, { method: 'POST', headers, body })
            responseJson = await response.json()
            let mediaLink = responseJson["download"]
    
            const stream = { url: mediaLink, title: torrentName }
            respond(res,  { streams: [stream] })
        }
        else {
            let torrentName = result[0]
            let torrentLink = result[1]
            response = await fetch(torrentLink)

            const torrentBuffer = await response.arrayBuffer();
            const { success, infohash, magnet_uri, dn, xl, main_tracker, tracker_list, is_private, files } = torrent2magnet(Buffer.from(torrentBuffer));
            let magnet = magnet_uri + "&tr=" + main_tracker
    
    
    
            let apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/addMagnet`;
            let headers = {
            Authorization: `Bearer ${rdApi}`,
            };
            let body = new URLSearchParams();
            body.append('magnet', magnet);
        
            response = await fetch(apiUrl, { method: 'POST', headers, body })
            responseJson = await response.json()
            let torrentId = responseJson.id
    
            let torrentInfo
            while (true) {
                apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
                headers = {
                Authorization: `Bearer ${rdApi}`,
                };
            
                response = await fetch(apiUrl, { method: 'GET', headers })
                responseJson = await response.json()
                torrentInfo = responseJson
                let file_status = responseJson["status"]
                if (file_status != "magnet_conversion") {
                    break
                }
                await wait(5000)
            }
    
            let torrentFileId = selectBiggestFileSeason(seasonEpisode, torrentInfo);
            let torrentFiles = torrentInfo["files"]



            apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/selectFiles/${torrentId}`;
            headers = {
            Authorization: `Bearer ${rdApi}`,
            };
            body = new URLSearchParams();
            body.append('files', torrentFileId);
            response = await fetch(apiUrl, { method: 'POST', headers, body })
    
    
            while (true) {
                apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
                headers = {
                Authorization: `Bearer ${rdApi}`,
                };
            
                response = await fetch(apiUrl, { method: 'GET', headers })
                responseJson = await response.json()
                let links = responseJson["links"]
                if (links.length >= 1) {
                    break
                }
                await wait(5000)
            }
    
            let downloadLink = responseJson["links"][0]
    
            apiUrl = `https://api.real-debrid.com/rest/1.0/unrestrict/link`
            headers = {
            Authorization: `Bearer ${rdApi}`,
            };
            body = new URLSearchParams();
            body.append('link', downloadLink);
            response = await fetch(apiUrl, { method: 'POST', headers, body })
            responseJson = await response.json()
            let mediaLink = responseJson["download"]
    
            const stream = { url: mediaLink, title: torrentName.replace("S" + season, seasonEpisode) }
            respond(res,  { streams: [stream] })
        }
    }
});

app.get('/configure', (req, res) => {
    res.sendFile(__dirname + '/index.html');
})

app.get('/', (req, res) => {
    res.redirect('/configure');
})

app.listen(port, () => {
    console.log(`Server is running at https://localhost:${port}`);
});
