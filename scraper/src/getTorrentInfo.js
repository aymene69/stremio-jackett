import http from "http";
import https from "https";
import ParseTorrent, { toMagnetURI } from "parse-torrent";

export default async function getTorrentInfo(torrentLink) {
	let magnetLink, torrentParsed;

	let isMagnetLink = torrentLink.startsWith("magnet:");
	if (isMagnetLink) {
		magnetLink = torrentLink;
		torrentParsed = await ParseTorrent(torrentLink);
	} else {
		try {
			const response = await fetch(torrentLink);
			const torrentBuffer = await response.arrayBuffer();

			torrentParsed = await ParseTorrent(Buffer.from(torrentBuffer));
			magnetLink = toMagnetURI(torrentParsed);
		} catch {
			isMagnetLink = true;

			await new Promise((resolve, reject) =>
				(torrentLink.startsWith("https") ? https : http)
					.request(torrentLink, async res => {
						magnetLink = res.headers.location;
						try {
							torrentParsed = await ParseTorrent(res.headers.location);
						} catch (error) {
							torrentParsed = undefined;
						}
						resolve();
					})
					.end(),
			);
		}
	}
	if (torrentParsed === undefined) {
		console.error("Error fetching torrent info for " + torrentLink);
		return undefined;
	}
	const torrentInfo = {
		name: "Jackett",
		infoHash: torrentParsed.infoHash,
		magnetLink,
		seeders: "1",
		fileIdx: 0,
		sources: torrentParsed.announce.map(element => `tracker:${element}`),
		// Only `.torrent` outputs a files array
		files:
			!isMagnetLink &&
			// @ts-ignore
			torrentParsed.files.map(file => ({
				name: file.name,
				length: file.length,
			})),
	};

	return torrentInfo;
}
