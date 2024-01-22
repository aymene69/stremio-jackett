export async function getName(id, type) {
	if (typeof id !== "string") {
		return id;
	}

	const res = await fetch(`https://v3-cinemeta.strem.io/meta/${type}/${id}.json`);
	const name = (await res.json()).meta.name;

	return name;
}
