import Database from "better-sqlite3";

export default function insertTable(category, data) {
	const db = new Database("data/cache.db");
	db.exec(
		`
		CREATE TABLE IF NOT EXISTS ${category} (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			link TEXT,
			indexer TEXT,
			title TEXT,
			size TEXT,
			seeders INTEGER,
			torrentInfo TEXT,
			dateAdded INTEGER
		)
		`,
	);

	const insertStatement = db.prepare(
		`
		INSERT INTO ${category} (link, indexer, title, size, seeders, torrentInfo, dateAdded)
		VALUES (?, ?, ?, ?, ?, ?, ?)
		`,
	);

	insertStatement.run(
		data.link,
		data.indexer,
		data.title,
		data.size,
		data.seeders,
		JSON.stringify(data.torrentInfo),
		data.dateAdded,
	);
}
