import jackettSearch from "./utils/jackettSearch";

export default async function fetchResults(
	debridApi,
	jackettHost,
	jackettApiKey,
	addonType,
	maxResults,
	sorting,
	searchQuery,
) {
	let results = await jackettSearch(
		debridApi,
		jackettHost,
		jackettApiKey,
		addonType,
		maxResults,
		sorting,
		searchQuery,
	);
	if (results.length === 0) {
		results = await jackettSearch(debridApi, jackettHost, jackettApiKey, addonType, 1, sorting, searchQuery);
		if (results.length === 0) {
			results = [{ name: "Jackett", title: "No results found", url: "#" }];
		}
	}

	return results;
}
