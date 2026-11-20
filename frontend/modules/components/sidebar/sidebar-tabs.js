import { DOM_IDS } from '@utils/constants.js';

/** The two tabs of the sidebar: the chat and the memory. */
export class SidebarTabs {
    /** @param {() => void} onShowMemory - Called when the memory tab is opened, to load what it shows. */
    constructor(onShowMemory) {
        this.chatTab = document.getElementById(DOM_IDS.CHAT_TAB);
        this.memoryTab = document.getElementById(DOM_IDS.MEMORY_TAB);
        this.chatPanel = document.getElementById(DOM_IDS.CHAT_PANEL);
        this.memoryPanel = document.getElementById(DOM_IDS.MEMORY_PANEL);
        this.onShowMemory = onShowMemory;

        this.chatTab.addEventListener('click', () => this.showChat());
        this.memoryTab.addEventListener('click', () => this.showMemory());
    }

    get isMemoryOpen() {
        return !this.memoryPanel.hidden;
    }

    showChat() {
        this.select(this.chatTab, this.memoryTab);
        this.chatPanel.hidden = false;
        this.memoryPanel.hidden = true;
    }

    showMemory() {
        this.select(this.memoryTab, this.chatTab);
        this.chatPanel.hidden = true;
        this.memoryPanel.hidden = false;
        this.onShowMemory();
    }

    select(selected, other) {
        selected.classList.add('active');
        selected.setAttribute('aria-current', 'true');
        other.classList.remove('active');
        other.removeAttribute('aria-current');
    }
}
