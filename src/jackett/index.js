import fetch from "node-fetch";
import helper from "../helper.js";
import getTorrentInfo from "./utils/getTorrentInfo.js";
import processXML from "./utils/processXML.js";

async function jackettSearch(debridApi, jackettHost, jackettApiKey, addonType, searchQuery) {
	if (searchQuery.type === "movie") {
		try {
			if (addonType === "torrent") {
				console.log("Will return Torrents.");
				for (let i = 0; i < 5; i++) {
					const item = items[i];
					const torrentInfo = await getTorrentInfo(item.link);
					torrentInfo.seeders = item.seeders;
					torrentInfo.title = `${item.title}\r\n👤${item.seeders} 📁${helper.toHomanReadable(item.size)}`;
					delete torrentInfo.fileIdx;
					results.push(torrentInfo);
					console.log(`Added torrent to results: ${item.title}`);
				}
				if (results.length === 0) {
					console.log("No results found.");
					results.push({ name: "Jackett", title: "No results found", url: "#" });
				}
			} else {
				console.log("Will return Debrid links.");
				for (let i = 0; i < items.length; i++) {
					const item = items[i];
					console.log("Getting torrent info...");
					const torrentInfo = await getTorrentInfo(item.link);
					console.log(`Torrent info: ${item.title}`);
					console.log("Getting RD link...");
					const downloadLink = await helper.getMovieRDLink(torrentInfo.magnetLink, debridApi);
					const torrentReturn = {
						name: "Jackett Debrid",
						title: `${item.title}\r\n📁${helper.toHomanReadable(item.size)}`,
						url: downloadLink,
					};
					results.push(torrentReturn);
					break;
				}
				if (results.length === 0) {
					results.push({ name: "Jackett Debrid", title: "No results found", url: "#" });
				}
			}
			console.log("Returning results.");
			return results;
		} catch (e) {
			const results = [];
			results.push({ name: "Jackett", title: "No results found", url: "#" });
			console.log(`Error: ${e}`);
			return results;
		}
	}
	if (searchQuery.type === "series") {
		try {
			if (addonType === "torrent") {
				if (results.length === 0) {
					console.log("No results found with season/episode. Trying without...");
					console.log("Searching on Jackett...");
					const searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=5000&q=${encodeURIComponent(
						searchQuery.name,
					)}+S${searchQuery.season}`;
					const response = await fetch(searchUrl);
					const responseXml = await response.text();
					const items = await processXML(responseXml);
					const results = [];
					for (let i = 0; i < items.length; i++) {
						const item = items[i];
						console.log("Getting torrent info...");
						const torrentInfo = await getTorrentInfo(item.link);
						console.log(`Torrent info: ${item.title}`);
						torrentInfo.seeders = item.seeders;
						torrentInfo.title = `${item.title}\r\n👤${item.seeders} 📁${helper.toHomanReadable(item.size)}`;
						console.log("Determining episode file...");
						torrentInfo.fileIdx = parseInt(
							helper.selectBiggestFileSeasonTorrent(
								torrentInfo.files,
								`S${searchQuery.season}E${searchQuery.episode}`,
							),
							10,
						);
						console.log("Episode file determined.");
						results.push(torrentInfo);
						console.log(`Added torrent to results: ${item.title}`);
					}
					if (results.length === 0) {
						console.log("No results found.");
						results.push({ name: "Jackett", title: "No results found", url: "#" });
					}
					return results;
				}
				return results;
			}

			if (results.length === 0) {
				const searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=5000&q=${encodeURIComponent(
					searchQuery.name,
				)}+S${searchQuery.season}`;
				const response = await fetch(searchUrl);
				const responseXml = await response.text();
				const items = await processXML(responseXml);
				const results = [];
				for (let i = 0; i < items.length; i++) {
					const item = items[i];
					const torrentInfo = await getTorrentInfo(item.link);
					const downloadLink = await helper.getMovieRDLink(
						torrentInfo.magnetLink,
						debridApi,
						`S${searchQuery.season}E${searchQuery.episode}`,
					);
					const torrentReturn = {
						name: "Jackett Debrid",
						title: `${item.title}\r\n📁${helper.toHomanReadable(item.size)}`,
						url: downloadLink,
					};
					results.push(torrentReturn);
					break;
				}
				if (results.length === 0) {
					results.push({ name: "Jackett Debrid", title: "No results found", url: "#" });
				}
				return results;
			}
			return results;
		} catch (e) {
			console.log(e);
			const results = [];
			results.push({ name: "Jackett", title: "No results found", url: "#" });
			return results;
		}
	}
}

export default {
	jackettSearch,
};
