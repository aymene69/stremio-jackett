/* eslint-disable prefer-destructuring */

export async function getName(id, type, tmdbApiKey, locale) {
	if (typeof id !== "string") {
		return id;
	}

	if (!tmdbApiKey) {
		const res = await fetch(`https://v3-cinemeta.strem.io/meta/${type}/${id}.json`);
		// @ts-ignore
		const { meta } = await res.json();
		const { name } = meta;
		// @ts-ignore
		const { releaseInfo } = meta;

		return {
			name: name,
			year: releaseInfo,
		};
	}

	const res = await fetch(
		`https://api.themoviedb.org/3/find/${id}?api_key=${tmdbApiKey}&external_source=imdb_id&language=${locale}`,
	);

	if (type === "movie") {
		// @ts-ignore
		const { movie_results } = await res.json();
		const { release_date, title: name } = movie_results[0];

		return {
			name,
			year: release_date.substring(0, 4),
		};
	}

	if (type === "series") {
		// @ts-ignore
		const { tv_results } = await res.json();
		const { name } = tv_results[0];

		return { name };
	}
}
