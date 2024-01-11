const { addonBuilder } = require("stremio-addon-sdk")

// Docs: https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/api/responses/manifest.md
const manifest = {
	"id": "community.jackett",
	"version": "1.0.0",
	"catalogs": [],
	"resources": [
		"stream"
	],
	"types": [
		"movie",
		"series",
		"tv"
	],
	"name": "Jackett",
	"description": "Stremio Jackett Addon"
}
const builder = new addonBuilder(manifest)

builder.defineStreamHandler(({ type, id }) => {
    console.log("request for streams: " + type + " " + id);

    if (type === "movie") {
        function fetchStream() {
            return fetch("http://your_api_server:port/film/" + id)
                .then(response => response.json());
        }

        return fetchStream().then(streamLink => {
            const stream = { url: streamLink.link, title: streamLink.name }
			return { streams: [stream] };
            });
	}
    if (type === "series") {
        function fetchStream() {
            return fetch("http://your_api_server:port/serie/" + id)
                .then(response => response.json());
        }

        return fetchStream().then(streamLink => {
            const stream = { url: streamLink.link, title: streamLink.name }
            return { streams: [stream] };
            });
        }
}
);

module.exports = builder.getInterface();
