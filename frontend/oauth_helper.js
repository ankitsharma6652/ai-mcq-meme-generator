/**
 * OAuth Helper Functions for Frontend
 * Handles OAuth login flows for social providers
 */

const OAUTH_BASE_URL = 'http://localhost:8000/api/auth';

/**
 * Initiate OAuth login for a provider
 * @param {string} provider - Provider name (google, github, linkedin, twitter)
 */
export async function initiateOAuthLogin(provider) {
    try {
        const response = await fetch(`${OAUTH_BASE_URL}/login/${provider}`);
        const data = await response.json();

        if (data.authorization_url) {
            // Redirect to provider's authorization page
            window.location.href = data.authorization_url;
        } else {
            throw new Error('No authorization URL returned');
        }
    } catch (error) {
        console.error(`OAuth login failed for ${provider}:`, error);
        alert(`Failed to initiate ${provider} login. Please try again or use email/password.`);
    }
}

/**
 * Extract token from URL after OAuth callback
 * Call this on page load to check if user just logged in via OAuth
 */
export function getOAuthTokenFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const provider = urlParams.get('provider');

    if (token && provider) {
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
        return { token, provider };
    }

    return null;
}

/**
 * Check if OAuth provider is configured
 * @param {string} provider - Provider name
 * @returns {Promise<boolean>}
 */
export async function isOAuthProviderConfigured(provider) {
    try {
        const response = await fetch(`${OAUTH_BASE_URL}/login/${provider}`);
        return response.ok;
    } catch {
        return false;
    }
}
