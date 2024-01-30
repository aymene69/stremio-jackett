export function sortByLocale(item1, item2, locale) {
	const order = { [locale]: 1, "🌐": 2 };

	const locale1 = item1.locale;
	const locale2 = item2.locale;

	const order1 = order[locale1] || 3;
	const order2 = order[locale2] || 3;

	return order1 - order2;
}
