import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import http from 'http';
import helper from './helper.js';
import jackett from './jackett.js';

const app = express();
const port = process.env.PORT || 3000;

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


const noResults = { streams: [{ url: "#", title: "Aucun résultat trouvé" }] }


const server = http.createServer(app);
const serverTimeout = 120000;
server.timeout = serverTimeout;

var respond = function (res, data) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', '*');
    res.setHeader('Content-Type', 'application/json');
    res.send(data);
};

app.use(cors());

app.get('/:debridApi/:service/:jackettUrl/:jackettApi/manifest.json', (req, res) => {
    const manifest = {
        id: 'community.aymene69.jackett',
        version: '1.0.0',
        catalogs: [],
        resources: ['stream'],
        types: ['movie', 'series'],
        name: 'Jackett',
        description: 'Stremio Jackett Addon',
        behaviorHints: {
            "configurable": true,
        },
    };
    respond(res, manifest);
});

app.use((err, req, res, next) => {
    respond(res, noResults);
});

app.get('/:debridApi/:service/:jackettUrl/:jackettApi/stream/:type/:id', async (req, res) => {
    try {
        const type = req.params.type;
        const id = req.params.id.replace(".json", "").split(':');
        const debridApi = req.params.debridApi;
        const service = req.params.service;
        const jackettUrl = req.params.jackettUrl;
        const jackettApi = req.params.jackettApi;
        const mediaName = await helper.getName(id[0], type)
        if (type == 'movie') {
            const torrentInfo = await jackett.jackettSearch(debridApi, jackettUrl, jackettApi, service, { name: mediaName, type: type });
            console.log(torrentInfo[0])
            respond(res, { "streams": torrentInfo});
        }
        if (type == 'series') {
            const torrentInfo = await jackett.jackettSearch(debridApi, jackettUrl, jackettApi, service, { name: mediaName, type: type, season: helper.getNum(id[1]), episode: helper.getNum(id[2]) });
            console.log(torrentInfo)
            respond(res, { "streams": torrentInfo});
        }
    } catch (e) {
        console.log(e)
        respond(res, noResults);
    }
});

app.get('/configure', (req, res) => {
    res.sendFile(__dirname + '/index.html');
})

app.get('/', (req, res) => {
    res.redirect('/configure');
})

server.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
