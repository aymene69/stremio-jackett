// /path/filename.js

/**
 * Detects the language of a torrent from its name and returns the corresponding emoji.
 * This version supports English, French, and multi-language torrents.
 * 
 * @param {string} torrentName - Name of the torrent.
 * @return {string} - Emoji representing the detected language.
 */
export function detectLanguageEmoji(torrentName) {
    // Check for 'multi' language first
    if (/\bMULTI\b/i.test(torrentName)) {
        return '🌐'; // Emoji for multi-language
    }

    // Extended regex patterns for various language conventions
    const languagePatterns = {
        'en': /(\bEN\b|\bENGLISH\b|\bENG\b|[\[\(]\s*EN\s*[\]\)])|((720|1080)[pi].*EN)|(EN.*[xh]\.264)/i,
        'fr': /(\bFR\b|\bFRENCH\b|\bVF\b|\bVFF\b|\bFRA\b|[\[\(]\s*FR\s*[\]\)])|((720|1080)[pi].*FR)|(FR.*[xh]\.264)/i
        // Additional language patterns can be added here
    };

    for (const [emoji, pattern] of Object.entries(languagePatterns)) {
        if (pattern.test(torrentName)) {
            return getLanguageEmoji(emoji);
        }
    }

    return '🏳️'; // Default emoji if no language is detected
}

/**
 * Maps language codes to their corresponding emojis.
 * 
 * @param {string} langCode - The language code (e.g., 'en', 'fr').
 * @return {string} - The corresponding emoji.
 */
function getLanguageEmoji(langCode) {
    const emojiMap = {
        'en': '🇬🇧', // Emoji for English
        'fr': '🇫🇷', // Emoji for French
        // Additional language emoji mappings can be added here
    };

    return emojiMap[langCode] || '🏳️';
}

// Example usage
/*
console.log(detectLanguageEmoji("Game of Thrones S01E01 [EN]")); // Should return 🇬🇧
console.log(detectLanguageEmoji("Le Fabuleux Destin d'Amélie Poulain VF")); // Should return 🇫🇷
console.log(detectLanguageEmoji("Interstellar FRENCH 1080p")); // Should return 🇫🇷
console.log(detectLanguageEmoji("Interstellar MULTi 1080p")); // Should return 🌐
*/
