import xml2js from "xml2js";

export default async function processXML(xml) {
	return new Promise((resolve, reject) => {
		xml2js.parseString(
			xml,
			{
				explicitArray: false,
				ignoreAttrs: false,
			},
			(err, result) => {
				if (err) {
					reject(err);
					return;
				}

				const items = result.rss.channel.item;

				if (!items) {
					resolve([]);
					return;
				}

				const extractedDataArray = Array.isArray(items)
					? items.map(item => ({
							indexer: item.jackettindexer,
							title: item.title,
							size: item.size,
							link: item.link,
							seeders: item["torznab:attr"]
								? item["torznab:attr"].find(attr => attr.$.name === "seeders")?.$.value
								: undefined,
						}))
					: [
							{
								indexer: items.jackettindexer,
								title: items.title,
								size: items.size,
								link: items.link,
								seeders: items["torznab:attr"]
									? items["torznab:attr"].find(attr => attr.$.name === "seeders")?.$.value
									: undefined,
							},
						];

				// Trier par ordre décroissant du nombre de seeders
				const sortedData = extractedDataArray.sort((a, b) => (b.seeders || 0) - (a.seeders || 0));

				resolve(sortedData);
			},
		);
	});
}
