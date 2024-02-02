import sqlite3 from "sqlite3";

export default function insertTable(category, data) {
	console.log(data);
	const db = new sqlite3.Database("cache.db");
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
				console.error(err.message);
			} else {
				db.run(
					`
					INSERT INTO ${category} (link, title, size, seeders, torrentInfo, dateAdded)
					VALUES (?, ?, ?, ?, ?, ?)
				`,
					[data.link, data.title, data.size, data.seeders, JSON.stringify(data.torrentInfo), data.dateAdded],
				);
			}
		},
	);
}
