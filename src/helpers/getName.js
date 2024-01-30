export async function getName(id, type) {
	if (typeof id !== "string") {
		return id;
	}

	const res = await fetch(`https://v3-cinemeta.strem.io/meta/${type}/${id}.json`);
	// @ts-ignore
	const { meta } = await res.json();
	const { name } = meta;
	// @ts-ignore
	const { releaseInfo } = meta;

	return {
		name: name,
		year: releaseInfo,
	};
}
