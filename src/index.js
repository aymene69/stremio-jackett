import cors from "cors";
import express from "express";
import http from "http";
import routes from "./routes.js";

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
