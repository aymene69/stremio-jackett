export function selectBiggestFileSeasonDL(files, se) {
	return files.find(file => file.name.includes(se));
}