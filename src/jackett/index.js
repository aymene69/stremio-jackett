import jackettSearch from "./utils/jackettSearch.js";


export default async function fetchResults(debridApi, jackettHost, jackettApiKey, addonType, maxResults, searchQuery) {
	let results = await jackettSearch(debridApi, jackettHost, jackettApiKey, addonType, maxResults, searchQuery);
	if (results.length === 0) {
		results = await jackettSearch(debridApi, jackettHost, jackettApiKey, addonType, 1, searchQuery);
		if (results.length === 0) {
			results = [{ name: "Jackett", title: "No results found", url: "#" }]
		}
	}
	
	return results;
}