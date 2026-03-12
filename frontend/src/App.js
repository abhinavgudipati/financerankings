import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [rankings, setRankings] = useState([]);
  const [startYear, setStartYear] = useState(2018);
  const [endYear, setEndYear] = useState(2024);

  const fetchRankings = async () => {
    const res = await axios.get(
      `http://localhost:8000/rankings?start_year=${startYear}&end_year=${endYear}`
    );
    setRankings(res.data);
  };

  useEffect(() => {
    fetchRankings();
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>FinanceRankings.org</h1>

      <div>
        <input
          type="number"
          value={startYear}
          onChange={(e) => setStartYear(e.target.value)}
        />
        <input
          type="number"
          value={endYear}
          onChange={(e) => setEndYear(e.target.value)}
        />
        <button onClick={fetchRankings}>Update</button>
        <a
          href={`http://localhost:8000/rankings/export?start_year=${startYear}&end_year=${endYear}`}
        >
          Export CSV
        </a>
      </div>

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Institution</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {rankings.map((r, index) => (
            <tr key={index}>
              <td>{index + 1}</td>
              <td>{r.institution}</td>
              <td>{r.score.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;