import { marked } from 'marked';

/**
 * The agent's reply as HTML. The model writes markdown (headings, bold, lists, links), and marked turns it into HTML.
 * Links open in a new tab, and the page they open cannot reach this one.
 * @param {string} text
 * @returns {string}
 */
export function formatMessage(text) {
    return marked.parse(text, { breaks: true }).replaceAll('<a ', '<a target="_blank" rel="noopener noreferrer" ');
}
