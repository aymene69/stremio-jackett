export async function getAvailabilityRD(hash, debridApi) {
	let url;
	if (typeof hash !== "string") {
		const hashList = hash.join("/");
		url = `https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/${hashList}`;
	} else {
		url = `https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/${hash}`;
	}
	const headers = {
		Authorization: `Bearer ${debridApi}`,
	};
	const response = await fetch(url, { method: "GET", headers });
	const json = await response.json();
	const { length } = json[hash];
	if (length === 0) {
		return false;
	}
	return true;
}
