import { selectBiggestFileSeasonPM } from "./selectBiggestFileSeasonPM";

function wait(ms) {
	new Promise(resolve => setTimeout(resolve, ms));
}

async function addMagnetToPM(magnetLink, debridApi) {
	const apiUrl = `https://www.premiumize.me/api/transfer/create?apikey=${debridApi}`;
	const form = new FormData();
	form.append("src", magnetLink);
	const response = await fetch(apiUrl, { method: "POST", body: form });
	/** @type {any} */
	const responseJson = await response.json();
	return responseJson.id;
}

export async function getMoviePMLink(torrentLink, debridApi, seasonEpisode) {
	const torrentId = await addMagnetToPM(torrentLink, debridApi);
	console.log(`Magnet added to PM. ID: ${torrentId}`);
	/** @type {any} */
	let responseJson, fileId;
	if (seasonEpisode) {
		while (true) {
			const apiUrl = `https://www.premiumize.me/api/transfer/list?apikey=${debridApi}`;
			const response = await fetch(apiUrl, { method: "GET" });
			responseJson = await response.json();
			const file_status = responseJson.transfers.find(item => item.id === torrentId).status;
			fileId = responseJson.transfers.find(item => item.id === torrentId).folder_id;
			if (file_status !== "finished") {
				await wait(5000);
			} else {
				break;
			}
		}
		const apiUrl = `https://www.premiumize.me/api/folder/list?id=${fileId}&apikey=${debridApi}`;
		const response = await fetch(apiUrl, { method: "GET" });
		responseJson = await response.json();

		const mediaLink = selectBiggestFileSeasonPM(responseJson, seasonEpisode).link;
		const apiClear = `https://www.premiumize.me/api/transfer/clearfinished?apikey=${debridApi}`;
		await fetch(apiClear, { method: "POST" });
		console.log("Finished.");
		return mediaLink;
	}
	while (true) {
		const apiUrl = `https://www.premiumize.me/api/transfer/list?apikey=${debridApi}`;
		const response = await fetch(apiUrl, { method: "GET" });
		responseJson = await response.json();
		const file_status = responseJson.transfers.find(item => item.id === torrentId).status;
		fileId = responseJson.transfers.find(item => item.id === torrentId).file_id;
		if (file_status !== "finished") {
			await wait(5000);
		} else {
			break;
		}
	}
	const apiUrl = `https://www.premiumize.me/api/item/details?id=${fileId}&apikey=${debridApi}`;
	const response = await fetch(apiUrl, { method: "GET" });
	responseJson = await response.json();
	const mediaLink = responseJson.link;
	const apiClear = `https://www.premiumize.me/api/transfer/clearfinished?apikey=${debridApi}`;
	await fetch(apiClear, { method: "POST" });
	console.log("Finished.");
	return mediaLink;
}
