import fs from "fs";
import { cachePopular } from "./cacheRun.js";

function getConfig() {
	const config = fs.readFileSync("config.json", "utf-8");
	return JSON.parse(config);
}

async function startScrape() {
	while (true) {
		while (true) {
			const { jackettUrl, jackettApi, tmdbApiKey, languageException, scrapeEvery } = getConfig();
			if (jackettUrl && jackettApi && tmdbApiKey && languageException && scrapeEvery) {
				console.log("Caching popular items");
				await cachePopular(jackettUrl, jackettApi, tmdbApiKey, languageException);
				console.log("Cached popular items");
				await new Promise(resolve => setTimeout(resolve, scrapeEvery));
				fs.unlinkSync("cache.db");
				console.log("Deleted cache");
			} else {
				console.log(jackettUrl, jackettApi, tmdbApiKey, languageException, scrapeEvery);
				console.error("Missing config values");
				await new Promise(resolve => setTimeout(resolve, 10000));
			}
		}
	}
}

startScrape();
