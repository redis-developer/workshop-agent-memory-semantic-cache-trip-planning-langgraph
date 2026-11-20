/** A copy of the markup of a <template>, ready to be filled in and added to the page. */
export function cloneTemplate(templateId) {
    return document.getElementById(templateId).content.firstElementChild.cloneNode(true);
}

/** A link address from the web that is safe to put in an href: http or https only. Null for anything else. */
export function safeUrl(url) {
    try {
        const parsed = new URL(url);
        return parsed.protocol === 'http:' || parsed.protocol === 'https:' ? parsed.href : null;
    } catch {
        return null;
    }
}
