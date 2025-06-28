import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function EntryPage() {
  const [input, setInput] = useState("");
  const [hover, setHover] = useState(false);
  const navigate = useNavigate();

  const search = async (e) => {
    e.preventDefault();
    const response = await fetch("http://127.0.0.1:5000/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_input: input }),
    });

    const data = await response.json();
    navigate("/searching", {
      state: { input, results: data },
    });
  };

  return (
    <div className="d-flex justify-content-center" style={{ height: '100vh', width: '100vw', backgroundColor:'#F3F0EE' }}>
      <form style={{ width: '500px', padding:"150px 0px 0px 0px"}} onSubmit={search}>
        <div className='d-flex justify-content-center'>
          <img src="/img/logo.png" height="100px" width="120px" style={{ borderRadius:"50%" }} />
        </div>
        <div className="input-group shadow rounded-pill">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="form-control rounded-start-pill py-2 px-3"
            placeholder="Search Jobs with SainikHire"
          />
          <button
            type="submit"
            className="btn btn-primary rounded-end-pill px-4"
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
            style={{
              backgroundColor: hover ? '#f6cefc' : '#9269ec',
              borderColor: '#e7defa',
            }}
          >
            🔦
          </button>
        </div>
      </form>
    </div>
  );
}

export default EntryPage;
