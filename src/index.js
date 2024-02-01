import cors from "cors";
import express from "express";
import http from "http";
import { cachePopular } from "./helpers/cacheRun";
import { updateApp } from "./helpers/updateApp";
import routes from "./routes";
import "dotenv/config";

if (process.env.NODE_ENV === "production") {
	setInterval(async () => {
		try {
			await updateApp();
		} catch (error) {
			console.error("An error has occurred :", error);
		}
	}, 60000);
}

setInterval(async () => {
	if (process.env.TMDB_API === undefined) {
		console.error("TMDB_API is not defined");
		return;
	}
	try {
		const executeOnce = async () => {
			await cachePopular(
				process.env.JACKETT_URL,
				process.env.JACKETT_API,
				process.env.TMDB_API,
				process.env.LANGUAGE,
			);
		};
		await executeOnce();
		setInterval(async () => {
			await executeOnce();
		}, 2160000);
	} catch (error) {
		console.error("An error has occurred :", error);
	}
}, 5000);

const app = express();
const port = process.env.PORT || 3000;
export const subpath = process.env.SUBPATH || "";

const server = http.createServer(app);
const serverTimeout = 120000;
server.timeout = serverTimeout;

app.use(cors());

app.use(subpath, routes);

server.listen(port, () => {
	console.log(`Server is running at http://localhost:${port}${subpath || ""}`);
});
