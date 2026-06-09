import axios from 'axios';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Register = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/register', form)
      .then(() => {
        setMessage('Registration successful. Please login.');
        setTimeout(() => navigate('/login'), 800);
      })
      .catch((err) => {
        setError(err.response?.data?.error || 'Registration failed');
      });
  };

  return (
    <div className='d-flex align-items-center flex-column mt-3'>
      <h2>Create account</h2>
      <form className='w-50' onSubmit={handleSubmit}>
        {error ? <div className='alert alert-danger'>{error}</div> : null}
        {message ? <div className='alert alert-success'>{message}</div> : null}
        <div className='mb-3'>
          <label className='form-label'>Username</label>
          <input
            type='text'
            className='form-control'
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />
        </div>
        <div className='mb-3'>
          <label className='form-label'>Password</label>
          <input
            type='password'
            className='form-control'
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>
        <button className='btn btn-primary me-2' type='submit'>Register</button>
        <Link className='btn btn-outline-secondary' to='/login'>Back to login</Link>
      </form>
    </div>
  );
};

export default Register;
