import { DOM_IDS } from '@utils/constants.js';
import { cloneTemplate } from '@utils/dom.js';

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
     * Show what a step says about what it did, under its name.
     * @param {string} key - The step it is about.
     * @param {string} info
     */
    showInfo(key, info) {
        const row = this.stepList?.querySelector(`[data-key="${key}"]`);
        if (!row || !info) return;

        const infoLine = row.querySelector('.step-info');
        infoLine.textContent = info;
        infoLine.hidden = false;
    }

    /**
     * Show a step: a dot that is lit while it runs, and how long it took once it is done.
     * @param {string} key - Tells this run of the step from another: the agent step runs again after each pass of the tools.
     * @param {string} label - What the server says to show for the step.
     * @param {'started' | 'finished' | 'failed'} status
     * @param {number} [durationMs]
     */
    show(key, label, status, durationMs) {
        if (!this.stepList) return;

        let row = this.stepList.querySelector(`[data-key="${key}"]`);
        if (!row) {
            row = cloneTemplate(DOM_IDS.STEP_TEMPLATE);
            row.dataset.key = key;
            row.querySelector('.step-label').textContent = label;
            this.stepList.append(row);
        }
        row.classList.toggle('running', status === 'started');
        row.classList.toggle('done', status === 'finished');
        row.classList.toggle('failed', status === 'failed');

        if (durationMs !== undefined) {
            const duration = row.querySelector('.step-duration');
            duration.textContent = `${durationMs.toLocaleString()} ms`;
            duration.dateTime = `PT${durationMs / 1000}S`;
            duration.hidden = false;
        }
    }
}
