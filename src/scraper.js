import fs from "fs";
import { cachePopular } from "./scraper/cacheRun";
import "dotenv/config";

function getConfig() {
	const config = fs.readFileSync("scraper.json", "utf-8");
	return JSON.parse(config);
}

while (true) {
	const { jackettUrl, jackettApiKey, tmdbApiKey, language, scrapeEvery } = getConfig();
	await cachePopular(jackettUrl, jackettApiKey, tmdbApiKey, language);
	await new Promise(resolve => setTimeout(resolve, scrapeEvery));
}
