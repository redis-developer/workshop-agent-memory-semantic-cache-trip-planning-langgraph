/** "maya-chen" becomes "Maya Chen": the name to show for a traveler's id. */
export function toDisplayName(userId) {
    return userId
        .split('-')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/** "Maya Chen" becomes "maya-chen": lowercase letters, numbers and hyphens. Null when the name cannot be used. */
export function toUserId(name) {
    const id = name.trim().toLowerCase().replace(/\s+/g, '-');
    return /^[a-z0-9-]{1,40}$/.test(id) ? id : null;
}
