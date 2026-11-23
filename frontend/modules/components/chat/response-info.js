import { DOM_IDS } from '@utils/constants.js';
import { cloneTemplate } from '@utils/dom.js';

/** "cache_read" becomes "Cache read" */
function toLabel(name) {
    return `${name.charAt(0).toUpperCase()}${name.slice(1).replace(/_/g, ' ')}`;
}

/** The box under a reply: how long it took and what it used. Its markup is the response-info template. */
export class ResponseInfo {
    /**
     * @param {{usage: {inputTokens: number, outputTokens: number, totalTokens: number, inputTokenDetails: Object, outputTokenDetails: Object}, responseTime: number, isCacheHit: boolean}} details
     */
    constructor({ usage, responseTime, isCacheHit }) {
        this.usage = usage;
        this.responseTime = responseTime;
        this.isCacheHit = isCacheHit;
    }

    createElement() {
        const { inputTokens, outputTokens, totalTokens, inputTokenDetails, outputTokenDetails } = this.usage;
        const footer = cloneTemplate(DOM_IDS.RESPONSE_INFO_TEMPLATE);

        footer.querySelector('.response-time').textContent = `${this.responseTime.toFixed(1)}s`;
        footer.querySelector('.token-total').textContent = `${totalTokens.toLocaleString()} tokens`;
        footer.querySelector('.cached-badge').hidden = !this.isCacheHit;
        footer.querySelector('.cached-message').hidden = !this.isCacheHit;
        footer.querySelector('.no-model-calls-message').hidden = totalTokens !== 0;

        const detailRows = (counts) => Object.entries(counts ?? {}).map(([name, value]) => [toLabel(name), value.toLocaleString()]);
        const rows = [
            ['Response time', `${this.responseTime.toFixed(3)}s`],
            ['Input tokens', inputTokens.toLocaleString()],
            ...detailRows(inputTokenDetails),
            ['Output tokens', outputTokens.toLocaleString()],
            ...detailRows(outputTokenDetails),
            ['Total tokens', totalTokens.toLocaleString()],
        ];
        footer.querySelector('.usage').append(
            ...rows.map(([name, value]) => {
                const row = cloneTemplate(DOM_IDS.USAGE_ROW_TEMPLATE);
                row.querySelector('.usage-name').textContent = name;
                row.querySelector('.usage-value').textContent = value;
                return row;
            }),
        );
        return footer;
    }
}
