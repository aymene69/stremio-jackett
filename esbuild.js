import { build } from "esbuild";
import { readFileSync, rmSync } from "fs";
import { dirname } from "path";
import { pathToFileURL } from "url";
import packageJson from "./package.json" with { type: "json" };

const { devDependencies } = packageJson;

const start = Date.now();

try {
	const outdir = "dist";

	rmSync(outdir, { recursive: true, force: true });

	build({
		bundle: true,
		entryPoints: ["./src/index.js", "./src/**/*.css", "./src/**/*.html"],
		external: [...(devDependencies && Object.keys(devDependencies))],
		keepNames: true,
		loader: {
			".css": "copy",
			".html": "copy",
		},
		minify: true,
		outbase: "./src",
		outdir,
		outExtension: {
			".js": ".cjs",
		},
		platform: "node",
		plugins: [
			{
				name: "populate-import-meta",
				setup: ({ onLoad }) => {
					onLoad({ filter: new RegExp(`${import.meta.dirname}/src/.*\.(js|ts)$`) }, args => {
						console.log(args.path);
						const contents = readFileSync(args.path, "utf8");

						const transformedContents = contents
							.replace(/import\.meta\.filename/g, JSON.stringify(pathToFileURL(args.path)))
							.replace(/import\.meta\.dirname/g, JSON.stringify(dirname(args.path)));

						return { contents: transformedContents, loader: "default" };
					});
				},
			},
		],
	}).then(() => {
		// biome-ignore lint/style/useTemplate: <explanation>
		console.log("⚡ " + "\x1b[32m" + `Done in ${Date.now() - start}ms`);
	});
} catch (e) {
	console.log(e);
	process.exit(1);
}
