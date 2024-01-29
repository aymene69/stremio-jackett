export function sortBySize(files, order = "desc") {
	return files.sort((a, b) => {
		const sizeA = parseInt(a.size) || 0;
		const sizeB = parseInt(b.size) || 0;

		if (order === "desc") {
			return sizeB - sizeA;
		}
		if (order === "asc") {
			return sizeA - sizeB;
		}
		throw new Error('Invalid order parameter. Use "asc" or "desc".');
	});
}
