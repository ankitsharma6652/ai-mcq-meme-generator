import React, { useState } from 'react';

const Auth = ({ onLogin }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        phone_number: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const endpoint = isLogin ? '/token' : '/signup';

            // Prepare body based on endpoint
            let body;
            let headers = {};

            if (isLogin) {
                // OAuth2PasswordRequestForm expects form data, not JSON
                body = new URLSearchParams();
                body.append('username', formData.email);
                body.append('password', formData.password);
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
            } else {
                body = JSON.stringify({
                    email: formData.email,
                    password: formData.password,
                    full_name: formData.full_name,
                    phone_number: formData.phone_number || null
                });
                headers['Content-Type'] = 'application/json';
            }

            const res = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                headers: headers,
                body: body
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || 'Authentication failed');
            }

            if (isLogin) {
                // Login successful, save token
                localStorage.setItem('token', data.access_token);
                onLogin(data.access_token);
            } else {
                // Signup successful, switch to login
                setIsLogin(true);
                setError('Account created! Please log in.');
                setLoading(false); // Stop loading but don't auto-login yet
                return;
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
                <p className="auth-subtitle">
                    {isLogin ? 'Login to access your AI workspace' : 'Join to start creating amazing content'}
                </p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit}>
                    {!isLogin && (
                        <>
                            <div className="form-group">
                                <label>Full Name</label>
                                <input
                                    type="text"
                                    name="full_name"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    required
                                    placeholder="John Doe"
                                />
                            </div>
                            <div className="form-group">
                                <label>Phone Number (Optional)</label>
                                <input
                                    type="tel"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleChange}
                                    placeholder="+1234567890"
                                />
                            </div>
                        </>
                    )}

                    <div className="form-group">
                        <label>Email Address</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            placeholder="you@example.com"
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            placeholder="••••••••"
                        />
                    </div>

                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? 'Processing...' : (isLogin ? 'Login' : 'Sign Up')}
                    </button>
                </form>

                <div className="auth-footer">
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <button
                        className="link-btn"
                        onClick={() => {
                            setIsLogin(!isLogin);
                            setError(null);
                        }}
                    >
                        {isLogin ? 'Sign Up' : 'Login'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Auth;
