/**
 * by @AndroneDev
 * Detects the language of a torrent from its name and returns the corresponding emoji.
 * This version supports English, French, and multi-language torrents.
 *
 * @param {string} torrentName - Name of the torrent.
 * @return {string} - Emoji representing the detected language.
 */
export function detectQuality(torrentName) {
	const qualityPatterns = {
		"1080p": /1080|Full HD/i,
		"2160p": /4K|(2160|3840)/i,
		"720p": /720|HD/i,
		"480p": /480|SD/i,
		"360p": /360|Low Quality/i,
		// Ajoute d'autres modèles de qualité au besoin
	};

	for (const [quality, pattern] of Object.entries(qualityPatterns)) {
		if (pattern.test(torrentName)) {
			return quality;
		}
	}

	return "Unknown"; // Retourne 'Unknown' si la qualité n'est pas détectée
}
