const { useState } = React;

// Get API base URL (works for both localhost and PythonAnywhere)
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : window.location.origin;

// OAuth Helper Function
const initiateOAuthLogin = async (provider) => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login/${provider}`);
        const data = await response.json();

        if (data.authorization_url) {
            window.location.href = data.authorization_url;
        } else {
            alert(`Failed to initiate ${provider} login. Please configure OAuth credentials.`);
        }
    } catch (error) {
        console.error(`OAuth login failed for ${provider}:`, error);
        alert(`${provider} login is not configured yet.`);
    }
};

const Auth = ({ onLogin }) => {
    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Welcome!</h2>
                <p className="auth-subtitle">
                    Sign in to access your AI workspace
                </p>

                <div className="social-login">
                    <button
                        className="social-btn google-btn"
                        onClick={() => initiateOAuthLogin('google')}
                        style={{
                            width: '100%',
                            padding: '1rem',
                            background: '#fff',
                            border: '1px solid var(--border-color)',
                            borderRadius: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '12px',
                            cursor: 'pointer',
                            fontSize: '1rem',
                            fontWeight: '600',
                            color: '#333',
                            transition: 'all 0.3s',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-2px)';
                            e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                        }}
                    >
                        <svg width="24" height="24" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" /><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" /><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" /><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" /></svg>
                        Continue with Google
                    </button>
                </div>

                <div style={{
                    marginTop: '2rem',
                    padding: '1rem',
                    background: 'rgba(99, 102, 241, 0.05)',
                    borderRadius: '10px',
                    textAlign: 'center',
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)'
                }}>
                    <p style={{ margin: 0 }}>
                        🔒 Secure authentication via Google OAuth
                    </p>
                </div>
            </div>
        </div>
    );
};

window.Auth = Auth;
