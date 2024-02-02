import { jackettCache } from "./jackettCache.js";

async function getPopularMovies(tmdbApiKey, language) {
	const results = [];
	for (let i = 1; i <= 1; i++) {
		let url = `https://api.themoviedb.org/3/movie/popular?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		let response = await fetch(url);
		let data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			let year;
			try {
				year = elem.release_date.substring(0, 4);
			} catch (error) {
				year = "undefined";
			}
			const isDuplicate = results.some(item => item.title === elem.title && item.year === year);
			if (!isDuplicate) results.push({ title: elem.title, year: year });
		}
		url = `https://api.themoviedb.org/3/movie/now_playing?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		response = await fetch(url);
		data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			let year;
			try {
				year = elem.release_date.substring(0, 4);
			} catch (error) {
				year = "undefined";
			}
			const isDuplicate = results.some(item => item.title === elem.title && item.year === year);
			if (!isDuplicate) results.push({ title: elem.title, year: year });
		}
		url = `https://api.themoviedb.org/3/movie/top_rated?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		response = await fetch(url);
		data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			let year;
			try {
				year = elem.release_date.substring(0, 4);
			} catch (error) {
				year = "undefined";
			}
			const isDuplicate = results.some(item => item.title === elem.title && item.year === year);
			if (!isDuplicate) results.push({ title: elem.title, year: year });
		}
	}
	return results;
}

async function getPopularTV(tmdbApiKey, language) {
	const results = [];
	for (let i = 1; i <= 1; i++) {
		let url = `https://api.themoviedb.org/3/tv/popular?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		let response = await fetch(url);
		let data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			// @ts-ignore
			const isDuplicate = results.some(item => item.name === elem.name);
			if (!isDuplicate) results.push({ title: elem.name });
		}
		url = `https://api.themoviedb.org/3/tv/on_the_air?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		response = await fetch(url);
		data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			// @ts-ignore
			const isDuplicate = results.some(item => item.name === elem.name);
			if (!isDuplicate) results.push({ title: elem.name });
		}
		url = `https://api.themoviedb.org/3/tv/top_rated?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		response = await fetch(url);
		data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			// @ts-ignore
			const isDuplicate = results.some(item => item.name === elem.name);
			if (!isDuplicate) results.push({ title: elem.name });
		}
		url = `https://api.themoviedb.org/3/tv/airing_today?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		response = await fetch(url);
		data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			// @ts-ignore
			const isDuplicate = results.some(item => item.name === elem.name);
			if (!isDuplicate) results.push({ title: elem.name });
		}
	}
	return results;
}

export async function cachePopular(jackettUrl, jackettApi, tmdbApiKey, language) {
	try {
		const movieResults = await getPopularMovies(tmdbApiKey, language);
		console.log("Got popular movies");
		const tvResults = await getPopularTV(tmdbApiKey, language);
		console.log("Got popular tv");
		await jackettCache(jackettUrl, jackettApi, movieResults, "movie");
		await jackettCache(jackettUrl, jackettApi, tvResults, "series");
	} catch (error) {
		console.error(error.message);
	}
}
