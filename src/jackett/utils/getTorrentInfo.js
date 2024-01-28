import http from "http";
import https from "https";
import ParseTorrent, { toMagnetURI } from "parse-torrent";

async function fetchTorrentBuffer(torrentLink) {
	const response = await fetch(torrentLink);
	const torrentBuffer = await response.arrayBuffer();
	return Buffer.from(torrentBuffer);
}

async function fetchMagnetLink(torrentLink) {
	return new Promise((resolve, reject) => {
		const protocol = torrentLink.startsWith("https") ? https : http;
		protocol.request(torrentLink, async (res) => {
			const magnetLink = res.headers.location;
			if (magnetLink != undefined && !magnetLink.startsWith("magnet:")) {
				reject();
			} else {
				resolve(magnetLink);
			}
		}).end();
	});
}

export default async function getTorrentInfo(torrentLink) {
	let magnetLink, torrentParsed;

	try {
		if (torrentLink.startsWith("magnet:")) {
			magnetLink = torrentLink;
			torrentParsed = await ParseTorrent(torrentLink);
		} else {
			const torrentBuffer = await fetchTorrentBuffer(torrentLink);
			torrentParsed = await ParseTorrent(torrentBuffer);
			magnetLink = toMagnetURI(torrentParsed);
		}
	} catch {
		try {
			magnetLink = await fetchMagnetLink(torrentLink);
			torrentParsed = await ParseTorrent(magnetLink);
		} catch {
			console.log(`Failed to parse magnet link ${magnetLink}`);
			return null;
		}
	}

	// @ts-ignore
	if (torrentParsed.files == undefined) {
		throw new Error("No files found in torrent");
	}
	const torrentInfo = {
		name: "Jackett",
		infoHash: torrentParsed.infoHash,
		magnetLink,
		seeders: "1",
		fileIdx: 0,
		sources: torrentParsed.announce.map((element) => `tracker:${element}`),
		files: !torrentLink.startsWith("magnet:") &&
			// @ts-ignore
			torrentParsed.files.map(file => ({
				name: file.name,
				length: file.length,
			})),

	};

	return torrentInfo;
}
