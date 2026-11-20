/** GET a JSON answer. Throws with the server's message when the request failed. */
export async function getJson(url) {
    const response = await fetch(url);
    const body = await response.json();
    if (!response.ok) throw new Error(body.error ?? `The server answered ${response.status}`);
    return body;
}
