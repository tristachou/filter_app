import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import QRCode from 'qrcode';

function MfaSetupView({ closeView }) {
  const { setupMfa, finalizeMfa, username } = useAuth();
  const [secretCode, setSecretCode] = useState(null);
  const [qrCodeUrl, setQrCodeUrl] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleStartSetup = async () => {
    setError('');
    setSuccess(false);
    if (!username) {
      setError("Username not found. Cannot set up MFA.");
      return;
    }
    try {
      const response = await setupMfa();
      const issuer = 'SimpleGrading App';
      const secret = response.SecretCode;
      setSecretCode(secret);

      // Generate QR code URL with the actual username
      const otpauth = `otpauth://totp/${issuer}:${username}?secret=${secret}&issuer=${issuer}`;
      const dataUrl = await QRCode.toDataURL(otpauth);
      setQrCodeUrl(dataUrl);

    } catch (err) {
      setError(err.message || 'Could not start MFA setup.');
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await finalizeMfa(verificationCode);
      setSuccess(true);
      // Optionally close the view after a delay
      setTimeout(() => {
        closeView();
      }, 3000);
    } catch (err) {
      setError(err.message || 'Verification failed. Check the code and try again.');
    }
  };

  if (success) {
    return (
      <>
        <h3>MFA Enabled Successfully!</h3>
        <p>You will be asked for a code on your next login.</p>
        <button onClick={closeView} className="btn">Close</button>
      </>
    );
  }

  return (
    <>
      <h3>Set Up Two-Factor Authentication</h3>
      {!qrCodeUrl ? (
        <>
          <p>Click the button below to generate a QR code. Scan it with your authenticator app (e.g., Google Authenticator).</p>
          <button onClick={handleStartSetup} className="btn btn-primary">Enable MFA</button>
        </>
      ) : (
        <>
          <p>1. Scan this QR code with your authenticator app.</p>
          <img src={qrCodeUrl} alt="MFA QR Code" style={{ backgroundColor: 'white', padding: '10px', margin: '20px 0' }} />
          <p>2. Enter the 6-digit code from the app to verify.</p>
          <form onSubmit={handleVerify} style={{ marginTop: '20px' }}>
            <input
              type="text"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              placeholder="6-digit code"
              pattern="\d{6}"
              required
            />
            <button type="submit" className="btn btn-primary">Verify & Complete</button>
          </form>
        </>
      )}
      {error && <p className="error-message">{error}</p>}
      <hr style={{ margin: '20px 0' }}/>
      <button onClick={closeView} className="btn btn-secondary">Cancel</button>
    </>
  );
}

export default MfaSetupView;
