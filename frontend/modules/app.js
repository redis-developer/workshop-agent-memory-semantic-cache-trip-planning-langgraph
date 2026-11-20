import { Canvas } from '@components/canvas/canvas.js';
import { ChatInput } from '@components/chat/chat-input.js';
import { ChatWindow } from '@components/chat/chat-window.js';
import { MemoryPanel } from '@components/memory/memory-panel.js';
import { SidebarTabs } from '@components/sidebar/sidebar-tabs.js';
import { LoginView } from '@components/user/login-view.js';
import { streamChat } from '@services/chat-service.js';
import { DOM_IDS } from '@utils/constants.js';
import { toDisplayName, toUserId } from '@utils/user-id.js';

const appView = document.getElementById(DOM_IDS.APP);
const userName = document.getElementById(DOM_IDS.USER_NAME);

// Who is logged in. It is in the address (?user=ashwin), so a refresh keeps you logged in and each tab can be a
// different traveler. This stands in for a real login.
const userParam = new URLSearchParams(location.search).get('user');
let userId = toUserId(userParam ?? '') ?? '';
let sessionId = crypto.randomUUID();
/** The ids of the memories the agent was given for the last turn. */
let recalledMemoryIds = [];
/** What the agent did in the last turn: the memories it was given, and each tool it called. */
let turnLines = [];
/** How long the last turn took and what it used. It arrives just before the reply is done. */
let turnUsage = null;

const chatWindow = new ChatWindow();
const chatInput = new ChatInput((message) => send(message));
const canvas = new Canvas((text) => send(text));
const memoryPanel = new MemoryPanel();
const tabs = new SidebarTabs(refreshMemory);
const loginView = new LoginView(logIn);

function refreshMemory() {
    memoryPanel.refresh(userId, sessionId, recalledMemoryIds, turnLines);
}

// ----- A new conversation -----------------------------------------------------------------------------

function startNewSession() {
    sessionId = crypto.randomUUID();
    recalledMemoryIds = [];
    turnLines = [];
    chatWindow.clear();
    canvas.showWelcome();
    if (tabs.isMemoryOpen) refreshMemory();
}

document.getElementById(DOM_IDS.NEW_SESSION).addEventListener('click', startNewSession);

// ----- Logging in and out --------------------------------------------------------------------------------

function showApp() {
    loginView.hide();
    appView.hidden = false;
    userName.textContent = userId;
    canvas.greet(toDisplayName(userId));
    chatInput.focus();
}

function logIn(name) {
    userId = name;
    history.replaceState(null, '', `?user=${userId}`);
    startNewSession();
    showApp();
}

document.getElementById(DOM_IDS.LOG_OUT).addEventListener('click', () => {
    userId = '';
    history.replaceState(null, '', location.pathname);
    startNewSession();
    tabs.showChat();
    appView.hidden = true;
    loginView.show();
});

if (userId) {
    showApp();
} else {
    loginView.show();
    // A ?user= that cannot be used, such as one with a symbol in it
    if (userParam) loginView.showNameError();
}

// ----- Sending a message ------------------------------------------------------------------------------

/** What the server streams back for a turn, one event at a time. */
function handleEvent(event) {
    switch (event.type) {
        case 'step':
            chatWindow.showStep(event.key, event.step, event.status, event.durationMs);
            if (event.input) turnLines.push(`${event.step}(${JSON.stringify(event.input)})`);
            break;
        case 'memories':
            recalledMemoryIds = event.memories.map((memory) => memory.id);
            turnLines.push(`Recalled ${event.memories.length} memories for this message`);
            break;
        case 'attachments':
            canvas.show(event.attachments);
            break;
        case 'token':
            chatWindow.appendToReply(event.text);
            break;
        case 'usage':
            turnUsage = event;
            break;
        case 'done':
            chatWindow.finishReply(event.reply, turnUsage);
            break;
        case 'error':
            chatWindow.showError(`Something went wrong: ${event.message}`);
            break;
    }
}

async function send(message) {
    turnLines = [];
    turnUsage = null;
    chatWindow.startTurn(message);
    chatInput.clear();
    chatInput.setBusy(true);

    try {
        await streamChat({ userId, sessionId, message }, handleEvent);
    } catch (error) {
        chatWindow.showError(`Something went wrong: ${error.message}`);
    } finally {
        chatInput.setBusy(false);
        chatInput.focus();
        if (tabs.isMemoryOpen) refreshMemory();
    }
}
