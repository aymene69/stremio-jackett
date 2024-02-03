export async function getAvailabilityDL(magnet, debridApi) {
	const url = `https://debrid-link.com/api/v2/seedbox/cached?url=${encodeURIComponent(magnet)}`;
	const headers = {
		Authorization: `Bearer ${debridApi}`
	};
	const response = await fetch(url, {headers});
	/** @type {any} */
	const json = await response.json();

	return Object.values(json.value).length > 0;
}
