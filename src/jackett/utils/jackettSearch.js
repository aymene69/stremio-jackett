import { detectLanguageEmoji } from "../../helpers/getLanguage";
import { getMovieADLink } from "../../helpers/getMovieADLink";
import { getMoviePMLink } from "../../helpers/getMoviePMLink";
import { getMovieRDLink } from "../../helpers/getMovieRDLink";
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
	sorting,
	searchQuery,
	host,
	qualityExclusion,
) {
	try {
		const { episode, name, season, type, year } = searchQuery;
		const isSeries = type === "series";
		const torrentAddon = addonType === "torrent";

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
		if (sorting.sorting === "quality") {
			if (searchQuery.locale === "undefined") {
				console.log("Sorting by quality");
				items.items = sortByQuality(items.items);
			}
			let sorted = sortByQuality(items.items);
			sorted = sorted.sort((a, b) => sortByLocale(a, b, detectLanguageEmoji(searchQuery.locale)));
			console.log("Sorting by locale + quality...");
			items.items = sorted;
		}
		if (sorting.sorting === "size") {
			if (searchQuery.locale === "undefined") {
				console.log(`Sorting by size ${sorting.ascOrDesc}`);
				items.items = sortBySize(items.items, sorting.ascOrDesc);
			}
			let sorted = sortBySize(items.items, sorting.ascOrDesc);
			sorted = sorted.sort((a, b) => sortByLocale(a, b, detectLanguageEmoji(searchQuery.locale)));
			console.log("Sorting by locale + size...");
			items.items = sorted;
		}
		items.items = items.items.sort((a, b) => sortByLocale(a, b, detectLanguageEmoji(searchQuery.locale)));
		const results = [];
		if (!torrentAddon && items.cached === false)
			items.items = await threadedAvailability(items.items, debridApi, addonType, maxResults);
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
					if (maxResults === "1") {
						const downloadLink = await getMovieRDLink(torrentInfo.magnetLink, debridApi);
						if (downloadLink === null) {
							return [{ name: "Jackett", title: "No results found", url: "#" }];
						}
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} - ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: downloadLink,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
						break;
					}
					console.log("Getting RD link...");
					results.push({
						name: "Jackett Debrid",
						title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
						url: `${host}/getStream/realdebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/undefined`,
						quality: detectQuality(item.title),
						size: item.size,
						locale: detectLanguageEmoji(item.title),
					});
				}

				if (addonType === "alldebrid") {
					if (maxResults === "1") {
						const downloadLink = await getMovieADLink(torrentInfo.magnetLink, debridApi);
						if (downloadLink === "blocked") {
							console.log("Error: AllDebrid blocked for this IP. Please check your email.");
							return [{ name: "AllDebrid blocked", title: "Please check your email", url: "#" }];
						}
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: downloadLink,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
						break;
					}
					console.log("Getting AD link...");
					results.push({
						name: "Jackett Debrid",
						title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
						url: `${host}/getStream/alldebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/undefined`,
						quality: detectQuality(item.title),
						size: item.size,
						locale: detectLanguageEmoji(item.title),
					});
				}

				if (addonType === "premiumize") {
					if (maxResults === "1") {
						const downloadLink = await getMoviePMLink(torrentInfo.magnetLink, debridApi);
						if (downloadLink === null) {
							return [{ name: "Jackett", title: "No results found", url: "#" }];
						}
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: downloadLink,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
						break;
					}
					console.log("Getting RD link...");
					results.push({
						name: "Jackett Debrid",
						title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
						url: `${host}/getStream/premiumize/${debridApi}/${btoa(torrentInfo.magnetLink)}/undefined`,
						quality: detectQuality(item.title),
						size: item.size,
						locale: detectLanguageEmoji(item.title),
					});
				}
			} else {
				torrentInfo.seeders = item.seeders;
				torrentInfo.title = `${item.title.slice(0, 98)}...\r\n${detectLanguageEmoji(torrentInfo.title)} ${detectQuality(torrentInfo.title)}\r\n👤${item.seeders} 📁${toHumanReadable(item.size)}`;
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
			if (!torrentAddon && items.cached === false)
				items.items = await threadedAvailability(items.items, debridApi, addonType, maxResults);
			for (let index = 0; index < maxResults; index++) {
				const item = items.items[index];
				if (!item) {
					break;
				}
				let torrentInfo;
				if (items.cached) {
					torrentInfo = JSON.parse(item.torrentInfo);
				}
				console.log(`Torrent info: ${item.title}`);
				torrentInfo = item.torrentInfo;
				if (!torrentAddon) {
					if (addonType === "realdebrid") {
						if (maxResults === "1") {
							const url = await getMovieRDLink(
								torrentInfo.magnetLink,
								debridApi,
								`S${searchQuery.season}E${searchQuery.episode}`,
							);
							if (url === null) {
								return [{ name: "Jackett", title: "No results found", url: "#" }];
							}
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
								url,
								quality: detectQuality(item.title),
								size: item.size,
								locale: detectLanguageEmoji(item.title),
							});
							break;
						}
						console.log("Getting RD link...");
						console.log(
							`${host}/getStream/realdebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/S${searchQuery.season}E${searchQuery.episode}`,
						);
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/realdebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/S${searchQuery.season}E${searchQuery.episode}`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}

					if (addonType === "alldebrid") {
						if (maxResults === "1") {
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
								title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
								url,
								quality: detectQuality(item.title),
								size: item.size,
								locale: detectLanguageEmoji(item.title),
							});
							break;
						}
						console.log("Getting AD link...");
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/alldebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/S${searchQuery.season}E${searchQuery.episode}`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}

					if (addonType === "premiumize") {
						if (maxResults === "1") {
							const url = await getMoviePMLink(
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
								title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
								url,
								quality: detectQuality(item.title),
								size: item.size,
								locale: detectLanguageEmoji(item.title),
							});
							break;
						}
						console.log("Getting RD link...");
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/premiumize/${debridApi}/${btoa(torrentInfo.magnetLink)}/S${searchQuery.season}E${searchQuery.episode}`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}
				} else {
					console.log("Getting torrent info...");
					console.log(`Torrent info: ${item.title}`);

					torrentInfo.seeders = item.seeders;
					torrentInfo.title = `${item.title.slice(0, 98)}...\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`;

					console.log("Determining episode file...");
					torrentInfo.fileIdx = parseInt(
						selectBiggestFileSeasonTorrent(
							torrentInfo.files,
							`S${searchQuery.season}E${searchQuery.episode}`,
						),
						10,
					);
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
