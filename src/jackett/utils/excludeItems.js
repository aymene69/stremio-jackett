export function excludeItem(items, qualityExclusion) {
	if (qualityExclusion.lengh === 0) {
		return items;
	}
	const filteredItems = items.filter(item => {
		if (qualityExclusion.some(keyword => item.title.includes(keyword))) {
			console.log(`Excluding ${item.title}...`);
			return false;
		}
		return true;
	});

	const sortedItems = filteredItems.sort((a, b) => a.title.localeCompare(b.title));

	return sortedItems;
}
