import { clamp } from "@hyoretsu/utils";
import express, { Router } from "express";
import { existsSync, readFileSync } from "fs";
import handlebars from "handlebars";
import { version } from "../package.json";
import { getName } from "./helpers/getName";
import { getNum } from "./helpers/getNum";
import fetchResults from "./jackett/index";
import { subpath } from "./index";

const routes = Router();

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
		icon: "https://i.imgur.com/tVjqEJP.png",
		version: "1.2.3",
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

routes.get("/:params/configure", (req, res) => {
	const paramsJson = JSON.parse(atob(req.params.params));
	const prefill = `?jackettUrl=${encodeURI(paramsJson.jackettUrl)}&jackettApi=${paramsJson.jackettApiKey}&realDebridApi=${paramsJson.debridApiKey}&allDebridApi=${paramsJson.debridApiKey}&premiumizeDebridApi=${paramsJson.debridApiKey}&serviceProvider=${paramsJson.streamService}&maxResults=${paramsJson.maxResults}&sorting=${paramsJson.sorting}&ascOrDesc=${paramsJson.ascOrDesc}`;
	res.redirect(`${subpath}/configure${prefill}`);
});

routes.get("/:params/stream/:type/:id", async (req, res) => {
	try {
		const paramsJson = JSON.parse(atob(req.params.params));
		const { type } = req.params;
		const id = req.params.id.replace(".json", "").split(":");
		const service = paramsJson.streamService;
		const { jackettUrl } = paramsJson;
		const jackettApi = paramsJson.jackettApiKey;
		const debridApi = paramsJson.debridApiKey;
		const maxResults = clamp(1, paramsJson.maxResults || 5, 15);
		const { sorting } = paramsJson;
		const { ascOrDesc } = paramsJson;
		let sort;
		if (sorting === "sizedesc" || sorting === "sizeasc") {
			sort = {
				sorting: "size",
				ascOrDesc: ascOrDesc,
			};
		} else if (sorting === "quality") {
			sort = {
				sorting: "quality",
				ascOrDesc: ascOrDesc,
			};
		} else {
			sort = {
				sorting: "quality",
				ascOrDesc: "desc",
			};
		}
		console.log(sort);
		const mediaName = await getName(id[0], type);
		if (type === "movie") {
			console.log(`Movie request.\nID: ${id[0]}\nName: ${mediaName.name}`);
			const torrentInfo = await fetchResults(debridApi, jackettUrl, jackettApi, service, maxResults, sort, {
				name: mediaName.name,
				year: mediaName.year,
				type: type,
			});
			respond(res, { streams: torrentInfo });
		}
		if (type === "series") {
			console.log(
				`Series request. ID: ${id[0]}\nName: "${mediaName}"\nSeason: ${getNum(id[1])} Episode: ${getNum(
					id[2],
				)}`,
			);
			const torrentInfo = await fetchResults(debridApi, jackettUrl, jackettApi, service, maxResults, sort, {
				name: mediaName,
				type: type,
				season: getNum(id[1]),
				episode: getNum(id[2]),
			});
			respond(res, { streams: torrentInfo });
		}
	} catch (e) {
		console.log(e);
		respond(res, noResults);
	}
});

routes.get("/", (req, res) => {
	res.redirect(`${subpath}/configure`);
});

const { dirname } = import.meta;

routes.use("/", express.static(`${dirname}/frontend`));

routes.get("/configure", async (req, res) => {
	const template = handlebars.compile(readFileSync(`${dirname}/frontend/configure/index.hbs`, "utf8"));

	res.send(template({ version }));
});

routes.use((req, res, next) => {
	if (!req.path.endsWith(".html")) {
		if (req.path.match(/\..*$/g)) {
			next();
			return;
		}

		const isNamedFile = existsSync(`${dirname}/frontend${req.path}.html`);

		if (isNamedFile) {
			res.sendFile(`${dirname}/frontend${req.path}.html`);
		} else {
			res.sendFile(`${dirname}/frontend${req.path}/index.html`);
		}
	}
});

export default routes;
