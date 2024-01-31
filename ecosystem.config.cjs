module.exports = {
	apps: [
		{
			name: "stremio-jackett",
			script: "npm start",
			cwd: "/app",
			watch: true,
			autorestart: true,
			env: {
				NODE_ENV: "production",
				PORT: 3000,
			},
		},
	],
};
