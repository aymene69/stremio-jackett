import { getAvailabilityAD } from "../../helpers/getAvailabilityAD";
import { getAvailabilityRD } from "../../helpers/getAvailabilityRD";
import { getMovieADLink } from "../../helpers/getMovieADLink";
import { getMovieRDLink } from "../../helpers/getMovieRDLink";
import { selectBiggestFileSeasonTorrent } from "../../helpers/selectBiggestFileSeasonTorrent";
import { toHumanReadable } from "../../helpers/toHumanReadable";
import getTorrentInfo from "./getTorrentInfo";
import processXML from "./processXML";

async function getItemsFromUrl(url) {
	const res = await fetch(url);

	const items = await processXML(await res.text());

	return items;
}

export default async function jackettSearch(
	debridApi,
	jackettHost,
	jackettApiKey,
	addonType,
	maxResults,
	searchQuery,
) {
	try {
		const { episode, name, season, type } = searchQuery;
		const isSeries = type === "series";
		const torrentAddon = addonType === "torrent";

		console.log(`Searching on Jackett, will return ${!torrentAddon ? "debrid links" : "torrents"}...`);

		let searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=${
			isSeries ? 5000 : 2000
		}&q=${encodeURIComponent(name)}${isSeries ? `+S${season}E${episode}` : ""}`;

		console.log(searchUrl.replace(/apikey=.*&/g, "apikey=<private>&"));

		const results = [];

		let items = await getItemsFromUrl(searchUrl);
		for (const [index, item] of items.entries()) {
			if (index >= maxResults) {
				break;
			}
			if (index >= 15) {
				break;
			}

			const torrentInfo = await getTorrentInfo(item.link);
			console.log(`Torrent info: ${item.title}`);

			if (!torrentAddon) {
				if (addonType === "realdebrid") {
					if (maxResults === 1) {
						const downloadLink = await getMovieRDLink(torrentInfo.magnetLink, debridApi);
						if (downloadLink === null) {
							results.push({
								name: "Jackett Debrid",
								title: "RD link not found.",
								url: "#",
							});
							break;
						}
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
						if (downloadLink === null) {
							results.push({
								name: "Jackett Debrid",
								title: "RD link not found.",
								url: "#",
							});
						}
						else {
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
								url: downloadLink,
							});
						}
					}
				}
				if (addonType === "alldebrid") {
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
			)}+S${searchQuery.season}`;

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
							if (url === null) {
								results.push({
									name: "Jackett Debrid",
									title: "RD link not found.",
									url: "#",
								});
								break;
							}
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
							if (url === null) {
								continue
							}
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n📁${toHumanReadable(item.size)}`,
								url,
							});
						}
					}
					if (addonType === "alldebrid") {
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
