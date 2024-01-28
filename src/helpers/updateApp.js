import { exec } from "child_process";
import fetch from "node-fetch";
import os from "os";
import { version as localVersion } from "../../package.json";

async function getAppVersionGithub() {
	/** @type {GitHub.Release} */
	// @ts-ignore
	const latestRelease = await (
		await fetch("https://api.github.com/repos/aymene69/stremio-jackett/releases/latest")
	).json();

	const appVersion = latestRelease.tag_name;

	return appVersion.replace("v", "");
}

export async function updateApp() {
	const latestVersion = await getAppVersionGithub();

	if (localVersion === latestVersion) {
		return;
	}

	console.log("A new update is available!");
	console.log("Local version:", localVersion, "GitHub version:", latestVersion);
	console.log("Updating app...");

	let updateCmd = "git clone https://github.com/aymene69/stremio-jackett temp";
	if (os.platform() === "win32") {
		updateCmd += " & xcopy temp\\* .\\ /E /I /Q & rmdir /S /Q temp & ";
	} else {
		updateCmd += " && sudo rsync -a temp/ ./ && sudo rm -r temp && ";
	}
	updateCmd += "npm install";

	exec(updateCmd);

	console.log("App updated.");
}
