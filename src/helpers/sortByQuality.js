export function sortByQuality(files) {
	const qualityOrder = ["2160p", "1080p", "720p", "480p", "360p"];

	try {
		return files.sort((a, b) => {
			const qualityIndexA = qualityOrder.indexOf(getQualityCode(a.quality.toUpperCase()));
			const qualityIndexB = qualityOrder.indexOf(getQualityCode(b.quality.toUpperCase()));

			if (qualityIndexA !== -1 && qualityIndexB !== -1) {
				return qualityIndexA - qualityIndexB;
			}

			if (qualityIndexA === -1) return 1;
			if (qualityIndexB === -1) return -1;

			return 0;
		});
	} catch {
		return files;
	}
}

function getQualityCode(quality) {
	if (quality.includes("2160")) return "2160p";
	if (quality.includes("1080")) return "1080p";
	if (quality.includes("720")) return "720p";
	if (quality.includes("480")) return "480p";
	if (quality.includes("360")) return "360p";

	return quality;
}
