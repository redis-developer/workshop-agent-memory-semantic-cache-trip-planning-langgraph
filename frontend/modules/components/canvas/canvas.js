import { CANVAS_VIEWS, DOM_IDS } from '@utils/constants.js';
import { renderPlaceCard } from './place-card.js';
import { renderWeatherCard } from './weather-card.js';

/**
 * The main pane. It shows the welcome text until the agent finds something, then what it found:
 * the weather and the places (its attachments).
 */
export class Canvas {
    /** @param {(text: string) => void} onSamplePick - Called with the text of a sample prompt that was clicked. */
    constructor(onSamplePick) {
        this.canvas = document.getElementById(DOM_IDS.CANVAS);
        this.welcomeLabel = document.getElementById(DOM_IDS.WELCOME_LABEL);

        // Where each type of attachment is drawn, how to draw it, and how many of the latest ones to show
        this.slots = {
            weather: { list: document.getElementById(DOM_IDS.WEATHER), render: renderWeatherCard, latest: 1 },
            place: { list: document.getElementById(DOM_IDS.PLACES), render: renderPlaceCard, latest: Infinity },
        };

        this.canvas.addEventListener('click', (event) => {
            const sample = event.target.closest('.sample');
            if (sample) onSamplePick(sample.dataset.text);
        });
    }

    /** @param {string} name - Who is logged in, for the greeting on the welcome text. */
    greet(name) {
        this.welcomeLabel.textContent = `Welcome, ${name}`;
    }

    /** The welcome text, for a new conversation. It also clears what the last conversation found. */
    showWelcome() {
        for (const { list } of Object.values(this.slots)) list.replaceChildren();
        this.canvas.dataset.view = CANVAS_VIEWS.WELCOME;
    }

    /**
     * Draw what came with the agent's reply. A type the reply did not bring is left as it was.
     * The welcome text stays until there is something to show, and what was found before stays until something new is found.
     * @param {Array<{type: string, data: Object}>} attachments
     */
    show(attachments) {
        for (const [type, { list, render, latest }] of Object.entries(this.slots)) {
            const found = attachments.filter((attachment) => attachment.type === type).slice(-latest);
            if (found.length > 0) list.replaceChildren(...found.map((attachment) => render(attachment.data)));
        }
        if (attachments.length > 0) this.canvas.dataset.view = CANVAS_VIEWS.RESULTS;
    }
}
