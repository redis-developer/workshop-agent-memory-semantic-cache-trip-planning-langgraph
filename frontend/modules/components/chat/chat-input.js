import { DOM_IDS } from '@utils/constants.js';

/** The box the traveler types a message in, and the send button. */
export class ChatInput {
    /** @param {(message: string) => void} onSubmit - Called with the message when the traveler sends one. */
    constructor(onSubmit) {
        this.form = document.getElementById(DOM_IDS.CHAT_FORM);
        this.input = document.getElementById(DOM_IDS.CHAT_INPUT);
        this.sendButton = document.getElementById(DOM_IDS.SEND_BUTTON);

        this.form.addEventListener('submit', (event) => {
            event.preventDefault();
            const message = this.input.value.trim();
            if (message && !this.sendButton.disabled) onSubmit(message);
        });
    }

    clear() {
        this.input.value = '';
    }

    focus() {
        this.input.focus();
    }

    /** While the agent works on a reply, another message cannot be sent. */
    setBusy(busy) {
        this.sendButton.disabled = busy;
    }
}
