import { build } from "esbuild";
import { readFileSync, rmSync } from "fs";
import path from "path";
import url from "url";

const { devDependencies } = JSON.parse(readFileSync("./package.json", "utf8"));

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
						const contents = readFileSync(args.path, "utf8");

						const dirname = JSON.stringify(path.dirname(args.path));
						const filename = JSON.stringify(url.pathToFileURL(args.path));

						const transformedContents = contents
							.replace(
								/import\.meta/g,
								JSON.stringify({
									dirname,
									filename,
								}),
							)
							.replace(/import\.meta\.filename/g, filename)
							.replace(/import\.meta\.dirname/g, dirname);

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
