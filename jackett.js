import fetch from 'node-fetch'
import parseTorrent, { toMagnetURI } from 'parse-torrent';
import { Buffer } from "buffer";
import xml2js from 'xml2js';
import helper from './helper.js';

const xml2jsOptions = {
    explicitArray: false,
    ignoreAttrs: false,
};

async function processXML(xml) {
    return new Promise((resolve, reject) => {
        xml2js.parseString(xml, xml2jsOptions, (err, result) => {
            if (err) {
                reject(err);
                return;
            }

            const items = result.rss.channel.item;

            if (!items) {
                resolve([]);
                return;
            }

            const extractedDataArray = Array.isArray(items) ? items.map(item => ({
                title: item.title,
                size: item.size,
                link: item.link,
                seeders: item['torznab:attr'] ? item['torznab:attr'].find(attr => attr.$.name === 'seeders')?.$.value : undefined,
            })) : [{
                title: items.title,
                size: items.size,
                link: items.link,
                seeders: items['torznab:attr'] ? items['torznab:attr'].find(attr => attr.$.name === 'seeders')?.$.value : undefined,
            }];

            // Trier par ordre décroissant du nombre de seeders
            const sortedData = extractedDataArray.sort((a, b) => (b.seeders || 0) - (a.seeders || 0));

            resolve(sortedData);
        });
    });
}

async function getTorrentInfo(torrentLink) {
    try {
        let response = await fetch(torrentLink);
        const torrentBuffer = await response.arrayBuffer();
        const torrentParsed = await parseTorrent(Buffer.from(torrentBuffer))

        const torrentInfo = {
            name: "Jackett",
            infoHash: torrentParsed.infoHash,
            magnetLink: toMagnetURI(torrentParsed),
            seeders: "1",
            fileIdx: 0,
            sources: torrentParsed.announce.map(function(element) {
                return 'tracker:' + element;
              }),
            files: torrentParsed.files.map(file => {
                return {
                    name: file.name,
                    length: file.length
                }
            })
        }
        return torrentInfo;
    } catch (e) {
        return undefined
    }
}

async function jackettSearch(debridApi, jackettHost, jackettApiKey, addonType, searchQuery) {
    if (searchQuery.type == 'movie') {
        try {
            console.log("Searching on Jackett...")
            const searchUrl = jackettHost + '/api/v2.0/indexers/all/results/torznab/api?apikey=' + jackettApiKey + '&cat=2000&q=' + encodeURIComponent(searchQuery.name)
            let response = await fetch(searchUrl);
            let responseXml = await response.text()
            let items = await processXML(responseXml);
            let results = [];
            if (addonType == 'torrent') {
                console.log("Will return Torrents.")
                for (let i = 0; i < 5 ; i++) {
                    let item = items[i];
                    let torrentInfo = await getTorrentInfo(item.link)
                    torrentInfo.seeders = item.seeders
                    torrentInfo.title = item.title + "\r\n👤" + item.seeders + " 📁" + helper.toHomanReadable(item.size)
                    delete torrentInfo.fileIdx
                    results.push(torrentInfo);
                    console.log("Added torrent to results: " + item.title)
                }
                if (results.length == 0) {
                    console.log("No results found.")
                    results.push({ name: "Jackett", title: "Aucun résultat trouvé", url: "#" })
                }
            }
            else {
                console.log("Will return Debrid links.")
                for (let i = 0; i < items.length; i++) {
                    let item = items[i];
                    console.log("Getting torrent info...")
                    let torrentInfo = await getTorrentInfo(item.link)
                    console.log("Torrent info: " + item.title)
                    console.log("Getting RD link...")
                    let downloadLink = await helper.getMovieRDLink(torrentInfo.magnetLink, debridApi)
                    let torrentReturn = {
                        name: "Jackett Debrid",
                        title: item.title + "\r\n📁" + helper.toHomanReadable(item.size),
                        url: downloadLink,
                    }
                    results.push(torrentReturn);
                    break
                }
                if (results.length == 0) {
                    results.push({ name: "Jackett Debrid", title: "Aucun résultat trouvé", url: "#" })
                }
            }
            console.log("Returning results.")
            return results;
        } catch (e) {
            let results = [];
            results.push({ name: "Jackett", title: "Aucun résultat trouvé", url: "#" })
            console.log("Error: " + e)
            return results;
        }
    }
    if (searchQuery.type == 'series') {
        try {
            console.log("Searching on Jackett...")
            const searchUrl = jackettHost + '/api/v2.0/indexers/all/results/torznab/api?apikey=' + jackettApiKey + '&cat=5000' + '&q=' + encodeURIComponent(searchQuery.name) + '+S' + searchQuery.season + 'E' + searchQuery.episode
            let response = await fetch(searchUrl);
            let responseXml = await response.text()
            let items = await processXML(responseXml);
            let results = [];

            if (addonType == 'torrent') {
                console.log("Will return Torrents.")
                for (let i = 0; i < 5 ; i++) {
                    let item = items[i];
                    if (!item) {
                        break
                    }
                    console.log("Getting torrent info...")
                    let torrentInfo = await getTorrentInfo(item.link)
                    console.log("Torrent info: " + item.title)
                    torrentInfo.seeders = item.seeders
                    torrentInfo.title = item.title + "\r\n👤" + item.seeders + " 📁" + helper.toHomanReadable(item.size)
                    results.push(torrentInfo);
                    console.log("Added torrent to results: " + item.title)
                }
                if (results.length == 0) {
                    console.log("No results found with season/episode. Trying without...")
                    console.log("Searching on Jackett...")
                    const searchUrl = jackettHost + '/api/v2.0/indexers/all/results/torznab/api?apikey=' + jackettApiKey + '&cat=5000&q=' + encodeURIComponent(searchQuery.name) + '+S' + searchQuery.season
                    let response = await fetch(searchUrl);
                    let responseXml = await response.text()
                    let items = await processXML(responseXml);
                    let results = [];
                    for (let i = 0; i < items.length; i++) {
                        let item = items[i];
                        console.log("Getting torrent info...")
                        let torrentInfo = await getTorrentInfo(item.link)
                        console.log("Torrent info: " + item.title)
                        torrentInfo.seeders = item.seeders
                        torrentInfo.title = item.title + "\r\n👤" + item.seeders + " 📁" + helper.toHomanReadable(item.size)
                        console.log("Determining episode file...")
                        torrentInfo.fileIdx = parseInt(helper.selectBiggestFileSeasonTorrent(torrentInfo.files, "S" + searchQuery.season+ "E" + searchQuery.episode), 10)
                        console.log("Episode file determined.")
                        results.push(torrentInfo);
                        console.log("Added torrent to results: " + item.title)
                    }
                    if (results.length == 0) {
                        console.log("No results found.")
                        results.push({ name: "Jackett", title: "Aucun résultat trouvé", url: "#" })
                    }
                    return results;
                }
                return results;
            }
            else {
                console.log("Will return Debrid links.")
                for (let i = 0; i < items.length; i++) {
                    let item = items[i];
                    console.log("Getting torrent info...")
                    let torrentInfo = await getTorrentInfo(item.link)
                    console.log("Torrent info: " + item.title)
                    console.log("Getting RD link...")
                    let downloadLink = await helper.getMovieRDLink(torrentInfo.magnetLink, debridApi)
                    let torrentReturn = {
                        name: "Jackett Debrid",
                        title: item.title + "\r\n📁" + helper.toHomanReadable(item.size),
                        url: downloadLink,
                    }
                    results.push(torrentReturn);
                    break
                }
                if (results.length == 0) {
                    const searchUrl = jackettHost + '/api/v2.0/indexers/all/results/torznab/api?apikey=' + jackettApiKey + '&cat=' + "5000" + '&q=' + encodeURIComponent(searchQuery.name) + '+S' + searchQuery.season
                    let response = await fetch(searchUrl);
                    let responseXml = await response.text()
                    let items = await processXML(responseXml);
                    let results = [];
                    for (let i = 0; i < items.length; i++) {
                        let item = items[i];
                        let torrentInfo = await getTorrentInfo(item.link)
                        let downloadLink = await helper.getMovieRDLink(torrentInfo.magnetLink, debridApi, "S" + searchQuery.season+ "E" + searchQuery.episode)
                        let torrentReturn = {
                            name: "Jackett Debrid",
                            title: item.title + "\r\n📁" + helper.toHomanReadable(item.size),
                            url: downloadLink,
                        }
                        results.push(torrentReturn);
                        break
                    }
                    if (results.length == 0) {
                        results.push({ name: "Jackett Debrid", title: "Aucun résultat trouvé", url: "#" })
                    }
                    return results;
                }
                return results;
            }
        }
        catch (e) {
            console.log(e)
            let results = [];
            results.push({ name: "Jackett", title: "Aucun résultat trouvé", url: "#" })
            return results;
        }
    }

};

export default {
    jackettSearch
};
