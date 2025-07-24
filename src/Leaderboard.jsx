import React, { useEffect, useState } from "react";

const API = "https://fifa-backend-1007444302360.us-central1.run.app";

export default function Leaderboard() {
  const [individual, setIndividual] = useState([]);
  const [teams, setTeams] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const indRes = await fetch(`${API}/leaderboard/individual`);
      if (indRes.ok) {
        setIndividual(await indRes.json());
      }
      const teamRes = await fetch(`${API}/leaderboard/team`);
      if (teamRes.ok) {
        const data = await teamRes.json();
        const filtered = data.filter((e) => e.name.split(" + ").length === 2);
        setTeams(filtered);
      }
    };
    fetchData();
  }, []);

  const renderTable = (entries) => (
    <table className="leaderboard-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Matches</th>
          <th>Wins</th>
          <th>Losses</th>
          <th>Draws</th>
          <th>Goals For</th>
          <th>Goals Against</th>
          <th>Win %</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((e) => (
          <tr key={e.name}>
            <td>{e.name}</td>
            <td>{e.matches}</td>
            <td>{e.wins}</td>
            <td>{e.losses}</td>
            <td>{e.draws}</td>
            <td>{e.goals_for}</td>
            <td>{e.goals_against}</td>
            <td>{e.win_rate.toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );

  return (
    <div className="App">
      <h1>Leaderboard</h1>
      <section>
        <h2>Individual</h2>
        {renderTable(individual)}
      </section>
      <section>
        <h2>Teams of Two</h2>
        {renderTable(teams)}
      </section>
    </div>
  );
}
