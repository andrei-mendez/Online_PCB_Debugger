import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const Verify = () => {
  const { token } = useParams();  // Get the token from the URL params
  const [message, setMessage] = useState('');
  const navigate = useNavigate();  // Hook for navigation

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        const response = await fetch(`http://localhost:8000/verify/${token}`);
        const data = await response.json();

        setMessage(data.message);  // Display server response message

        // If email is successfully verified, redirect to login page
        if (data.message === 'Email successfully verified!') {
          // Wait a bit for the message to show before redirecting
          setTimeout(() => {
            navigate('/login');  // Redirect to login page
          }, 2000);  // 2 seconds delay
        }

      } catch (error) {
        setMessage('Error verifying email.');
      }
    };

    verifyEmail();
  }, [token, navigate]);  // Re-run the effect when token changes

  return (
    <div>
      <h1>Email Verification</h1>
      <p>{message}</p> {/* Show the verification message */}
    </div>
  );
};

export default Verify;  // Ensure the component is exported