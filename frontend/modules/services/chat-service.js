import { getJson } from './http.js';

/** What the service holds for one conversation: { messageCount, summary }. */
export function fetchSession(userId, sessionId) {
    return getJson(`/api/chat/session?userId=${encodeURIComponent(userId)}&sessionId=${encodeURIComponent(sessionId)}`);
}

/**
 * Send one message and read the events the server streams back, one JSON object per line.
 * Calls `onEvent` with each one. See the event types in backend/modules/ai/agent_workflow/stream_events.py.
 */
export async function streamChat({ userId, sessionId, message }, onEvent) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, sessionId, message }),
    });
    if (!response.ok || !response.body) throw new Error(`The server answered ${response.status}`);

    const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
    let unread = '';
    for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        unread += value;
        const lines = unread.split('\n');
        unread = lines.pop(); // the last piece may be half a line
        for (const line of lines) if (line.trim()) onEvent(JSON.parse(line));
    }
}
