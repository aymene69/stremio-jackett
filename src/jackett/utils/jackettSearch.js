import { getAvailabilityAD } from "../../helpers/getAvailabilityAD";
import { getAvailabilityPM } from "../../helpers/getAvailabilityPM";
import { getAvailabilityRD } from "../../helpers/getAvailabilityRD";
import { detectLanguageEmoji } from "../../helpers/getLanguage";
import { getMovieADLink } from "../../helpers/getMovieADLink";
import { getMoviePMLink } from "../../helpers/getMoviePMLink";
import { getMovieRDLink } from "../../helpers/getMovieRDLink";
import { detectQuality } from "../../helpers/getQuality";
import { selectBiggestFileSeasonTorrent } from "../../helpers/selectBiggestFileSeasonTorrent";
import { sortByLocale } from "../../helpers/sortByLocale";
import { sortByQuality } from "../../helpers/sortByQuality";
import { sortBySize } from "../../helpers/sortBySize";
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
	sorting,
	searchQuery,
	host,
) {
	try {
		const { episode, name, season, type, year } = searchQuery;
		const isSeries = type === "series";
		const torrentAddon = addonType === "torrent";

		console.log(`Searching on Jackett, will return ${!torrentAddon ? "debrid links" : "torrents"}...`);

		let searchUrl;
		if (isSeries) {
			searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&t=search&cat=5000&q=${encodeURIComponent(name.name)}+S${season}E${episode}`;
		} else {
			searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&t=movie&cat=2000&q=${encodeURIComponent(name)}&year=${year}`;
		}

		console.log(searchUrl.replace(/(apikey=)[^&]+(&t)/, "$1<private>$2"));

		const results = [];
		let items = await getItemsFromUrl(searchUrl);
		for (const [index, item] of items.entries()) {
			console.log(maxResults);
			if (index >= maxResults) {
				break;
			}

			const torrentInfo = await getTorrentInfo(item.link);
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
					const availability = await getAvailabilityRD(torrentInfo.infoHash, debridApi);
					if (!availability) {
						console.log("No RD link found. Skipping...");
						continue;
					}
					if (availability) {
						console.log(
							`${host}/getStream/realdebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/undefined`,
						);
						console.log("Host: ", host);
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/realdebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/undefined`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}
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
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/alldebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/undefined`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}
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
					const availability = await getAvailabilityPM(torrentInfo.infoHash, debridApi);
					if (!availability) {
						console.log("No RD link found. Skipping...");
						continue;
					}
					if (availability) {
						results.push({
							name: "Jackett Debrid",
							title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
							url: `${host}/getStream/premiumize/${debridApi}/${btoa(torrentInfo.magnetLink)}/undefined`,
							quality: detectQuality(item.title),
							size: item.size,
							locale: detectLanguageEmoji(item.title),
						});
					}
				}
			}

			torrentInfo.seeders = item.seeders;
			torrentInfo.title = `${item.title.slice(0, 98)}...\r\n${detectLanguageEmoji(torrentInfo.title)} ${detectQuality(torrentInfo.title)}\r\n👤${item.seeders} 📁${toHumanReadable(item.size)}`;
			if (!isSeries) {
				torrentInfo.fileIdx = undefined;
			}

			if (torrentAddon) results.push(torrentInfo);
			console.log(`Added torrent to results: ${item.title}`);
		}

		if (isSeries && results.length === 0) {
			if (torrentAddon) {
				console.log("No results found with season/episode. Trying without...");
				console.log("Searching on Jackett...");
			}

			searchUrl = `${jackettHost}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApiKey}&cat=5000&q=${encodeURIComponent(
				searchQuery.name.name,
			)}+S${searchQuery.season}`;

			console.log(searchUrl.replace(/(apikey=)[^&]+(&t)/, "$1<private>$2"));
			items = await getItemsFromUrl(searchUrl);
			for (const item of items) {
				const torrentInfo = await getTorrentInfo(item.link);

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
						const availability = await getAvailabilityRD(torrentInfo.infoHash, debridApi);
						if (!availability) {
							console.log("No RD link found. Skipping...");
							continue;
						}
						if (availability) {
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
								url: `${host}/getStream/realdebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/S${searchQuery.season}E${searchQuery.episode}`,
								quality: detectQuality(item.title),
								size: item.size,
								locale: detectLanguageEmoji(item.title),
							});
						}
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
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
								url: `${host}/getStream/alldebrid/${debridApi}/${btoa(torrentInfo.magnetLink)}/S${searchQuery.season}E${searchQuery.episode}`,
								quality: detectQuality(item.title),
								size: item.size,
								locale: detectLanguageEmoji(item.title),
							});
						}
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
						const availability = await getAvailabilityPM(torrentInfo.infoHash, debridApi);
						if (!availability) {
							console.log("No RD link found. Skipping...");
							continue;
						}
						if (availability) {
							results.push({
								name: "Jackett Debrid",
								title: `${item.title}\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`,
								url: `${host}/getStream/premiumize/${debridApi}/${btoa(torrentInfo.magnetLink)}/S${searchQuery.season}E${searchQuery.episode}`,
								quality: detectQuality(item.title),
								size: item.size,
								locale: detectLanguageEmoji(item.title),
							});
						}
					}
				}

				console.log("Getting torrent info...");
				console.log(`Torrent info: ${item.title}`);

				torrentInfo.seeders = item.seeders;
				torrentInfo.title = `${item.title.slice(0, 98)}...\r\n${detectLanguageEmoji(item.title)} ${detectQuality(item.title)}\r\n📁${toHumanReadable(item.size)}`;

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
		console.log(detectLanguageEmoji(searchQuery.locale));
		if (sorting.sorting === "quality") {
			if (searchQuery.locale === "undefined") {
				console.log("Sorting by quality");
				return sortByQuality(results);
			}
			let sorted = sortByQuality(results);
			sorted = sorted.sort((a, b) => sortByLocale(a, b, detectLanguageEmoji(searchQuery.locale)));
			console.log("Sorting by locale + quality...");
			return sorted;
		}
		if (sorting.sorting === "size") {
			if (searchQuery.locale === "undefined") {
				console.log(`Sorting by size ${sorting.ascOrDesc}`);
				return sortBySize(results, sorting.ascOrDesc);
			}
			let sorted = sortBySize(results, sorting.ascOrDesc);
			sorted = sorted.sort((a, b) => sortByLocale(a, b, detectLanguageEmoji(searchQuery.locale)));
			console.log("Sorting by locale + size...");
			return sorted;
		}
		if (searchQuery.locale === "undefined") {
			return results;
		}
		console.log("Sorting by locale...");
		return results.sort((a, b) => sortByLocale(a, b, detectLanguageEmoji(searchQuery.locale)));
	} catch (e) {
		console.error(e);

		return [{ name: "Jackett", title: "No results found", url: "#" }];
	}
}
