import fs from "fs";
import { cachePopular } from "./cacheRun.js";

function getConfig() {
	try {
		const config = fs.readFileSync("data/config.json", "utf-8");
		return JSON.parse(config);
	} catch (e) {
		return {
			jackettUrl: "",
			jackettApi: "",
			tmdbApiKey: "",
			languageException: "",
			scrapeEvery: 0,
		};
	}
}

async function startScrape() {
	while (true) {
		while (true) {
			const { jackettUrl, jackettApi, tmdbApiKey, languageException, scrapeEvery } = getConfig();
			if (jackettUrl && jackettApi && tmdbApiKey && languageException && scrapeEvery) {
				let scrapeTime;
				if (scrapeEvery === "6h") scrapeTime = 21600000;
				if (scrapeEvery === "1d") scrapeTime = 86400000;
				if (scrapeEvery === "3d") scrapeTime = 259200000;
				if (scrapeEvery === "week") scrapeTime = 604800000;
				console.log("Caching popular items");
				await cachePopular(jackettUrl, jackettApi, tmdbApiKey, languageException);
				console.log("Cached popular items");
				await new Promise(resolve => setTimeout(resolve, scrapeTime));
				fs.unlinkSync("data/cache.db");
				console.log("Deleted cache");
			} else {
				console.error("Missing config values");
				await new Promise(resolve => setTimeout(resolve, 10000));
			}
		}
	}
}

startScrape();
