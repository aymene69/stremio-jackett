import sqlite3 from "sqlite3";
import { jackettCache } from "./jackettCache.js";

async function getPopularMovies(tmdbApiKey, language) {
	const results = [];
	for (let i = 1; i <= 3; i++) {
		let url = `https://api.themoviedb.org/3/movie/popular?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		let response = await fetch(url);
		let data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			const isDuplicate = results.some(
				item => item.title === elem.title && item.year === elem.release_date.substring(0, 4),
			);
			if (!isDuplicate) results.push({ title: elem.title, year: elem.release_date.substring(0, 4) });
		}
		url = `https://api.themoviedb.org/3/movie/now_playing?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		response = await fetch(url);
		data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			const isDuplicate = results.some(
				item => item.title === elem.title && item.year === elem.release_date.substring(0, 4),
			);
			if (!isDuplicate) results.push({ title: elem.title, year: elem.release_date.substring(0, 4) });
		}
		url = `https://api.themoviedb.org/3/movie/top_rated?api_key=${tmdbApiKey}&language=${language}&page=${i}`;
		response = await fetch(url);
		data = await response.json();
		// @ts-ignore
		for (const elem of data.results) {
			const isDuplicate = results.some(
				item => item.title === elem.title && item.year === elem.release_date.substring(0, 4),
			);
			if (!isDuplicate) results.push({ title: elem.title, year: elem.release_date.substring(0, 4) });
		}
	}
	return results;
}

async function getPopularTV(tmdbApiKey, language) {
	const results = [];
	for (let i = 1; i <= 2; i++) {
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

// Fonction asynchrone pour créer une base de données et une table pour les films ou séries
const processDatabase = async (list, category) => {
	return new Promise((resolve, reject) => {
		const db = new sqlite3.Database("cache.db");

		// Crée la table si elle n'existe pas
		db.run(
			`
            CREATE TABLE IF NOT EXISTS ${category} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link TEXT,
                title TEXT,
                size TEXT,
                seeders INTEGER,
                torrentInfo TEXT,
				dateAdded INTEGER
            )
        `,
			err => {
				if (err) {
					reject(err);
				} else {
					console.log(`Table ${category} créée avec succès!`);
					const stmt = db.prepare(
						`INSERT INTO ${category} (link, title, size, seeders, torrentInfo, dateAdded) VALUES (?, ?, ?, ?, ?, ?)`,
					);

					for (const item of list) {
						stmt.run(
							item.link,
							item.title,
							item.size,
							item.seeders,
							JSON.stringify(item.torrentInfo, item.dateAdded),
						);
					}

					stmt.finalize();

					console.log("Données insérées avec succès!");

					resolve("Opérations terminées avec succès!");
				}
				db.close();
			},
		);
	});
};

export async function cachePopular(jackettUrl, jackettApi, tmdbApiKey, language) {
	try {
		const movieResults = await getPopularMovies(tmdbApiKey, language);
		const tvResults = await getPopularTV(tmdbApiKey, language);
		const jackettMovieResults = await jackettCache(jackettUrl, jackettApi, movieResults, "movie");
		const jackettTVResults = await jackettCache(jackettUrl, jackettApi, tvResults, "series");
		(async () => {
			try {
				await processDatabase(jackettMovieResults, "movie");
				await processDatabase(jackettTVResults, "series");
			} catch (error) {
				console.error(error.message);
			}
		})();
	} catch (error) {
		console.error(error.message);
	}
}
