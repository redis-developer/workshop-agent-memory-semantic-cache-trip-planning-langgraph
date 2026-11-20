import { getJson } from './http.js';

/** What the service holds about a traveler across conversations: { entries }. */
export function fetchProfile(userId) {
    return getJson(`/api/user/profile?userId=${encodeURIComponent(userId)}`);
}
