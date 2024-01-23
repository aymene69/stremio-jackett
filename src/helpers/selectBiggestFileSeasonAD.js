export function selectBiggestFileSeasonAD(files, se) {
	return files.findIndex(file => file.filename.includes(se)) + 1 || null;
}
