import dotenv from "dotenv";
import fs from "fs";

export function writeToEnv(variable, value) {
	const envPath = ".env";
	if (!fs.existsSync(envPath)) {
		fs.writeFileSync(envPath, "");
	}
	const envContent = fs.readFileSync(envPath, "utf-8");
	const envLines = envContent.split("\n");

	const existingIndex = envLines.findIndex(line => line.startsWith(variable + "="));

	if (existingIndex !== -1) {
		envLines[existingIndex] = `${variable}=${value}`;
	} else {
		envLines.push(`${variable}=${value}`);
	}

	fs.writeFileSync(envPath, envLines.join("\n"));

	dotenv.config();
}
