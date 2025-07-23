import React from 'react'

export default function AdminPage({
  adminToken,
  setAdminToken,
  players,
  matches,
  deletePlayer,
  deleteMatch,
}) {
  return (
    <div className="App">
      <h1>Admin Panel</h1>
      <input
        value={adminToken}
        onChange={(e) => setAdminToken(e.target.value)}
        placeholder="admin token"
      />
      <h3>Players</h3>
      <ul>
        {players.map((p) => (
          <li key={p.id}>
            {p.id}: {p.username}{' '}
            <button className="danger" onClick={() => deletePlayer(p.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
      <h3>Matches</h3>
      <ul>
        {matches.map((m) => (
          <li key={m.id}>
            {m.team_a_club.name} vs {m.team_b_club.name}{' '}
            <button className="danger" onClick={() => deleteMatch(m.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
