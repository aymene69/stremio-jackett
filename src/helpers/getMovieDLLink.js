import { selectBiggestFileSeasonDL } from "./selectBiggestFileSeasonDL";

function wait(ms) {
	new Promise(resolve => setTimeout(resolve, ms));
}

async function addMagnetToDL(magnetLink, debridApi) {
	const apiUrl = "https://debrid-link.com/api/v2/seedbox/add";
	const headers = {
		Authorization: `Bearer ${debridApi}`,
		"Content-Type": "application/json"
	};
	const body = JSON.stringify({
		url: magnetLink,
		async: true
	});

	const response = await fetch(apiUrl, { method: "POST", headers, body });
	const responseJson = await response.json();

	if( !responseJson.value ){
		throw new Error("Magnet not added on DL");
	}

	return responseJson.value;
}

export async function getMovieDLLink(torrentLink, debridApi, seasonEpisode) {
	try {
		let torrent = await addMagnetToDL(torrentLink, debridApi);
		let tries = 0;
		console.log(`Magnet added to DL. ID: ${torrent.id}, downloadPercent: ${torrent.downloadPercent}`);

		while (torrent.downloadPercent < 100 && tries < 10) {

			await wait(5000);

			tries++;
			const apiUrl = `https://debrid-link.com/api/v2/seedbox/list?id=${torrent.id}`;
			const headers = {
				Authorization: `Bearer ${debridApi}`
			};

			const response = await fetch(apiUrl, { headers });
			const responseJson = await response.json();
			torrent = responseJson.value[0];

		}

		let file;
		const torrentFiles = torrent.files.sort((a, b) => b.size - a.size);
		if (seasonEpisode) {
			console.log("Selecting biggest file for season/episode...");
			file = selectBiggestFileSeasonDL(torrentFiles, seasonEpisode);
			console.log("Biggest file selected.");
		} else {
			file = torrentFiles[0];
			console.log("Selecting biggest file...");
		}
		const mediaLink = file.downloadUrl;

		return mediaLink;
	}catch(err){
		console.log(err);
		return null;
	}
}
