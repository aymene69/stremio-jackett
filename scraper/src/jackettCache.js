import getTorrentInfo from "./getTorrentInfo.js";
import insertTable from "./insertTable.js";
import processXML from "./processXML.js";

async function getItemsFromUrl(url) {
	const res = await fetch(url);

	const items = await processXML(await res.text());

	return items;
}

export async function jackettCache(jackettUrl, jackettApi, list, category) {
	if (category === "movie") {
		if (list.length !== 0) {
			console.log("okkkkkkkkkk");
			for (const elem of list) {
				const searchUrl = `${jackettUrl}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApi}&t=movie&cat=2000&q=${encodeURIComponent(elem.title)}&year=${elem.year}`;
				console.log(searchUrl);
				const items = await getItemsFromUrl(searchUrl);
				let increment = 0;
				for (const item of items) {
					if (increment === 20) break;
					insertTable(category, {
						title: item.title,
						size: item.size,
						link: item.link,
						seeders: item.seeders,
						torrentInfo: await getTorrentInfo(item.link),
						dateAdded: Date.now(),
					});
					console.log(`Cached item: ${item.title}`);
					increment += 1;
				}
			}
		}
	}
	if (category === "series") {
		if (list.length !== 0) {
			for (const elem of list) {
				const searchUrl = `${jackettUrl}/api/v2.0/indexers/all/results/torznab/api?apikey=${jackettApi}&t=search&cat=5000&q=${encodeURIComponent(elem.title)}`;
				const items = await getItemsFromUrl(searchUrl);
				let increment = 0;
				for (const item of items) {
					if (increment === 20) break;
					insertTable(category, {
						title: item.title,
						size: item.size,
						link: item.link,
						seeders: item.seeders,
						torrentInfo: await getTorrentInfo(item.link),
						dateAdded: Date.now(),
					});
					console.log(`Cached item: ${item.title}`);
					increment += 1;
				}
			}
		}
	}
}
