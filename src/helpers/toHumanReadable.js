export function toHumanReadable(bytes) {
	if (Math.abs(bytes) < 1024) {
		return `${bytes} B`;
	}

	const units = ["kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];

	let i = -1;
	do {
		bytes /= 1024;
		i += 1;
	} while (Math.abs(bytes) >= 1024 && i < units.length - 1);

	return `${bytes.toFixed(1)} ${units[i]}`;
}
