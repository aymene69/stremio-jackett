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

const qualityOrder = [['4k', '2160p'], ['1080p'], ['720p'], ['480p']];

function getQualityIndex(title) {
    for (let i = 0; i < qualityOrder.length; i++) {
        for (let j = 0; j < qualityOrder[i].length; j++) {
            if (title.includes(qualityOrder[i][j])) {
                return i;
            }
        }
    }
    return qualityOrder.length; // If none of the qualities match
}

function compareItems(a, b, prioQuality) {
    const aContainsPrioQuality = a.title.toLowerCase().includes(prioQuality);
    const bContainsPrioQuality = b.title.toLowerCase().includes(prioQuality);

    // If both or neither title contains the dynamic value, then sort by quality
    if (aContainsPrioQuality === bContainsPrioQuality) {
        const aQualityIndex = getQualityIndex(a.title);
        const bQualityIndex = getQualityIndex(b.title);

        if (aQualityIndex === bQualityIndex) {
            // If quality is the same, then sort by seeders (descending)
            return b.seeders - a.seeders;
        }

        return aQualityIndex - bQualityIndex;
    }

    // If only one title contains the dynamic value, it should come first
    return aContainsPrioQuality ? -1 : 1;
}

function sortItemsIntoPrioritizedQuality(items, prioQuality) {
    return items.sort((a, b) => compareItems(a, b, prioQuality));
}

export default async function jackettSearch(debridApi, jackettHost, jackettApiKey, addonType, maxResults, searchQuery, id, prioQuality) {
	try {
		const { episode, name, season, type } = searchQuery;
		const isSeries = type === "series";
		const torrentAddon = addonType === "torrent";

		console.log("Searching on Jackett...");
		console.log(`Will return ${!torrentAddon ? "Debrid link" : "Torrents"}.`);

		let searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=${
			isSeries ? 5000 : 2000
		}&q=${encodeURIComponent(id)}${isSeries ? `&season=${season}&episode=${episode}` : ""}`;

		console.log(`Searching for ${id}...`);
		const results = [];

		let items = await getItemsFromUrl(searchUrl);
		if (items.length === 0) {
			searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=${
				isSeries ? 5000 : 2000
			}&q=${encodeURIComponent(name)}${isSeries ? `&season=${season}&episode=${episode}` : ""}`;

			items = await getItemsFromUrl(searchUrl);
		}

		if (!torrentAddon) {
			let quality = ["1080p"];
			if (prioQuality === "4k"){
				quality = ["2160p", "4k"];
			}else {
				quality = [prioQuality];
			}

			items = sortItemsIntoPrioritizedQuality(items, quality);
		}
		
		for (const [index, item] of items.entries()) {
			if (index >= maxResults) {
				break;
			}
			if (index >= 15 ) {
				break;
			}

			console.log("Getting torrent info...");
			const torrentInfo = await getTorrentInfo(item.link);
			console.log(`Torrent info: ${item.title}`);

			if (!torrentAddon) {
				if (addonType === "realdebrid") {
					if (maxResults === 1) {
						const downloadLink = await getMovieRDLink(torrentInfo.magnetLink, debridApi);
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
							url: downloadLink,
						});
						break;
					}
					console.log("Getting RD link...");
					const availability = await getAvailabilityRD(torrentInfo.infoHash, debridApi);
					if (!availability) {
						console.log("No RD link found. Skipping...");
						continue;
					}
					if (availability) {
						const downloadLink = await getMovieRDLink(torrentInfo.magnetLink, debridApi);
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
							url: downloadLink,
						});
					}

				} if (addonType === "alldebrid") {
					if (maxResults === 1) {
						const downloadLink = await getMovieADLink(torrentInfo.magnetLink, debridApi);
						if (downloadLink === "blocked") {
							console.log("Error: AllDebrid blocked for this IP. Please check your email.");
							return [{ name: "AllDebrid blocked", title: "Please check your email", url: "#" }];
						}
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
							url: downloadLink,
						});
						break;
					}
					console.log("Getting AD link...");
					const availability = await getAvailabilityAD(torrentInfo.magnetLink, debridApi);
					if (availability === "blocked") {
						console.log("Error: AllDebrid blocked for this IP. Please check your email.");
						return [{ name: "AllDebrid blocked", title: "Please check your email", url: "#" }];
					}
					if (!availability) {
						console.log("No AD link found. Skipping...");
						continue;
					}
					if (availability) {
						const downloadLink = await getMovieADLink(torrentInfo.magnetLink, debridApi);
						if (downloadLink === "blocked") {
							console.log("Error: AllDebrid blocked for this IP. Please check your email.");
							return [{ name: "AllDebrid blocked", title: "Please check your email", url: "#" }];
						}
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
							url: downloadLink,
						});
					}

				}
			}

			torrentInfo.seeders = item.seeders;
			torrentInfo.title = `${item.title}\r\n👤${item.seeders} 📁${toHumanReadable(item.size)}`;
			if (!isSeries) {
				torrentInfo.fileIdx = undefined;
			}

			if (torrentAddon) results.push(torrentInfo);
			console.log(`Added torrent to results: ${item.title}`);
		}

		// Try again without episode
		if (isSeries && results.length === 0) {
			if (torrentAddon) {
				console.log("No results found with season/episode. Trying without...");
				console.log("Searching on Jackett...");
			}

			searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=5000&q=${encodeURIComponent(
				searchQuery.name,
			)}&season${searchQuery.season}`;

			items = await getItemsFromUrl(searchUrl);
			for (const item of items) {
				const torrentInfo = await getTorrentInfo(item.link);

				if (!torrentAddon) {
					if (addonType === "realdebrid") {
						if (maxResults === 1) {
							const url = await getMovieRDLink(
								torrentInfo.magnetLink,
								debridApi,
								`S${searchQuery.season}E${searchQuery.episode}`,
							);
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
								url,
							});
							break;
						}
						console.log("Getting RD link...");
						const availability = await getAvailabilityRD(torrentInfo.infoHash, debridApi);
						if (!availability) {
							console.log("No RD link found. Skipping...");
							continue;
						}
						if (availability) {
							const url = await getMovieRDLink(
								torrentInfo.magnetLink,
								debridApi,
								`S${searchQuery.season}E${searchQuery.episode}`,
							);
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
								url,
							});
						}
            
					} if (addonType === "alldebrid") {
						if (maxResults === 1) {
							console.log("Getting AD link...");
							const url = await getMovieADLink(
								torrentInfo.magnetLink,
								debridApi,
								`S${searchQuery.season}E${searchQuery.episode}`,
							);
							if (url === "blocked") {
								console.log("Error: AllDebrid blocked for this IP. Please check your email.");
								return [{ name: "AllDebrid blocked", title: "Please check your email", url: "#" }];
							}
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
								url,
							});
							break;
						}
						console.log("Getting AD link...");
						const availability = await getAvailabilityAD(torrentInfo.magnetLink, debridApi);
						if (availability === "blocked") {
							console.log("Error: AllDebrid blocked for this IP. Please check your email.");
							return [{ name: "AllDebrid blocked", title: "Please check your email", url: "#" }];
						}
						if (!availability) {
							console.log("No AD link found. Skipping...");
							continue;
						}
						if (availability) {
							const url = await getMovieADLink(
								torrentInfo.magnetLink,
								debridApi,
								`S${searchQuery.season}E${searchQuery.episode}`,
							);
							if (url === "blocked") {
								console.log("Error: AllDebrid blocked for this IP. Please check your email.");
								return [{ name: "AllDebrid blocked", title: "Please check your email", url: "#" }];
							}
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
								url,
							});
						}
					}
				}

				console.log("Getting torrent info...");
				console.log(`Torrent info: ${item.title}`);

				torrentInfo.seeders = item.seeders;
				torrentInfo.title = `${item.title}\r\n👤${item.seeders} 📁${toHumanReadable(item.size)}`;

				console.log("Determining episode file...");
				torrentInfo.fileIdx = parseInt(
					selectBiggestFileSeasonTorrent(torrentInfo.files, `S${searchQuery.season}E${searchQuery.episode}`),
					10,
				);
				console.log("Episode file determined.");

				results.push(torrentInfo);
				console.log(`Added torrent to results: ${item.title}`);
			}
		}

		return results;
	} catch (e) {
		console.error(e);

		return [{ name: "Jackett", title: "No results found", url: "#" }];
	}
}
