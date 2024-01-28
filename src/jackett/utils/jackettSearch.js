import { getMovieRDLink } from "../../helpers/getMovieRDLink.js";
import { getMovieADLink } from "../../helpers/getMovieADLink.js";
import { getAvailabilityAD } from "../../helpers/getAvailabilityAD.js";
import { getAvailabilityRD } from "../../helpers/getAvailabilityRD.js";
import { selectBiggestFileSeasonTorrent } from "../../helpers/selectBiggestFileSeasonTorrent.js";
import { toHumanReadable } from "../../helpers/toHumanReadable.js";
import getTorrentInfo from "./getTorrentInfo.js";
import processXML from "./processXML.js";

async function getItemsFromUrl(url) {
	const res = await fetch(url);
	const items = await processXML(await res.text());
	return items;
}

async function searchOnJackett(jackettHost, jackettApiKey, isSeries, name, season, episode) {
	const searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=${isSeries ? 5000 : 2000}&q=${encodeURIComponent(name)}${isSeries ? `+S${season}E${episode}` : ""}`;
	const items = await getItemsFromUrl(searchUrl);
	console.log(`Found ${items.length} results on Jackett.`);
	return items;
}

async function getTorrentsInfo(item) {
	const torrentInfo = await getTorrentInfo(item.link);
	console.log(`Torrent info: ${item.title}`);
	torrentInfo.name = `${item.title}\r\n👤${item.seeders} 📁${toHumanReadable(item.size)}`;
	return torrentInfo;
}

async function getAvailabilityLink(torrentInfo, addonType, debridApi) {
	let isAvailable = false;
	if (addonType === "realdebrid") {
		isAvailable = await getAvailabilityRD(torrentInfo.infoHash, debridApi);
	} else if (addonType === "alldebrid") {
		isAvailable = await getAvailabilityAD(torrentInfo.infoHash, debridApi);
	}
	return isAvailable;
}

function convertToStream(host, item, torrentInfo, addonType, debridApi) {
	let url;
	if (addonType === "torrent") {
		url = torrentInfo.magnetLink;
	} else {
		const base = { type: addonType, debridApi: debridApi, magnet: torrentInfo.magnetLink };
		url = host + "/stream/" + encodeURIComponent(btoa(JSON.stringify(base)));
	}
	return {
		name: "Jackett Debrid",
		title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
		url: url
	};
}

async function jackettSearch(host, debridApi, jackettHost, jackettApiKey, addonType, maxResults, searchQuery) {
	try {
		const { episode, name, season, type } = searchQuery;
		const isSeries = type === "series";
		const torrentAddon = addonType === "torrent";

		console.log(`Searching on Jackett for ${name} ${isSeries ? `S${season}E${episode}` : ""}... ${torrentAddon ? "Torrents" : "Debrid links"} max ${maxResults} results.`);

		console.log(`Will return ${!torrentAddon ? "Debrid link" : "Torrents"}.`);

		const items = await searchOnJackett(jackettHost, jackettApiKey, isSeries, name, season, episode);
		const results = await processItems(host, items, addonType, debridApi, maxResults);

		if (results.length === 0) {
			console.log("No results found.");
			return [{ name: "Jackett", title: "No results found", url: "#" }];
		}
		return results;
	} catch (e) {
		console.error(e);
		return [{ name: "Jackett", title: "No results found", url: "#" }];
	}
}

async function processItems(host, items, addonType, debridApi, maxResults) {
	const results = [];
	for (const [index, item] of items.entries()) {
		try {
			const torrentInfo = await getTorrentsInfo(item);
			const isAvailable = await getAvailabilityLink(torrentInfo, addonType, debridApi);
			if (isAvailable) {
				console.log(`Found ${item.title} in ${addonType}`);
				results.push(convertToStream(host, item, torrentInfo, addonType, debridApi));
			} else {
				console.log(`${item.title} doesn't exist in ${addonType}`);
			}
			if (results.length == maxResults) {
				break;
			}
		} catch (e) {
			console.log(`Failed to get torrent info for ${item.title}`);
			console.error(e);
			continue;
		}
	}
	return results;
}

export default jackettSearch;
