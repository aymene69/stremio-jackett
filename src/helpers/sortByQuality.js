export function sortByQuality(files) {
	const qualityOrder = ["2160p", "1080p", "720p", "480p", "360p"];

	try {
		return files
			.map(file => {
				const quality = getQualityCode(file.title.toUpperCase());
				return { ...file, quality };
			})
			.sort((a, b) => {
				const qualityIndexA = qualityOrder.indexOf(a.quality);
				const qualityIndexB = qualityOrder.indexOf(b.quality);

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

function getQualityCode(title) {
	if (title.includes("2160")) return "2160p";
	if (title.includes("1080")) return "1080p";
	if (title.includes("720")) return "720p";
	if (title.includes("480")) return "480p";
	if (title.includes("360")) return "360p";

	return title; // Retourne le titre si la qualité n'est pas trouvée
}
