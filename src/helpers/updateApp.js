import decompress from "decompress";
import fs from "fs/promises";
import fetch from "node-fetch";
import { version as localVersion } from "../../package.json";

async function getAppVersionGithub() {
	/** @type {GitHub.Release} */
	// @ts-ignore
	const latestRelease = await (
		await fetch("https://api.github.com/repos/aymene69/stremio-jackett/releases/latest")
	).json();

	const appVersion = latestRelease.tag_name;
	try {
		return appVersion.replace("v", "");
	} catch (e) {
		return localVersion;
	}
}

export async function updateApp() {
	const latestVersion = await getAppVersionGithub();

	if (localVersion === latestVersion) {
		return;
	}

	console.log("A new update is available!");
	console.log("Local version:", localVersion, "GitHub version:", latestVersion);
	console.log("Updating app...");
	const release = "https://api.github.com/repos/aymene69/stremio-jackett/releases/latest";
	const releaseJson = await (await fetch(release)).json();
	const asset = releaseJson.assets[0].browser_download_url;
	const response = await fetch(asset);
	const buffer = await response.buffer();
	await fs.writeFile("update.zip", buffer);
	await decompress("update.zip", "dist");
	await fs.unlink("update.zip");
	console.log("App updated.");
}
