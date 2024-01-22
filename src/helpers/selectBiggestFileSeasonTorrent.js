export function selectBiggestFileSeasonTorrent(files, se) {
	const filteredFiles = files.filter(file => {
		return file.name.includes(se);
	});

	if (filteredFiles.length === 0) {
		return null;
	}

	const filesTried = filteredFiles.sort((a, b) => {
		return b.length - a.length;
	});

	const biggestFileId = files.indexOf(filesTried[0]);

	return biggestFileId;
}
