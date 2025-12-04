const CACHE_NAME = 'quiz-meme-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/app_new.js',
    '/index.css',
    '/style.css',
    '/manifest.json',
    'https://unpkg.com/react@17/umd/react.production.min.js',
    'https://unpkg.com/react-dom@17/umd/react-dom.production.min.js',
    'https://unpkg.com/babel-standalone@6/babel.min.js',
    'https://fonts.googleapis.com/icon?family=Material+Icons',
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'
];

// Install Event: Cache core assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('📦 [Service Worker] Caching all: app shell and content');
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate Event: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🧹 [Service Worker] Clearing old cache');
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch Event: Network First for API, Cache First for Assets
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Strategy for API calls (User Data, Quizzes): Network First -> Fallback to Cache
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Clone and cache the response for offline use
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                    return response;
                })
                .catch(() => {
                    // If offline, try to return cached data
                    return caches.match(event.request);
                })
        );
    }
    // Strategy for Static Assets: Cache First -> Fallback to Network
    else {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request);
            })
        );
    }
});

// Sync Event: Handle background syncing of offline actions (if supported)
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-activity') {
        console.log('🔄 [Service Worker] Syncing offline activity...');
        // Logic to push local storage data to server would go here
        // For now, the main app handles this on "online" event
    }
});
