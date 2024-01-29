export async function getAvailabilityPM(magnet, debridApi) {
	const url = `https://www.premiumize.me/api/cache/check?items[]=${magnet}&apikey=${debridApi}`;
	const response = await fetch(url);
	/** @type {any} */
	const json = await response.json();
	if (json.status !== "success") {
		throw "Error getting availability";
	}
	const instant = json.response[0];
	if (instant === true) {
		return true;
	}
	return false;
}
