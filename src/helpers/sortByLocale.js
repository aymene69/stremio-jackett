import { detectLanguageEmoji } from "./getLanguage.js";

export function sortByLocale(items, locale) {
	const languageEmoji = detectLanguageEmoji(locale);
	const result = [];
	for (const item of items) {
		if (!item.title.includes(languageEmoji) || !item.title.includes("🌐") || !item.title.includes("🏳️")) {
			result.push(item);
		}
	}
	return result;
}
