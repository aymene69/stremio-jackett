export function selectBiggestFileSeasonPM(files, se) {
	return files.content.find(episode => episode.name.includes(se));
}
