export function selectBiggestFileSeason(files, se) {
	return files.find(file => se && file.path.includes(se))?.id || null;
}
