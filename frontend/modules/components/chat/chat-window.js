import { DOM_IDS } from '@utils/constants.js';
import { formatMessage } from '@utils/message-formatter.js';
import { ChatMessage } from './chat-message.js';
import { ResponseInfo } from './response-info.js';
import { TaskProgress } from './task-progress.js';

/** The conversation: the messages and the steps of the turn that is running. */
export class ChatWindow {
    constructor() {
        this.messagesList = document.getElementById(DOM_IDS.MESSAGES);
        this.taskProgress = new TaskProgress(this.messagesList);
        this.reply = null; // The agent's reply while it is being written
        this.replyText = '';
    }

    /**
     * @param {string} text
     * @param {'user' | 'agent' | 'error'} sender
     * @returns {HTMLElement} The message as it is shown in the chat.
     */
    addMessage(text, sender) {
        const message = new ChatMessage(text, sender).createElement();
        this.messagesList.append(message);
        this.scrollToEnd();
        return message;
    }

    /** The traveler sent a message: show it, and start the list of steps under it. */
    startTurn(text) {
        this.reply = null;
        this.replyText = '';
        this.addMessage(text, 'user');
        this.taskProgress.start();
        this.scrollToEnd();
    }

    showStep(key, label, status, durationMs) {
        this.taskProgress.show(key, label, status, durationMs);
        this.scrollToEnd();
    }

    showStepInfo(key, info) {
        this.taskProgress.showInfo(key, info);
        this.scrollToEnd();
    }

    /** Add a piece of the reply, as the model writes it. */
    appendToReply(text) {
        this.replyText += text;
        this.writeReply(this.replyText);
    }

    /**
     * The reply is done. The finished text replaces what streamed in, which may include text from before a tool call.
     * @param {string} text
     * @param {Object} [responseInfo] - How long the turn took and what it used. It is shown in a box under the reply.
     */
    finishReply(text, responseInfo) {
        if (text) this.writeReply(text);
        if (responseInfo && this.reply) {
            this.reply.after(new ResponseInfo(responseInfo).createElement());
            this.scrollToEnd();
        }
    }

    showError(text) {
        this.addMessage(text, 'error');
    }

    /** Empty the chat, for a new session. */
    clear() {
        this.messagesList.replaceChildren();
        this.reply = null;
        this.replyText = '';
    }

    writeReply(text) {
        this.reply ??= this.addMessage('', 'agent');
        this.reply.querySelector('.bubble').innerHTML = formatMessage(text);
        this.scrollToEnd();
    }

    scrollToEnd() {
        this.messagesList.scrollTop = this.messagesList.scrollHeight;
    }
}
