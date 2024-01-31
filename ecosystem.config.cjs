module.exports = {
	apps: [
		{
			name: "stremio-jackett",
			script: "npm start",
			watch: "./dist/index.cjs",
			autorestart: true,
			env: {
				NODE_ENV: "production",
				PORT: 3000,
			},
		},
	],
};
