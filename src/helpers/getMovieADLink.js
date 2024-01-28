import { selectBiggestFileSeasonAD } from "./selectBiggestFileSeasonAD";

function wait(ms) {
	new Promise(resolve => setTimeout(resolve, ms));
}

async function addMagnetToAD(magnetLink, debridApi) {
	const apiUrl = `https://api.alldebrid.com/v4/magnet/upload?agent=jackett&apikey=${debridApi}&magnet=${encodeURI(
		magnetLink,
	)}&method=add_magnet`;

	const response = await fetch(apiUrl, { method: "POST" });
	/** @type {any} */
	const responseJson = await response.json();
	if (responseJson.status === "error" && responseJson.error.code === "AUTH_BLOCKED") {
		return "blocked";
	}
	console.log(responseJson);
	return responseJson.data.magnets[0].id;
}

export async function getMovieADLink(torrentLink, debridApi, seasonEpisode) {
	const torrentId = await addMagnetToAD(torrentLink, debridApi);
	if (torrentId === "blocked") {
		return "blocked";
	}
	console.log(`Magnet added to AD. ID: ${torrentId}`);
	/** @type {any} */
	let responseJson;
	while (true) {
		const apiUrl = `https://api.alldebrid.com/v4/magnet/status?agent=jackett&apikey=${debridApi}&id=${torrentId}`;
		const response = await fetch(apiUrl, { method: "GET" });
		responseJson = await response.json();
		const file_status = responseJson.data.magnets.status;
		if (file_status !== "Ready") {
			await wait(5000);
		} else {
			break;
		}
	}

	let file;
	if (seasonEpisode) {
		const torrentFiles = responseJson.data.magnets.links;
		console.log("Selecting biggest file for season/episode...");
		const maxIndex = selectBiggestFileSeasonAD(torrentFiles, seasonEpisode);
		file = torrentFiles[maxIndex - 1];
		console.log("Biggest file selected.");
	} else {
		const torrentFiles = responseJson.data.magnets.links;
		console.log("Selecting biggest file...");
		file = torrentFiles[0];
	}
	const apiUrl = `https://api.alldebrid.com/v4/link/unlock?agent=jackett&apikey=${debridApi}&link=${file.link}`;
	const response = await fetch(apiUrl, { method: "GET" });
	responseJson = await response.json();
	const mediaLink = responseJson.data.link;

	return mediaLink;
}
