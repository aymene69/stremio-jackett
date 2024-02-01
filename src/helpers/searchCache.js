import sqlite3 from "sqlite3";

export async function searchCache(title, category) {
	const db = new sqlite3.Database("./cache.db");
	const query = `SELECT * FROM ${category} WHERE title LIKE '%${title}%' COLLATE NOCASE`;
	const results = await new Promise((resolve, reject) => {
		db.all(query, (err, rows) => {
			if (err) {
				reject(err);
			}
			resolve(rows);
		});
	});
	db.close();
	return results;
}
