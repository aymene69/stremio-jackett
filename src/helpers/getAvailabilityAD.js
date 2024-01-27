export async function getAvailabilityAD(magnet, debridApi) {
    const url = `https://api.alldebrid.com/v4/magnet/instant?agent=jackett&apikey=${debridApi}&magnets[]=${magnet}`;
    const response = await fetch(url);
    const json = await response.json();
    if (json.status === "blocked") {
        return "blocked";
    }
    const instant = json.data.magnets[0].instant;
    if (instant === true) {
        return true;
    }
        return false;
}
