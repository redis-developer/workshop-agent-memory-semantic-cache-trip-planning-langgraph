import { DOM_IDS } from '@utils/constants.js';
import { toUserId } from '@utils/user-id.js';

const NAME_ERROR = 'Use letters, numbers and spaces only.';

/**
 * The login screen. The name typed here is the traveler's ID, which stands in for a real login.
 * In a real app the ID comes from the signed-in user on the server, never from the browser.
 */
export class LoginView {
    /** @param {(userId: string) => void} onLogin - Called with the traveler's ID when a usable name is submitted. */
    constructor(onLogin) {
        this.screen = document.getElementById(DOM_IDS.LOGIN);
        this.form = document.getElementById(DOM_IDS.LOGIN_FORM);
        this.name = document.getElementById(DOM_IDS.LOGIN_NAME);
        this.error = document.getElementById(DOM_IDS.LOGIN_ERROR);

        this.form.addEventListener('submit', (event) => {
            event.preventDefault();
            const userId = toUserId(this.name.value);
            if (!userId) {
                this.showNameError();
                return;
            }
            this.error.hidden = true;
            onLogin(userId);
        });
    }

    show() {
        this.screen.hidden = false;
        this.name.value = '';
        this.name.focus();
    }

    hide() {
        this.screen.hidden = true;
    }

    showNameError() {
        this.error.textContent = NAME_ERROR;
        this.error.hidden = false;
    }
}
