import { DOM_IDS } from '@utils/constants.js';
import { cloneTemplate } from '@utils/dom.js';

/** One message in the chat. Its markup is the user-message or agent-message template. */
export class ChatMessage {
    /**
     * @param {string} text - The message text.
     * @param {'user' | 'agent' | 'error'} sender - An error is shown as a reply of the agent, in red.
     */
    constructor(text, sender) {
        this.text = text;
        this.sender = sender;
    }

    createElement() {
        const message = cloneTemplate(this.sender === 'user' ? DOM_IDS.USER_MESSAGE_TEMPLATE : DOM_IDS.AGENT_MESSAGE_TEMPLATE);
        message.classList.toggle('error', this.sender === 'error');
        message.querySelector('.bubble').textContent = this.text;
        return message;
    }
}
