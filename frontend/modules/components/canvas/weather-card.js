import { DOM_IDS } from '@utils/constants.js';
import { cloneTemplate, safeUrl } from '@utils/dom.js';

const WEATHER_ICONS = [
    [/rain|shower|storm|drizzle/, '☔'],
    [/snow/, '❄️'],
    [/hot|sunny|clear/, '☀️'],
    [/cloud|overcast/, '☁️'],
    [/cool|cold/, '🌥'],
];

/**
 * The weather the agent found, as a card.
 * @param {{city: string, when: string, condition: string, temperature: string, rainChance: number, airQuality?: string, pollen?: string, source?: {url: string}}} weather
 * @returns {HTMLElement}
 */
export function renderWeatherCard(weather) {
    const card = cloneTemplate(DOM_IDS.WEATHER_CARD_TEMPLATE);
    const condition = weather.condition.toLowerCase();
    card.querySelector('.weather-icon').textContent = WEATHER_ICONS.find(([pattern]) => pattern.test(condition))?.[1] ?? '🌤';
    card.querySelector('.weather-temp').textContent = weather.temperature;
    card.querySelector('.weather-condition').textContent = `${weather.city} · ${weather.when} · ${weather.condition}`;
    card.querySelector('.weather-rain').textContent = `${Math.round(weather.rainChance)}% chance of rain`;

    // What the weather may not have is hidden when it is missing
    const air = card.querySelector('.weather-air');
    air.textContent = `Air: ${weather.airQuality}`;
    air.hidden = !weather.airQuality;
    const pollen = card.querySelector('.weather-pollen');
    pollen.textContent = `Pollen: ${weather.pollen}`;
    pollen.hidden = !weather.pollen;

    const source = card.querySelector('.place-source');
    const href = safeUrl(weather.source?.url);
    source.hidden = !href;
    if (href) {
        source.href = href;
        source.textContent = 'Google ↗';
    }
    return card;
}
