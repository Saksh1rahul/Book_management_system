import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import { clearAuthData, getStoredUser, isAuthenticated } from './auth';

const Nav = () => {
  const navigate = useNavigate();
  const authenticated = isAuthenticated();

  const handleLogout = () => {
    clearAuthData();
    navigate('/login');
  };

  return (
    <div className='d-flex justify-content-between align-items-center px-4 py-3 shadow-sm'>
      <Link to='/' className='fs-4 fw-bold text-decoration-none text-dark'>Book Management System</Link>
      <div>
        {!authenticated ? (
          <>
            <Link to='/login' className='btn btn-outline-primary btn-sm me-2'>Login</Link>
            <Link to='/register' className='btn btn-outline-secondary btn-sm'>Register</Link>
          </>
        ) : (
          <>
            <span className='me-3'>Hello, {getStoredUser()}</span>
            <button className='btn btn-outline-danger btn-sm' onClick={handleLogout}>Logout</button>
          </>
        )}
      </div>
    </div>
  );
};

export default Nav;