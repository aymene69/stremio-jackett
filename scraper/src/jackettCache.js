import PQueue from "p-queue";
import getTorrentInfo from "./getTorrentInfo.js";
import insertTable from "./insertTable.js";
import processXML from "./processXML.js";

const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

const queue = new PQueue({ concurrency: 5 }); // Limite le nombre de workers à 5

async function getItemsFromUrl(url) {
	const res = await fetch(url);

	const items = await processXML(await res.text());

	return items;
}

export async function jackettCache(jackettUrl, jackettApi, list, category) {
	if (list.length !== 0) {
		await Promise.all(
			list.map(async elem => {
				await queue.add(async () => {
					let interval = 0;
					let searchUrl;
					if (category === "movie") {
						searchUrl = `${jackettUrl}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApi}&t=movie&cat=2000&q=${encodeURIComponent(elem.title)}&year=${elem.year}`;
					} else if (category === "series") {
						searchUrl = `${jackettUrl}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApi}&t=search&cat=5000&q=${encodeURIComponent(elem.title)}`;
					}
					console.log(searchUrl);
					const items = await getItemsFromUrl(searchUrl);
					let increment = 0;
					for (const item of items) {
						if (increment === 20) break;
						let torrentInfo;
						console.log("Fetching torrent info for " + item.title);
						torrentInfo = await getTorrentInfo(item.link);
						console.log(interval);
						if (torrentInfo === undefined) {
							console.log("Error fetching torrent info for " + item.title);
							console.log("Retrying...");
							while (true) {
								wait(5000);
								console.log("Test interval: " + interval);
								const itemsRetry = await getItemsFromUrl(searchUrl);
								torrentInfo = await getTorrentInfo(itemsRetry[interval].link);
								if (torrentInfo !== undefined) {
									console.log("Success");
									break;
								}
							}
						}
						insertTable(category, {
							title: item.title,
							size: item.size,
							link: item.link,
							seeders: item.seeders,
							torrentInfo: torrentInfo,
							dateAdded: Date.now(),
						});
						console.log(`Cached item: ${item.title}`);
						increment += 1;
						interval += 1;
					}
				});
			}),
		);
	}
}
