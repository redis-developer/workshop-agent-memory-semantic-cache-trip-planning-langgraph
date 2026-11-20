export const DOM_IDS = {
    LOGIN: 'login', // The login screen
    LOGIN_FORM: 'login-form', // The form on it
    LOGIN_NAME: 'login-name', // The text box for the traveler's name
    LOGIN_ERROR: 'login-error', // Says the name cannot be used
    APP: 'app', // The app: the canvas and the sidebar
    USER_NAME: 'user-name', // Shows who is logged in
    NEW_SESSION: 'new-session', // Button that starts a fresh conversation
    LOG_OUT: 'log-out', // Button that returns to the login screen
    CANVAS: 'canvas', // The main pane, which shows the welcome text or what the agent found
    WELCOME_LABEL: 'welcome-label', // The greeting above the headline of the welcome text
    WEATHER: 'weather', // Where the weather card is added
    WEATHER_CARD_TEMPLATE: 'weather-card-template', // Template for the weather card
    PLACES: 'places', // The list the place cards are added to
    PLACE_CARD_TEMPLATE: 'place-card-template', // Template for one place card
    CHAT_TAB: 'chat-tab', // The tab button for the chat
    MEMORY_TAB: 'memory-tab', // The tab button for the memory panel
    CHAT_PANEL: 'chat-panel', // The chat tab's content
    MEMORY_PANEL: 'memory-panel', // The memory tab's content
    MESSAGES: 'messages', // The list the chat messages are added to
    USER_MESSAGE_TEMPLATE: 'user-message-template', // Template for a message the traveler sent
    AGENT_MESSAGE_TEMPLATE: 'agent-message-template', // Template for a reply of the agent
    TASK_PROGRESS_TEMPLATE: 'task-progress-template', // Template for the steps of one turn, which stay above the reply
    STEP_TEMPLATE: 'step-template', // Template for one step in that list
    RESPONSE_INFO_TEMPLATE: 'response-info-template', // Template for the box under a reply: its time and its tokens
    USAGE_ROW_TEMPLATE: 'usage-row-template', // Template for one line in that box
    CHAT_FORM: 'chat-form', // The form the traveler types a message in
    CHAT_INPUT: 'chat-input', // The text box of that form
    SEND_BUTTON: 'send', // The send button of that form
    MEMORY_ERROR: 'memory-error', // Says the memory could not be read
    MEMORY_CONTENT: 'memory-content', // The sections of the memory panel
    MEMORY_TURN: 'memory-turn', // The list of what the agent did in the last turn
    TURN_LINE_TEMPLATE: 'turn-line-template', // Template for one line in that list
    MEMORY_SESSION_COUNT: 'memory-session-count', // How many messages the session holds
    MEMORY_SUMMARY: 'memory-summary', // The summary of the conversation
    MEMORY_ENTRIES_TITLE: 'memory-entries-title', // Heading of the long-term memories, with the traveler's name
    MEMORY_ENTRIES: 'memory-entries', // The list of long-term memories
    MEMORY_ENTRY_TEMPLATE: 'memory-entry-template', // Template for one long-term memory
};

// What the canvas shows, one at a time. It is the data-view of the canvas, and the CSS shows the matching section.
export const CANVAS_VIEWS = {
    WELCOME: 'welcome',
    RESULTS: 'results',
};
