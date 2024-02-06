import { detectLanguageEmoji } from "../../helpers/getLanguage";
import { detectQuality } from "../../helpers/getQuality";
import { searchCache } from "../../helpers/searchCache";
import { selectBiggestFileSeasonTorrent } from "../../helpers/selectBiggestFileSeasonTorrent";
import { sortByLocale } from "../../helpers/sortByLocale";
import { sortByQuality } from "../../helpers/sortByQuality";
import { sortBySize } from "../../helpers/sortBySize";
import { toHumanReadable } from "../../helpers/toHumanReadable";
import { excludeItem } from "./excludeItems";
import processXML from "./processXML";
import { threadedAvailability } from "./threadedAvailability";
import { threadedTorrent } from "./threadedTorrent";

async function getItemsFromUrl(url) {
	const res = await fetch(url);

	const items = await processXML(await res.text());
	console.log(items[0]);

	return items;
}

export default async function jackettSearch(
	debridApi,
	jackettHost,
	jackettApiKey,
	addonType,
	maxResults,
	sorting,
	searchQuery,
	host,
	qualityExclusion,
	maxSize,
	maxThread,
) {
	try {
		const { episode, name, season, type, year } = searchQuery;
		const isSeries = type === "series";
		const torrentAddon = addonType === "torrent";
		if (maxThread === undefined || maxThread === "" || parseInt(maxThread) === 0) {
			maxThread = 5;
		}
		console.log(`Searching on Jackett, will return ${!torrentAddon ? "debrid links" : "torrents"}...`);
		let items;
		console.log("Searching on cache...");
		if (isSeries) {
			items = await searchCache(`${name.name} S${season}E${episode}`, type);
		} else {
			items = await searchCache(name, type);
		}
		console.log("Cache search done.");
		items = { cached: true, items };
		let searchUrl;
		if (items.items.length === 0) {
			if (isSeries) {
				items = await searchCache(`${name.name} S${season}E${episode}`.replace(" ", "."), type);
			} else {
				items = await searchCache(name.replace(" ", "."), type);
			}
			if (items.length === 0) {
				if (isSeries) {
					searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&t=search&cat=5000&q=${encodeURIComponent(name.name)}+S${season}E${episode}`;
				} else {
					searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&t=movie&cat=2000&q=${encodeURIComponent(name)}&year=${year}`;
				}
				console.log(searchUrl.replace(/(apikey=)[^&]+(&t)/, "$1<private>$2"));
				items.items = await getItemsFromUrl(searchUrl);
				items.cached = false;
			}
		}
		items.items = excludeItem(items.items, qualityExclusion);
		if (searchQuery.locale !== undefined) items.items = sortByLocale(items.items, searchQuery.locale);
		if (sorting.sorting === "quality") {
			console.log("Sorting by quality");
			items.items = sortByQuality(items.items);
		}
		if (sorting.sorting === "size") {
			console.log(`Sorting by size ${sorting.ascOrDesc}`);
			items.items = sortBySize(items.items, sorting.ascOrDesc);
		}
		const results = [];
		if (!torrentAddon && items.cached === false) {
			items.items = await threadedAvailability(items.items, debridApi, addonType, maxResults, maxThread);
		} else {
			items.items = await threadedTorrent(items.items, maxResults, maxThread);
		}
		for (let index = 0; index < maxResults; index++) {
			const item = items.items[index];
			if (!item) {
				break;
			}
			let torrentInfo;
			try {
				torrentInfo = JSON.parse(item.torrentInfo);
			} catch (error) {
				torrentInfo = item.torrentInfo;
			}
			console.log(`Torrent info: ${item.title}`);
			if (!torrentAddon) {
				if (addonType === "realdebrid") {
					let config = {
						service: addonType,
						debridApi: debridApi,
						magnetLink: torrentInfo.magnetLink,
						season: undefined,
					};
					results.push({
						name: `${item.indexer._} Debrid [${detectQuality(item.title)}]`,
						title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
						url: `${host}/getStream/${btoa(JSON.stringify(config))}/${item.title}`,
						quality: detectQuality(item.title),
						size: item.size,
						locale: detectLanguageEmoji(item.title),
					});
				}
				if (addonType === "alldebrid") {
					let config = {
						service: addonType,
						debridApi: debridApi,
						magnetLink: torrentInfo.magnetLink,
						season: undefined,
					};
					results.push({
						name: `${item.indexer._} Debrid [${detectQuality(item.title)}]`,
						title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
						url: `${host}/getStream/${btoa(JSON.stringify(config))}/${item.title}`,
						quality: detectQuality(item.title),
						size: item.size,
						locale: detectLanguageEmoji(item.title),
					});
				}
				if (addonType === "premiumize") {
					let config = {
						service: addonType,
						debridApi: debridApi,
						magnetLink: torrentInfo.magnetLink,
						season: undefined,
					};
					results.push({
						name: `${item.indexer._} Debrid [${detectQuality(item.title)}]`,
						title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
						url: `${host}/getStream/${btoa(JSON.stringify(config))}/${item.title}`,
						quality: detectQuality(item.title),
						size: item.size,
						locale: detectLanguageEmoji(item.title),
					});
				}
			} else {
				torrentInfo.title = `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`;
				if (!isSeries) {
					torrentInfo.fileIdx = undefined;
				}
			}

			if (torrentAddon) results.push(torrentInfo);
			console.log(`Added torrent to results: ${item.title}`);
		}

		if (isSeries && results.length === 0) {
			if (torrentAddon) {
				console.log("No results found with season/episode. Trying without...");
				console.log("Searching on Jackett...");
			}
			items.items = await searchCache(`${searchQuery.name.name} S${searchQuery.season}`, type);
			if (items.items.length === 0) {
				items.items = await searchCache(
					`${searchQuery.name.name} S${searchQuery.season}`.replace(" ", "."),
					type,
				);
				if (items.items.length === 0) {
					searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=5000&q=${encodeURIComponent(
						searchQuery.name.name,
					)}+S${searchQuery.season}`;
					console.log(searchUrl.replace(/(apikey=)[^&]+(&t)/, "$1<private>$2"));
					items.items = await getItemsFromUrl(searchUrl);
				}
			}
			if (!torrentAddon && items.cached === false) {
				items.items = await threadedAvailability(items.items, debridApi, addonType, maxResults, maxThread);
			} else {
				items.items = await threadedTorrent(items.items, maxResults, maxThread);
			}
			for (let index = 0; index < maxResults; index++) {
				const item = items.items[index];
				if (!item) {
					break;
				}
				let torrentInfo;
				try {
					torrentInfo = JSON.parse(item.torrentInfo);
				} catch (error) {
					torrentInfo = item.torrentInfo;
				}
				console.log(`Torrent info: ${item.title}`);
				if (!torrentAddon) {
					if (addonType === "realdebrid") {
						let config = {
							service: addonType,
							debridApi: debridApi,
							magnetLink: torrentInfo.magnetLink,
							season: `S${searchQuery.season}E${searchQuery.episode}`,
						};
						results.push({
							name: `${item.indexer._} Debrid [${detectQuality(item.title)}]`,
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/${btoa(JSON.stringify(config))}/${item.title}`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}

					if (addonType === "alldebrid") {
						let config = {
							service: addonType,
							debridApi: debridApi,
							magnetLink: torrentInfo.magnetLink,
							season: `S${searchQuery.season}E${searchQuery.episode}`,
						};
						results.push({
							name: `${item.indexer._} Debrid [${detectQuality(item.title)}]`,
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/${btoa(JSON.stringify(config))}/${item.title}`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}

					if (addonType === "premiumize") {
						let config = {
							service: addonType,
							debridApi: debridApi,
							magnetLink: torrentInfo.magnetLink,
							season: `S${searchQuery.season}E${searchQuery.episode}`,
						};
						results.push({
							name: `${item.indexer._} Debrid [${detectQuality(item.title)}]`,
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/${btoa(JSON.stringify(config))}/${item.title}`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}
				} else {
					console.log("Getting torrent info...");
					console.log(`Torrent info: ${item.title}`);
					torrentInfo = item.torrentInfo;
					torrentInfo.title = `${item.title.slice(0, 98)}...\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`;

					console.log("Determining episode file...");
					torrentInfo.fileIdx = parseInt(
						selectBiggestFileSeasonTorrent(
							torrentInfo.files,
							`S${searchQuery.season}E${searchQuery.episode}`,
						),
						10,
					);
					console.log(torrentInfo.fileIdx);
					console.log("Episode file determined.");

					results.push(torrentInfo);
					console.log(`Added torrent to results: ${item.title}`);
				}
			}
		}
		return results;
	} catch (e) {
		console.error(e);

		return [{ name: "Jackett", title: "No results found", url: "#" }];
	}
}
