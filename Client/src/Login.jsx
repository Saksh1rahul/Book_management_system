import axios from 'axios';
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { saveAuthData } from './auth';

const Login = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:5000/login', form)
      .then((res) => {
        saveAuthData(res.data.token, res.data.username);
        navigate('/');
      })
      .catch((err) => {
        setError(err.response?.data?.error || 'Login failed');
      });
  };

  return (
    <div className='d-flex align-items-center flex-column mt-3'>
      <h2>Login</h2>
      <form className='w-50' onSubmit={handleSubmit}>
        {error ? <div className='alert alert-danger'>{error}</div> : null}
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
        <button className='btn btn-primary me-2' type='submit'>Login</button>
        <Link className='btn btn-outline-secondary' to='/register'>Create account</Link>
      </form>
    </div>
  );
};

export default Login;
