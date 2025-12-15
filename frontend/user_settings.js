/**
 * User Settings Component - Updated Version
 */

const UserSettings = ({ isOpen, onClose, token }) => {
    const [profile, setProfile] = React.useState({
        email: '',
        full_name: '',
        phone_number: '',
        designation: '',
        nature_of_work: '',
        company_name: '',
        profile_picture: '',
        bio: '',
        linkedin_url: '',
        twitter_url: '',
        github_url: '',
        website_url: ''
    });
    const [loading, setLoading] = React.useState(false);
    const [saving, setSaving] = React.useState(false);
    const [message, setMessage] = React.useState('');
    const [uploading, setUploading] = React.useState(false);

    React.useEffect(() => {
        if (isOpen && token) {
            fetchProfile();
        }
    }, [isOpen, token]);

    const fetchProfile = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setProfile({
                    email: data.email || '',
                    full_name: data.full_name || '',
                    phone_number: data.phone_number || '',
                    designation: data.designation || '',
                    nature_of_work: data.nature_of_work || '',
                    company_name: data.company_name || '',
                    profile_picture: data.profile_picture || '',
                    bio: data.bio || '',
                    linkedin_url: data.linkedin_url || '',
                    twitter_url: data.twitter_url || '',
                    github_url: data.github_url || '',
                    website_url: data.website_url || ''
                });
            }
        } catch (error) {
            console.error('Failed to fetch profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setProfile({
            ...profile,
            [e.target.name]: e.target.value
        });
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            setMessage('❌ File too large. Max 5MB.');
            return;
        }

        setUploading(true);
        setMessage('📤 Uploading...');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload-image', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                setProfile({
                    ...profile,
                    profile_picture: data.link
                });
                setMessage('✅ Image uploaded successfully!');
            } else {
                console.error('Upload Error:', data);
                setMessage(`❌ Upload failed: ${data.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Upload error:', error);
            setMessage('❌ Network error. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage('');

        try {
            const response = await fetch('/api/profile', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profile)
            });

            if (response.ok) {
                setMessage('✅ Profile updated successfully!');
                setTimeout(() => {
                    onClose();
                    window.location.reload(); // Refresh to show new profile
                }, 1500);
            } else {
                setMessage('❌ Failed to update profile');
            }
        } catch (error) {
            setMessage('❌ Error: ' + error.message);
        } finally {
            setSaving(false);
        }
    };

    if (!isOpen) return null;

    const inputStyle = {
        width: '100%',
        padding: '0.75rem',
        borderRadius: '8px',
        border: '1px solid var(--border-color)',
        background: 'var(--bg-color)',
        color: 'var(--text-primary)',
        fontSize: '0.95rem'
    };

    const labelStyle = {
        display: 'block',
        marginBottom: '0.5rem',
        fontWeight: '500',
        fontSize: '0.9rem'
    };

    return (
        <div className="modal-overlay" style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
            backdropFilter: 'blur(5px)'
        }} onClick={onClose}>
            <div className="settings-modal" style={{
                background: 'var(--card-bg)',
                padding: '2rem',
                borderRadius: '16px',
                maxWidth: '650px',
                width: '90%',
                maxHeight: '85vh',
                overflowY: 'auto',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-color)'
            }} onClick={(e) => e.stopPropagation()}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                        ⚙️ Profile Settings
                    </h2>
                    <button onClick={onClose} style={{
                        background: 'none',
                        border: 'none',
                        fontSize: '1.5rem',
                        cursor: 'pointer',
                        color: 'var(--text-secondary)',
                        padding: '0.5rem'
                    }}>✕</button>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>Loading...</div>
                ) : (
                    <form onSubmit={handleSubmit}>
                        {/* Email - Read Only */}
                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Email</label>
                            <input
                                type="email"
                                value={profile.email}
                                disabled
                                style={{ ...inputStyle, opacity: 0.7, cursor: 'not-allowed' }}
                            />
                        </div>

                        {/* Full Name */}
                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Full Name *</label>
                            <input
                                type="text"
                                name="full_name"
                                value={profile.full_name}
                                onChange={handleChange}
                                placeholder="Your Full Name"
                                style={inputStyle}
                            />
                        </div>

                        {/* Profile Picture */}
                        <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                            <label style={labelStyle}>Profile Picture</label>

                            {profile.profile_picture && (
                                <div style={{ marginBottom: '0.75rem', textAlign: 'center' }}>
                                    <img
                                        src={profile.profile_picture}
                                        alt="Profile Preview"
                                        style={{
                                            width: '100px',
                                            height: '100px',
                                            borderRadius: '50%',
                                            objectFit: 'cover',
                                            border: '3px solid var(--primary-color)'
                                        }}
                                    />
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                <label htmlFor="file-upload" style={{
                                    flex: 1,
                                    padding: '0.75rem',
                                    borderRadius: '8px',
                                    border: '2px dashed var(--primary-color)',
                                    background: 'rgba(99, 102, 241, 0.05)',
                                    color: 'var(--primary-color)',
                                    textAlign: 'center',
                                    cursor: 'pointer',
                                    fontWeight: '500'
                                }}>
                                    {uploading ? '⏳ Uploading...' : '📁 Upload Image'}
                                </label>
                                <input
                                    id="file-upload"
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileUpload}
                                    style={{ display: 'none' }}
                                />
                            </div>

                            <input
                                type="text"
                                name="profile_picture"
                                value={profile.profile_picture}
                                onChange={handleChange}
                                placeholder="Or paste image URL"
                                style={inputStyle}
                            />
                        </div>

                        {/* Designation */}
                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Designation</label>
                            <input
                                type="text"
                                name="designation"
                                value={profile.designation}
                                onChange={handleChange}
                                placeholder="e.g., Senior Developer"
                                style={inputStyle}
                            />
                        </div>

                        {/* Company Name */}
                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Company Name</label>
                            <input
                                type="text"
                                name="company_name"
                                value={profile.company_name}
                                onChange={handleChange}
                                placeholder="Your Company"
                                style={inputStyle}
                            />
                        </div>

                        {/* Nature of Work */}
                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Nature of Work</label>
                            <input
                                type="text"
                                name="nature_of_work"
                                value={profile.nature_of_work}
                                onChange={handleChange}
                                placeholder="e.g., Full Stack Development"
                                style={inputStyle}
                            />
                        </div>

                        {/* Phone */}
                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Phone Number</label>
                            <input
                                type="tel"
                                name="phone_number"
                                value={profile.phone_number}
                                onChange={handleChange}
                                placeholder="+1234567890"
                                style={inputStyle}
                            />
                        </div>

                        {/* Bio */}
                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Bio</label>
                            <textarea
                                name="bio"
                                value={profile.bio}
                                onChange={handleChange}
                                placeholder="Tell us about yourself..."
                                rows="3"
                                style={{ ...inputStyle, resize: 'vertical' }}
                            />
                        </div>

                        <h3 style={{ margin: '1.5rem 0 1rem', fontSize: '1.1rem', fontWeight: '600' }}>🔗 Social Links</h3>

                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>LinkedIn</label>
                            <input
                                type="url"
                                name="linkedin_url"
                                value={profile.linkedin_url}
                                onChange={handleChange}
                                placeholder="https://linkedin.com/in/username"
                                style={inputStyle}
                            />
                        </div>

                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Twitter</label>
                            <input
                                type="url"
                                name="twitter_url"
                                value={profile.twitter_url}
                                onChange={handleChange}
                                placeholder="https://twitter.com/username"
                                style={inputStyle}
                            />
                        </div>

                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>GitHub</label>
                            <input
                                type="url"
                                name="github_url"
                                value={profile.github_url}
                                onChange={handleChange}
                                placeholder="https://github.com/username"
                                style={inputStyle}
                            />
                        </div>

                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label style={labelStyle}>Website</label>
                            <input
                                type="url"
                                name="website_url"
                                value={profile.website_url}
                                onChange={handleChange}
                                placeholder="https://yourwebsite.com"
                                style={inputStyle}
                            />
                        </div>

                        {message && (
                            <div style={{
                                padding: '0.75rem',
                                borderRadius: '8px',
                                marginBottom: '1rem',
                                background: message.includes('✅') ? '#10b98120' : '#ef444420',
                                color: message.includes('✅') ? '#10b981' : '#ef4444',
                                textAlign: 'center'
                            }}>{message}</div>
                        )}

                        <button
                            type="submit"
                            disabled={saving}
                            style={{
                                width: '100%',
                                padding: '0.85rem',
                                borderRadius: '8px',
                                border: 'none',
                                background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                                color: 'white',
                                fontWeight: '600',
                                fontSize: '1rem',
                                cursor: saving ? 'not-allowed' : 'pointer',
                                opacity: saving ? 0.7 : 1
                            }}
                        >
                            {saving ? 'Saving...' : '💾 Save Changes'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

window.UserSettings = UserSettings;
