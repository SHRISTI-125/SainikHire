import React, { useState} from "react";
import { useLocation, Link } from "react-router-dom";
import {useEffect} from "react"

function SearchPage() {
  const location = useLocation();
  const initialInput = location.state?.input || "";
  const initialResults = location.state?.results || [];

  const [input, setInput] = useState(initialInput);
  const [results, setResults] = useState(initialResults);
  const [loading, setLoading] = useState(false);
  const [hover, setHover] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    const response = await fetch("http://127.0.0.1:5000/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_input: input }),
    });

    const data = await response.json();
    setResults(data);
    setLoading(false);
    //e.stopPropagation();
  };

  useEffect(() => {
    sessionStorage.setItem("searchInput", input);
    sessionStorage.setItem("searchResults", JSON.stringify(results));
  }, [input, results]);


  return (
    <div style={{ minHeight: '100vh', width: '100vw', backgroundColor: '#F3F0EE', paddingTop: '50px', position: 'relative' }}>
      <div style={{ position: 'absolute', top: 20, left: 20 }}>
        <img src="/img/logo2.png" height="60px" width="118px" style={{ borderRadius: "5%" }} alt="Logo" />
      </div>

      <form
        onSubmit={handleSearch}
        className="d-flex flex-column align-items-center"
        style={{ maxWidth: '600px', margin: '0 auto' }}
      >
        <div className="input-group shadow rounded-pill w-100 align-items-center">
          <input
            type="text"
            className="form-control rounded-start-pill py-2 px-3"
            placeholder="Write your skills and education"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            className="btn btn-primary rounded-end-pill px-4"
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
            style={{
              backgroundColor: hover ? '#f9f050' : '#9269ec',
              borderColor: '#e7defa',
            }}
          >
            🔦
          </button>
        </div>
      </form>
      <div className="d-flex justify-content-center mt-3">
      <Link to="/alljob" className="btn ms-2" style={{ borderRadius: "0px", borderColor: "white" }}>All</Link>
      <a href="#" className="btn ms-2" style={{ borderRadius: "0px", borderColor: "white" }}>ChatBot</a>
        <Link to="/recommendation" className="btn ms-2" style={{ borderRadius: "0px", borderColor: "white" }}>Job Recommendations</Link>
        <a href="#" className="btn ms-2" style={{ borderRadius: "0px", borderColor: "white" }}>CV Generation</a>
        <Link to="/jobupdate" className="btn ms-2" style={{ borderRadius: "0px", borderColor: "white" }}>What to post job?</Link>
        
      </div>

      {loading && (
        <div className="text-center mt-4">
          <p>Searching jobs...</p>
        </div>
      )}
      {!loading && results.length > 0 && (
        <div className="container mt-5">
          {results.map((job, index) => (
            <div key={index} className="card p-3 my-3"
            style={{ backgroundColor: '#F5F5F5', borderRadius: '0px', borderColor: '#e7defa' }}>
              <h5>
                <Link to={`/job/${job._id}`} style={{ textDecoration: 'none', color: '#5e35b1' }}>
                  {job.title}
                </Link>
              </h5>
              <p>{job.description?.slice(0, 500)}...</p>
            </div>
          ))}
        </div>
      )}

      {!loading && results.length === 0 && input !== "" && (
        <div className="text-center mt-4">
          <p className="text-danger">Job not detected</p>
        </div>
      )}
    </div>
  );
}

export default SearchPage;
