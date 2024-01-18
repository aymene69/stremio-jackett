import fetch from 'node-fetch';

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function getNum(s) {
    return s < 10 ? `0${s}` : s.toString();
}

function selectBiggestFileSeason(files, se) {
    return files.find(file => se && file.path.includes(se))?.id || null;
}

function selectBiggestFileSeasonTorrent(files, se) {
    const filteredFiles = files.filter(function(file) {
        return file.name.includes(se);
    });

    if (filteredFiles.length === 0) {
        return null;
    }

    const filesTried = filteredFiles.sort(function(a, b) {
        return b.length - a.length;
    });

        // Trouver l'index du fichier recherché
    const biggestFileId = files.indexOf(filesTried[0]);

    return biggestFileId;
}

function toHomanReadable(bytes) {
    if (Math.abs(bytes) < 1024) { return bytes + ' B'; }
  
    const units = ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
    let i = -1;
    do {
        bytes /= 1024;
        ++i;
    } while (Math.abs(bytes) >= 1024 && i < units.length - 1);
  
    return bytes.toFixed(1) + " " + units[i];
}

function getName(id, type) {
    if (typeof id === 'string') {
        const url = 'https://v3-cinemeta.strem.io/meta/' + type + '/' + id + '.json';
        return fetch(url).then(res => res.json()).then(res => res.meta.name);
    } else {
        return id;
    }
}

async function addMagnetToRD(magnetLink, debridApi) {
    const apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/addMagnet`;
    const headers = {
    Authorization: `Bearer ${debridApi}`,
    };
    const body = new URLSearchParams();
    body.append('magnet', magnetLink);
    
    const response = await fetch(apiUrl, { method: 'POST', headers, body })
    const responseJson = await response.json()
    return responseJson.id
}

async function setMovieFileRD(torrentId, debridApi, seasonEpisode) {
    let responseJson
    while (true) {
        let apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
        let headers = {
        Authorization: `Bearer ${debridApi}`,
        };
    
        let response = await fetch(apiUrl, { method: 'GET', headers })
        responseJson = await response.json()
        let file_status = responseJson["status"]
        if (file_status != "magnet_conversion") {
            break
        }
        await wait(5000)
    }
    let torrentFiles = responseJson["files"]
    let maxIndex
    if (seasonEpisode) {
        maxIndex = selectBiggestFileSeason(torrentFiles, seasonEpisode)
    }
    else { 
        maxIndex = torrentFiles.reduce((maxIndex, file, currentIndex, array) => {
            const currentBytes = file["bytes"] || 0;
            const maxBytes = array[maxIndex] ? array[maxIndex]["bytes"] || 0 : 0;
        
            return currentBytes > maxBytes ? currentIndex : maxIndex;
        }, 0);
    }
    let torrentFileId
    if (seasonEpisode)
        torrentFileId = torrentFiles[maxIndex-1]["id"]
    else
        torrentFileId = torrentFiles[maxIndex]["id"]
    let apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/selectFiles/${torrentId}`;
    let headers = {
    Authorization: `Bearer ${debridApi}`,
    };
    let body = new URLSearchParams();
    body.append('files', torrentFileId);
    let response = await fetch(apiUrl, { method: 'POST', headers, body })

}

async function getMovieRDLink(torrentLink, debridApi, seasonEpisode) {
    let torrentId = await addMagnetToRD(torrentLink, debridApi)
    if (seasonEpisode) {
        await setMovieFileRD(torrentId, debridApi, seasonEpisode)
    }
    else {
        await setMovieFileRD(torrentId, debridApi)
    }
    let responseJson
    while (true) {
        let apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
        let headers = {
        Authorization: `Bearer ${debridApi}`,
        };
    
        let response = await fetch(apiUrl, { method: 'GET', headers })
        responseJson = await response.json()
        let links = responseJson["links"]
        if (links.length >= 1) {
            break
        }
        await wait(5000)
    }

    
    let downloadLink = responseJson["links"][0]

    let apiUrl = `https://api.real-debrid.com/rest/1.0/unrestrict/link`
    let headers = {
    Authorization: `Bearer ${debridApi}`,
    };
    let body = new URLSearchParams();
    body.append('link', downloadLink);
    let response = await fetch(apiUrl, { method: 'POST', headers, body })
    responseJson = await response.json()
    let mediaLink = responseJson["download"]
    return mediaLink
}
export default {
    getNum,
    selectBiggestFileSeasonTorrent,
    selectBiggestFileSeason,
    toHomanReadable,
    getName,
    getMovieRDLink
};
