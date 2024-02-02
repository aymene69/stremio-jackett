module.exports = {
	apps: [
		{
			name: "stremio-jackett",
			script: "npm start",
			watch: ["./dist/addon/index.cjs"],
			autorestart: true,
			env: {
				NODE_ENV: "production",
				PORT: 3000,
			},
		},
		{
			name: "stremio-jackett-scraper",
			script: "npm run startscraper",
			watch: ["./dist/scraper/index.cjs", "./config.json"],
			autorestart: true,
		},
	],
};
