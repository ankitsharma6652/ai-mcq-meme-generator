/**
 * Analytics SDK - Captures EVERYTHING users do
 * Automatically tracks all interactions without manual intervention
 */

class AnalyticsSDK {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.sessionStartTime = Date.now();
        this.currentPage = window.location.pathname;
        this.pageStartTime = Date.now();
        this.events = [];
        this.batchSize = 10;
        this.flushInterval = 5000; // 5 seconds

        this.init();
    }

    init() {
        // Start session tracking
        this.startSession();

        // Track page view
        this.trackPageView();

        // Auto-track all clicks
        this.trackClicks();

        // Auto-track all form interactions
        this.trackForms();

        // Auto-track scroll depth
        this.trackScrollDepth();

        // Auto-track time on page
        this.trackTimeOnPage();

        // Auto-track page visibility
        this.trackVisibility();

        // Auto-track errors
        this.trackErrors();

        // Flush events periodically
        this.startAutoFlush();

        // Track session end
        this.trackSessionEnd();

        console.log('📊 Analytics SDK initialized - Tracking everything!');
    }

    getOrCreateSessionId() {
        let sessionId = sessionStorage.getItem('analytics_session_id');
        if (!sessionId) {
            sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('analytics_session_id', sessionId);
        }
        return sessionId;
    }

    async startSession() {
        const urlParams = new URLSearchParams(window.location.search);

        try {
            await fetch('/api/track-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    started_at: new Date().toISOString(),
                    is_active: true,
                    pages_viewed: 1,
                    mcqs_generated: 0,
                    quizzes_taken: 0,
                    memes_generated: 0,
                    device_type: this.getDeviceType(),
                    browser: this.getBrowser(),
                    os: this.getOS(),
                    referrer: document.referrer || null,
                    utm_source: urlParams.get('utm_source'),
                    utm_medium: urlParams.get('utm_medium'),
                    utm_campaign: urlParams.get('utm_campaign')
                })
            });
        } catch (error) {
            console.error('Session tracking failed:', error);
        }
    }

    trackPageView() {
        this.trackEvent({
            event_type: 'page_view',
            event_category: 'navigation',
            event_action: 'view',
            page_url: window.location.href,
            page_title: document.title,
            referrer: document.referrer
        });
    }

    trackClicks() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('button, a, [role="button"]');
            if (target) {
                const label = target.textContent?.trim() ||
                    target.getAttribute('aria-label') ||
                    target.id ||
                    target.className;

                this.trackEvent({
                    event_type: 'click',
                    event_category: 'engagement',
                    event_action: 'click',
                    event_label: label.substring(0, 100),
                    metadata: {
                        element_type: target.tagName,
                        element_id: target.id,
                        element_class: target.className,
                        href: target.href
                    }
                });
            }
        }, true);
    }

    trackForms() {
        // Track input focus
        document.addEventListener('focus', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.trackEvent({
                    event_type: 'input_focus',
                    event_category: 'engagement',
                    event_action: 'focus',
                    event_label: e.target.name || e.target.id || e.target.placeholder
                });
            }
        }, true);

        // Track input changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.trackEvent({
                    event_type: 'input_change',
                    event_category: 'engagement',
                    event_action: 'change',
                    event_label: e.target.name || e.target.id,
                    metadata: {
                        input_type: e.target.type,
                        has_value: !!e.target.value
                    }
                });
            }
        }, true);
    }

    trackScrollDepth() {
        let maxScroll = 0;
        let scrollTimeout;

        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrollPercent = Math.round(
                    (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
                );

                if (scrollPercent > maxScroll) {
                    maxScroll = scrollPercent;

                    // Track milestones
                    if ([25, 50, 75, 100].includes(scrollPercent)) {
                        this.trackEvent({
                            event_type: 'scroll_depth',
                            event_category: 'engagement',
                            event_action: 'scroll',
                            event_label: `${scrollPercent}%`,
                            event_value: scrollPercent
                        });
                    }
                }
            }, 100);
        });
    }

    trackTimeOnPage() {
        // Track every 30 seconds
        setInterval(() => {
            const timeOnPage = (Date.now() - this.pageStartTime) / 1000;
            this.trackEvent({
                event_type: 'time_on_page',
                event_category: 'engagement',
                event_action: 'time_spent',
                event_value: timeOnPage,
                time_on_page: timeOnPage
            });
        }, 30000);
    }

    trackVisibility() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.trackEvent({
                    event_type: 'page_hidden',
                    event_category: 'navigation',
                    event_action: 'hide',
                    time_on_page: (Date.now() - this.pageStartTime) / 1000
                });
            } else {
                this.trackEvent({
                    event_type: 'page_visible',
                    event_category: 'navigation',
                    event_action: 'show'
                });
                this.pageStartTime = Date.now();
            }
        });
    }

    trackErrors() {
        window.addEventListener('error', (e) => {
            this.trackEvent({
                event_type: 'javascript_error',
                event_category: 'error',
                event_action: 'error',
                event_label: e.message,
                metadata: {
                    filename: e.filename,
                    line: e.lineno,
                    column: e.colno,
                    stack: e.error?.stack
                }
            });
        });

        window.addEventListener('unhandledrejection', (e) => {
            this.trackEvent({
                event_type: 'promise_rejection',
                event_category: 'error',
                event_action: 'rejection',
                event_label: e.reason?.message || 'Unknown error',
                metadata: {
                    reason: String(e.reason)
                }
            });
        });
    }

    trackSessionEnd() {
        const endSession = () => {
            const sessionDuration = (Date.now() - this.sessionStartTime) / 1000;

            // Use sendBeacon for reliable tracking on page unload
            const data = JSON.stringify({
                session_id: this.sessionId,
                ended_at: new Date().toISOString(),
                duration_seconds: sessionDuration,
                is_active: false
            });

            navigator.sendBeacon('/api/track-session', data);
        };

        window.addEventListener('beforeunload', endSession);
        window.addEventListener('pagehide', endSession);
    }

    trackEvent(eventData) {
        const event = {
            session_id: this.sessionId,
            event_type: eventData.event_type,
            event_category: eventData.event_category,
            event_action: eventData.event_action,
            event_label: eventData.event_label || null,
            event_value: eventData.event_value || null,
            page_url: window.location.href,
            page_title: document.title,
            referrer: document.referrer || null,
            device_type: this.getDeviceType(),
            browser: this.getBrowser(),
            os: this.getOS(),
            time_on_page: eventData.time_on_page || null,
            metadata: eventData.metadata || null
        };

        this.events.push(event);

        // Auto-flush if batch is full
        if (this.events.length >= this.batchSize) {
            this.flush();
        }
    }

    async flush() {
        if (this.events.length === 0) return;

        const eventsToSend = [...this.events];
        this.events = [];

        try {
            for (const event of eventsToSend) {
                await fetch('/api/track-event', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
                    },
                    body: JSON.stringify(event)
                });
            }
        } catch (error) {
            console.error('Event tracking failed:', error);
            // Re-add events if failed
            this.events.unshift(...eventsToSend);
        }
    }

    startAutoFlush() {
        setInterval(() => this.flush(), this.flushInterval);
    }

    // Custom event tracking for specific actions
    trackCustomEvent(type, category, action, label = null, value = null, metadata = null) {
        this.trackEvent({
            event_type: type,
            event_category: category,
            event_action: action,
            event_label: label,
            event_value: value,
            metadata: metadata
        });
    }

    // Helper methods
    getDeviceType() {
        const ua = navigator.userAgent;
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            return 'tablet';
        }
        if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
            return 'mobile';
        }
        return 'desktop';
    }

    getBrowser() {
        const ua = navigator.userAgent;
        if (ua.includes('Firefox')) return 'Firefox';
        if (ua.includes('Chrome')) return 'Chrome';
        if (ua.includes('Safari')) return 'Safari';
        if (ua.includes('Edge')) return 'Edge';
        if (ua.includes('Opera')) return 'Opera';
        return 'Unknown';
    }

    getOS() {
        const ua = navigator.userAgent;
        if (ua.includes('Win')) return 'Windows';
        if (ua.includes('Mac')) return 'MacOS';
        if (ua.includes('Linux')) return 'Linux';
        if (ua.includes('Android')) return 'Android';
        if (ua.includes('iOS')) return 'iOS';
        return 'Unknown';
    }
}

// Initialize analytics automatically
window.analytics = new AnalyticsSDK();

// Export for use in other scripts
window.trackEvent = (type, category, action, label, value, metadata) => {
    window.analytics.trackCustomEvent(type, category, action, label, value, metadata);
};
