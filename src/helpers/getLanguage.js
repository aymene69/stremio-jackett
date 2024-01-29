/**
 * by @AndroneDev
 * Detects the language of a torrent from its name and returns the corresponding emoji.
 * This version supports English, French, and multi-language torrents.
 *
 * @param {string} torrentName - Name of the torrent.
 * @return {string} - Emoji representing the detected language.
 */
export function detectLanguageEmoji(torrentName) {
	// Check for 'multi' language first

	// Extended regex patterns for various language conventions
	const languagePatterns = {
		en: /(\bEN\b|\bENGLISH\b|\bENG\b|[\[\(]\s*EN\s*[\]\)])|((720|1080)[pi].*EN)|(EN.*[xh]\.264)/i,
		fr: /(\bFR\b|\bFRENCH\b|\bVF\b|\bVFF\b|\bTRUEFRENCH\b|\bVFQ\b|\bFRA\b|[\[\(]\s*FR\s*[\]\)])|((720|1080)[pi].*FR)|(FR.*[xh]\.264)/i,
		es: /(\bES\b|\bSPANISH\b|\bESP\b|[\[\(]\s*ES\s*[\]\)])|((720|1080)[pi].*ES)|(ES.*[xh]\.264)/i,
		pt: /(\bPT\b|\bPORTUGUESE\b|\bPOR\b|[\[\(]\s*PT\s*[\]\)])|((720|1080)[pi].*PT)|(PT.*[xh]\.264)/i,
		de: /(\bDE\b|\bGERMAN\b|\bGER\b|[\[\(]\s*DE\s*[\]\)])|((720|1080)[pi].*DE)|(DE.*[xh]\.264)/i,
		it: /(\bIT\b|\bITALIAN\b|\bITA\b|[\[\(]\s*IT\s*[\]\)])|((720|1080)[pi].*IT)|(IT.*[xh]\.264)/i,
	};

	for (const [emoji, pattern] of Object.entries(languagePatterns)) {
		if (pattern.test(torrentName)) {
			return getLanguageEmoji(emoji);
		}
	}
	if (/\bMULTI\b/i.test(torrentName)) {
		return "🌐"; // Emoji for multi-language
	}

	return "🏳️"; // Default emoji if no language is detected
}

/**
 * Maps language codes to their corresponding emojis.
 *
 * @param {string} langCode - The language code (e.g., 'en', 'fr').
 * @return {string} - The corresponding emoji.
 */
function getLanguageEmoji(langCode) {
	const emojiMap = {
		en: "🇬🇧", // Emoji for English
		fr: "🇫🇷", // Emoji for French
		es: "🇪🇸", // Emoji for Spanish
		pt: "🇵🇹", // Emoji for Portuguese
		de: "🇩🇪", // Emoji for German
		it: "🇮🇹", // Emoji for Italian
	};

	return emojiMap[langCode] || "🏳️";
}
