import fs from 'fs/promises';
import fetch from 'node-fetch';
import { exec } from 'child_process';
import os from 'os';

async function getAppVersionLocal() {
    const packageJsonPath = './package.json';
    const packageJsonContent = await fs.readFile(packageJsonPath, 'utf-8');
    const packageJson = JSON.parse(packageJsonContent);
    const appVersion = packageJson.version;
    return appVersion;
}

async function getAppVersionGithub() {
    const githubJson = await fetch('https://api.github.com/repos/aymene69/stremio-jackett/releases/latest');
    const githubJsonContent = await githubJson.json();
    // @ts-ignore
    const appVersion = githubJsonContent.tag_name;
    return appVersion.replace('v', '');
}

export async function updateApp() {
    const appVersionLocal = await getAppVersionLocal();
    const appVersionGithub = await getAppVersionGithub();
    if (appVersionLocal !== appVersionGithub) {
        console.log('A new update is available!');
        console.log('Local version:', appVersionLocal, 'Github version:', appVersionGithub);
        console.log('Updating app...');
        if (os.platform() === 'win32') {
            const updateCmd = "git clone https://github.com/aymene69/stremio-jackett temp & xcopy temp\\* .\\ /E /I /Q & rmdir /S /Q temp & npm install";
            await exec(updateCmd);
        }
        else {
            const updateCmd = "git clone https://github.com/aymene69/stremio-jackett temp && sudo rsync -a temp/ ./ && sudo rm -r temp && npm install";
            await exec(updateCmd);
        }
        console.log('App updated.');
    }
    else {
        console.log('App is up to date.');
    }
}