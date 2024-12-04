import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

const Login = (props) => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [emailError, setEmailError] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [loginError, setLoginError] = useState('') // New state to track login error

  const navigate = useNavigate()

  // Function to handle form submission (Login)
  const onButtonClick = async () => {
    // Reset errors
    setEmailError('');
    setPasswordError('');
    setLoginError('');

    // Validate inputs
    if ('' === email) {
        setEmailError('Please enter your email');
        return;
    }

    if (!/^[\w.-]+@[\w-]+\.[\w]{2,4}$/.test(email)) {
        setEmailError('Please enter a valid email');
        return;
    }

    if ('' === password) {
        setPasswordError('Please enter a password');
        return;
    }

    if (password.length < 7) {
        setPasswordError('The password must be 8 characters or longer');
        return;
    }

    const formData = new URLSearchParams();
    formData.append('username', email);  // Make sure your backend is expecting 'email'
    formData.append('password', password);

    try {
        const response = await fetch('http://localhost:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString(),  // Send the form data
        });

        if (!response.ok) {
            const errorData = await response.json();

            // Handle case where 'errorData.detail' might not be a string
            let errorMessage = 'Login failed'; // Default error message

            // Check if errorData.detail is an object (e.g., { type, loc, msg, input })
            if (typeof errorData.detail === 'object' && errorData.detail !== null) {
                // Extract the message from the object if possible
                errorMessage = errorData.detail.msg || 'An unknown error occurred';
            } else if (typeof errorData.detail === 'string') {
                // If it's a string, use it directly
                errorMessage = errorData.detail;
            }

            // Handle specific error for unverified email
            if (errorData.detail === "Email not verified") {
                errorMessage = "Your email is not verified. Please check your inbox and verify your email.";
            }

            setLoginError(errorMessage);
            return;
        }

        const data = await response.json();
        console.log(data);

        // Store token and redirect
        localStorage.setItem('authToken', data.access_token);
        navigate('/dashboard');  // Redirect to the dashboard on successful login

    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
        setLoginError('There was a problem with the login request');
    }
};

  return (
    <div className={'mainContainer'}>
      <div className={'titleContainer'}>
        <div>Login</div>
      </div>
      <br />
      <div className={'inputContainer'}>
        <input
          value={email}
          placeholder="Enter your email here"
          onChange={(ev) => setEmail(ev.target.value)}
          className={'inputBox'}
        />
        <label className="errorLabel">{emailError}</label>
      </div>
      <br />
      <div className={'inputContainer'}>
        <input
          value={password}
          placeholder="Enter your password here"
          onChange={(ev) => setPassword(ev.target.value)}
          className={'inputBox'}
        />
        <label className="errorLabel">{passwordError}</label>
      </div>
      <br />
      <div className={'inputContainer'}>
        <input className={'inputButton'} type="button" onClick={onButtonClick} value={'Log in'} />
      </div>
      <br />

      {/* Show login error message if any */}
      {loginError && <div className="errorMessage">{loginError}</div>}

      {/* Add Sign Up link */}
      <div className="signupLink">
        <p>
          Don't have an account?{' '}
          <Link to="/register">Sign Up</Link>
        </p>
      </div>
    </div>
  )
}

export default Login