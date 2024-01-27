import jackettSearch from "./utils/jackettSearch.js";


export default async function fetchResults(debridApi, jackettHost, jackettApiKey, addonType, maxResults, searchQuery, id, prioQuality) {
	let results = await jackettSearch(debridApi, jackettHost, jackettApiKey, addonType, maxResults, searchQuery, id, prioQuality);
	if (results.length === 0) {
		results = await jackettSearch(debridApi, jackettHost, jackettApiKey, addonType, 1, searchQuery, prioQuality);
		if (results.length === 0) {
			results = [{ name: "Jackett", title: "No results found", url: "#" }]
		}
	}
	
	return results;
}