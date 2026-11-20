import { fetchSession } from '@services/chat-service.js';
import { fetchProfile } from '@services/user-service.js';
import { DOM_IDS } from '@utils/constants.js';
import { cloneTemplate } from '@utils/dom.js';

/** What Redis Agent Memory holds for this traveler and conversation, and what the agent did in the last turn. */
export class MemoryPanel {
    constructor() {
        this.error = document.getElementById(DOM_IDS.MEMORY_ERROR);
        this.content = document.getElementById(DOM_IDS.MEMORY_CONTENT);
        this.turn = document.getElementById(DOM_IDS.MEMORY_TURN);
        this.sessionCount = document.getElementById(DOM_IDS.MEMORY_SESSION_COUNT);
        this.summary = document.getElementById(DOM_IDS.MEMORY_SUMMARY);
        this.entriesTitle = document.getElementById(DOM_IDS.MEMORY_ENTRIES_TITLE);
        this.entries = document.getElementById(DOM_IDS.MEMORY_ENTRIES);
    }

    /**
     * Fetch what the service holds, and show it.
     * @param {string} userId
     * @param {string} sessionId
     * @param {string[]} recalledMemoryIds - The memories the agent was given for the last message, which are marked.
     * @param {string[]} turnLines - What the agent did in the last turn, as the page saw it happen.
     */
    async refresh(userId, sessionId, recalledMemoryIds, turnLines) {
        let session;
        let profile;
        try {
            [session, profile] = await Promise.all([fetchSession(sessionId), fetchProfile(userId)]);
        } catch (error) {
            this.error.textContent = `Could not read memory: ${error.message}`;
            this.error.hidden = false;
            this.content.hidden = true;
            return;
        }
        this.error.hidden = true;
        this.content.hidden = false;

        // This turn
        this.turn.replaceChildren(
            ...turnLines.map((line) => {
                const item = cloneTemplate(DOM_IDS.TURN_LINE_TEMPLATE);
                item.textContent = line;
                return item;
            }),
        );

        // Session memory: this conversation
        this.sessionCount.textContent = `${session.messageCount} messages stored`;
        this.summary.textContent = session.summary ? `Summary: ${session.summary}` : '';
        this.summary.hidden = !session.summary;

        // Long-term memory: what the service knows about this traveler across conversations
        this.entriesTitle.textContent = `Long-term memory · ${userId}`;
        this.entries.replaceChildren(...profile.entries.map((memory) => this.createEntry(memory, recalledMemoryIds.includes(memory.id))));

        // Each list shows its empty message only when it has nothing to show
        this.turn.nextElementSibling.hidden = turnLines.length > 0;
        this.summary.nextElementSibling.hidden = Boolean(session.summary);
        this.entries.nextElementSibling.hidden = profile.entries.length > 0;
    }

    createEntry(memory, recalled) {
        const entry = cloneTemplate(DOM_IDS.MEMORY_ENTRY_TEMPLATE);
        entry.classList.toggle('recalled', recalled);
        entry.querySelector('.memory-text').textContent = memory.text;
        entry.querySelector('.memory-details').textContent = [memory.memoryType, ...(memory.topics ?? []), ...(recalled ? ['recalled this turn'] : [])].join(' · ');
        return entry;
    }
}
