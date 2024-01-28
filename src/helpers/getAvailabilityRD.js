export async function getAvailabilityRD(hash, debridApi) {
	const url = `https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/${hash}`;
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
