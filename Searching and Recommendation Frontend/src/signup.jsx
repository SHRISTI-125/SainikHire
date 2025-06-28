import React, { useState } from 'react';
import axios from 'axios';

function Signup() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [education, setEducation] = useState('');
    const [skills, setSkills] = useState('');
    const [rank, setRank] = useState('');
    const [location, setLocation] = useState('');
    const [formErrors, setFormErrors] = useState({});
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setFormErrors({});
        setSuccess('');

        const data = { name, email, password, education, skills, rank, location };

        try {
            const res = await axios.post('http://localhost:5000/signup', data);
            if (res.status === 200) {
                setSuccess('Signup successful!');
                setName('');
                setEmail('');
                setPassword('');
                setEducation('');
                setSkills('');
                setRank('');
                setLocation('');
            }
        } catch (err) {
            if (err.response && err.response.data.errors) {
                setFormErrors(err.response.data.errors);
            } else {
                console.error('Signup error:', err);
            }
        }
    };

    return (
        <div className="d-flex justify-content-center align-items-center vh-100"
            style={{ background: 'linear-gradient(to bottom, #f5eff9, rgb(185, 230, 194))' }}>
            
            <div className="bg-white p-4 rounded shadow-lg w-25">
            {success && (
              <div className="alert alert-success">
                {success} <br/><a href="/recommendation" className="recommend-page">Recommendation Page</a>
              </div>
            )}
                <h2 className="text-center mb-4">Information</h2>
                <form onSubmit={handleSubmit}>
                    <Input label="Name" value={name} setValue={setName} error={formErrors.name} />
                    <Input label="Rank" value={rank} setValue={setRank} error={formErrors.rank} />
                    <Input label="Educational Qualification" value={education} setValue={setEducation} error={formErrors.education} />
                    <Input label="Skills" value={skills} setValue={setSkills} error={formErrors.skills} />
                    <Input label="Location" value={location} setValue={setLocation} error={formErrors.location} />
                    <Input label="Email" type="email" value={email} setValue={setEmail} error={formErrors.email} />
                    <Input label="Password" type="password" value={password} setValue={setPassword} error={formErrors.password} />

                    <button type="submit" className="btn btn-success w-100 rounded-0">Submit</button>
                </form>
            </div>
        </div>
    );
}

function Input({ label, type = 'text', value, setValue, error }) {
    return (
        <div className="mb-3">
            <label className="form-label"><strong>{label}</strong></label>
            <input
                type={type}
                value={value}
                placeholder={`Enter your ${label}`}
                className={`form-control rounded-0 ${error ? 'is-invalid' : ''}`}
                onChange={(e) => setValue(e.target.value)}
            />
            {error && <div className="invalid-feedback">{error}</div>}
        </div>
    );
}

export default Signup;
