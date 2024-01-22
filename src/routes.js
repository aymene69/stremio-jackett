import { Router } from "express";
import { dirname } from "path";
import { fileURLToPath } from "url";
import helper from "./helper.js";
import { subpath } from "./index.js";
import jackettSearch from "./jackett/index.js";

const routes = Router();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const noResults = { streams: [{ url: "#", title: "No results found" }] };
function respond(res, data) {
	res.setHeader("Access-Control-Allow-Origin", "*");
	res.setHeader("Access-Control-Allow-Headers", "*");
	res.setHeader("Content-Type", "application/json");
	res.send(data);
}

routes.get("/:params/manifest.json", (req, res) => {
	const manifest = {
		id: "community.aymene69.jackett",
		version: "1.0.0",
		catalogs: [],
		resources: ["stream"],
		types: ["movie", "series"],
		name: "Jackett",
		description: "Stremio Jackett Addon",
		behaviorHints: {
			configurable: true,
		},
	};
	respond(res, manifest);
});

routes.use((err, req, res, next) => {
	respond(res, noResults);
});

routes.get("/:params/stream/:type/:id", async (req, res) => {
	try {
		const paramsJson = JSON.parse(atob(req.params.params));
		const type = req.params.type;
		const id = req.params.id.replace(".json", "").split(":");
		const service = paramsJson.streamService;
		const jackettUrl = paramsJson.jackettUrl;
		const jackettApi = paramsJson.jackettApiKey;
		const debridApi = paramsJson.debridApiKey;
		const mediaName = await helper.getName(id[0], type);
		if (type === "movie") {
			console.log(`Movie request. ID: ${id[0]} Name: ${mediaName}`);
			const torrentInfo = await jackettSearch(debridApi, jackettUrl, jackettApi, service, {
				name: mediaName,
				type: type,
			});
			respond(res, { streams: torrentInfo });
		}
		if (type === "series") {
			console.log(
				`Series request. ID: ${id[0]} Name: "${mediaName}" Season: ${helper.getNum(
					id[1],
				)} Episode: ${helper.getNum(id[2])}`,
			);
			const torrentInfo = await jackettSearch(debridApi, jackettUrl, jackettApi, service, {
				name: mediaName,
				type: type,
				season: helper.getNum(id[1]),
				episode: helper.getNum(id[2]),
			});
			respond(res, { streams: torrentInfo });
		}
	} catch (e) {
		console.log(e);
		respond(res, noResults);
	}
});

routes.get("/configure", (req, res) => {
	res.sendFile(`${__dirname}/index.html`);
});

routes.get("/", (req, res) => {
	res.redirect(`${subpath}/configure`);
});

export default routes;
