import { DOM_IDS } from '@utils/constants.js';
import { cloneTemplate } from '@utils/dom.js';

const STEP_LABELS = {
    retrieve_memories: 'Looking up what I remember about you',
    agent: 'Thinking',
    search_memories: 'Searching your memories',
    save_memory: 'Saving a memory',
    search_places: 'Searching Google Maps for places',
    lookup_weather: 'Checking the weather',
};

/** The steps the agent takes in one turn, shown in the chat under the traveler's message. */
export class TaskProgress {
    /** @param {HTMLElement} messagesList - The list of the chat, where the steps are added. */
    constructor(messagesList) {
        this.messagesList = messagesList;
        this.stepList = null; // The list of the turn that is running
    }

    /** Start the list of steps for a new turn. */
    start() {
        const progress = cloneTemplate(DOM_IDS.TASK_PROGRESS_TEMPLATE);
        this.stepList = progress.querySelector('.step-list');
        this.messagesList.append(progress);
    }

    /**
     * Show a step: a dot that is lit while it runs, and how long it took once it is done.
     * @param {string} key - Tells this run of the step from another: the agent step runs again after each pass of the tools.
     * @param {string} step
     * @param {'started' | 'finished'} status
     * @param {number} [durationMs]
     */
    show(key, step, status, durationMs) {
        if (!this.stepList) return;

        let row = this.stepList.querySelector(`[data-key="${key}"]`);
        if (!row) {
            row = cloneTemplate(DOM_IDS.STEP_TEMPLATE);
            row.dataset.key = key;
            row.querySelector('.step-label').textContent = STEP_LABELS[step] ?? step;
            this.stepList.append(row);
        }
        row.classList.toggle('running', status === 'started');
        row.classList.toggle('done', status === 'finished');

        if (durationMs !== undefined) {
            const duration = row.querySelector('.step-duration');
            duration.textContent = `${durationMs.toLocaleString()} ms`;
            duration.dateTime = `PT${durationMs / 1000}S`;
            duration.hidden = false;
        }
    }
}
