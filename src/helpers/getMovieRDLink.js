import { selectBiggestFileSeason } from "./selectBiggestFileSeason.js";

function wait(ms) {
	new Promise(resolve => setTimeout(resolve, ms));
}

async function addMagnetToRD(magnetLink, debridApi) {
	const apiUrl = "https://api.real-debrid.com/rest/1.0/torrents/addMagnet";
	const headers = {
		Authorization: `Bearer ${debridApi}`,
	};
	const body = new URLSearchParams();
	body.append("magnet", magnetLink);

	const response = await fetch(apiUrl, { method: "POST", headers, body });
	const responseJson = await response.json();
	return responseJson.id;
}

async function setMovieFileRD(torrentId, debridApi, seasonEpisode) {
	let responseJson;
	while (true) {
		const apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
		const headers = {
			Authorization: `Bearer ${debridApi}`,
		};

		const response = await fetch(apiUrl, { method: "GET", headers });
		responseJson = await response.json();
		const file_status = responseJson.status;
		if (file_status !== "magnet_conversion") {
			break;
		}
		await wait(5000);
	}
	const torrentFiles = responseJson.files;
	let maxIndex;
	if (seasonEpisode) {
		console.log("Selecting biggest file for season/episode...");
		maxIndex = selectBiggestFileSeason(torrentFiles, seasonEpisode);
		console.log("Biggest file selected.");
	} else {
		maxIndex = torrentFiles.reduce((maxIndex, file, currentIndex, array) => {
			const currentBytes = file.bytes || 0;
			const maxBytes = array[maxIndex] ? array[maxIndex].bytes || 0 : 0;

			return currentBytes > maxBytes ? currentIndex : maxIndex;
		}, 0);
	}
	let torrentFileId;
	if (seasonEpisode) torrentFileId = torrentFiles[maxIndex - 1].id;
	else torrentFileId = torrentFiles[maxIndex].id;
	const apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/selectFiles/${torrentId}`;
	const headers = {
		Authorization: `Bearer ${debridApi}`,
	};
	const body = new URLSearchParams();
	body.append("files", torrentFileId);
	const response = await fetch(apiUrl, { method: "POST", headers, body });
}

export async function getMovieRDLink(torrentLink, debridApi, seasonEpisode) {
	const torrentId = await addMagnetToRD(torrentLink, debridApi);
	console.log(`Magnet added to RD. ID: ${torrentId}`);
	if (seasonEpisode) {
		console.log("Setting episode file for season/episode...");
		await setMovieFileRD(torrentId, debridApi, seasonEpisode);
	} else {
		console.log("Setting movie file...");
		await setMovieFileRD(torrentId, debridApi);
	}
	let responseJson;
	console.log("Getting RD link...");
	while (true) {
		console.log("Waiting for RD link...");
		const apiUrl = `https://api.real-debrid.com/rest/1.0/torrents/info/${torrentId}`;
		const headers = {
			Authorization: `Bearer ${debridApi}`,
		};

		const response = await fetch(apiUrl, { method: "GET", headers });
		responseJson = await response.json();
		const links = responseJson.links;
		if (links.length >= 1) {
			console.log("RD link found.");
			break;
		}
		await wait(5000);
		console.log("RD link isn't ready. Retrying...");
	}

	const downloadLink = responseJson.links[0];
	const apiUrl = "https://api.real-debrid.com/rest/1.0/unrestrict/link";
	const headers = {
		Authorization: `Bearer ${debridApi}`,
	};
	const body = new URLSearchParams();
	body.append("link", downloadLink);
	const response = await fetch(apiUrl, { method: "POST", headers, body });
	responseJson = await response.json();
	const mediaLink = responseJson.download;
	console.log(`RD link: ${mediaLink}`);
	return mediaLink;
}
