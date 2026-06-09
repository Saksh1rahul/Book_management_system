import axios from 'axios';
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getAuthHeaders } from './auth';

const UpdateBook = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const book = location.state?.book;

    if (!book) {
        navigate('/');
        return null;
    }

    const [values, setValues] = useState({
        publisher: book.publisher,
        name: book.name,
        date: book.date,
        cost: book.cost,
        edition: book.edition || ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        axios.put(`http://localhost:5000/update/${book.id}`, values, { headers: getAuthHeaders() })
            .then(() => navigate('/'))
            .catch(err => {
                console.log(err);
                if (err.response?.status === 401) {
                    navigate('/login');
                }
            });
    };

    return (
        <div className='d-flex align-items-center flex-column mt-3'>
            <h2>Update Book</h2>
            <form className='w-50' onSubmit={handleSubmit}>
                <div className="mb-3 mt-3">
                    <label htmlFor="Publisher" className="form-label">Publisher</label>
                    <input type="text"
                        className="form-control"
                        placeholder="Enter Publisher name"
                        name="publisher"
                        value={values.publisher}
                        onChange={(e) => setValues({ ...values, publisher: e.target.value })}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="Book name" className="form-label">Book name:</label>
                    <input type="text"
                        className="form-control"
                        placeholder="Enter Book name"
                        name="name"
                        value={values.name}
                        onChange={(e) => setValues({ ...values, name: e.target.value })}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="Publish date" className="form-label">Publish Date:</label>
                    <input type="date"
                        className="form-control"
                        name="date"
                        value={values.date}
                        onChange={(e) => setValues({ ...values, date: e.target.value })}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="cost" className="form-label">Cost:</label>
                    <input type="text"
                        className="form-control"
                        placeholder="Rupees"
                        name="cost"
                        value={values.cost}
                        onChange={(e) => setValues({ ...values, cost: e.target.value })}
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="edition" className="form-label">Edition:</label>
                    <input type="text"
                        className="form-control"
                        placeholder="Enter edition (e.g. 2nd edition)"
                        name="edition"
                        value={values.edition}
                        onChange={(e) => setValues({ ...values, edition: e.target.value })}
                    />
                </div>
                <button type="submit" className="btn btn-primary">Update</button>
            </form>
        </div>
    );
};

export default UpdateBook;