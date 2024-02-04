module.exports = {
	apps: [
		{
			name: "stremio-jackett",
			script: "npm start",
			watch: ["./dist/addon/index.cjs"],
			cwd: "/app",
			autorestart: true,
			env: {
				NODE_ENV: "production",
				PORT: 3000,
			},
		},
		{
			name: "stremio-jackett-scraper",
			script: "npm run startscraper",
			cwd: "/app",
			watch: ["./dist/scraper/index.cjs", "./data/config.json"],
			autorestart: true,
		},
	],
};
