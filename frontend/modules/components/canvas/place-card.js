import { DOM_IDS } from '@utils/constants.js';
import { cloneTemplate, safeUrl } from '@utils/dom.js';

/**
 * One place the agent found, as a card.
 * @param {{name: string, rating?: string, description: string, url?: string}} place
 * @returns {HTMLElement}
 */
export function renderPlaceCard(place) {
    const card = cloneTemplate(DOM_IDS.PLACE_CARD_TEMPLATE);
    card.querySelector('.place-badge').textContent = place.name.charAt(0).toUpperCase();
    card.querySelector('.place-name').textContent = place.name;
    card.querySelector('.place-description').textContent = place.description;

    const rating = card.querySelector('.place-rating');
    rating.textContent = place.rating ?? '';
    rating.hidden = !place.rating;

    // The link is shown only when the address is safe
    const source = card.querySelector('.place-source');
    const href = safeUrl(place.url);
    source.hidden = !href;
    if (href) {
        source.href = href;
        source.textContent = `${new URL(href).hostname.replace(/^www\./, '')} ↗`;
    }
    return card;
}
