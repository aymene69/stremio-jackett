export async function getAvailabilityAD(magnet, debridApi) {
    const url = `https://api.alldebrid.com/v4/magnet/instant?agent=jackett&apikey=${debridApi}&magnets[]=${magnet}`;
    const response = await fetch(url);
    const json = await response.json();
    if (json.status === "error") {
        return "error";
    }
    const instant = json.data.magnets[0].instant;
    if (instant === true) {
        return true;
    }
        return false;
}
