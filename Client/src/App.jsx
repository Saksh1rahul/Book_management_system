import React, { useEffect } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Books from './Books';
import CreateBook from './CreateBook';
import Login from './Login';
import Nav from './Nav';
import Register from './Register';
import UpdateBook from './UpdateBook';
import { isAuthenticated } from './auth';

function ProtectedRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to='/login' replace />;
}

function App() {
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
  }, []);

  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path='/' element={<Books />} />
        <Route path='/login' element={<Login />} />
        <Route path='/register' element={<Register />} />
        <Route path='/create' element={<ProtectedRoute><CreateBook /></ProtectedRoute>} />
        <Route path='/update' element={<ProtectedRoute><UpdateBook /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
