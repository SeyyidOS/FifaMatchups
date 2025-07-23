import React from 'react'

export default function Home({
  username,
  setUsername,
  players,
  addPlayer,
  clubs,
  randomizeTier,
  selectedTier,
  tierClubs,
  form,
  setForm,
  createMatch,
  matches,
}) {
  return (
    <div className="App">
      <h1>FIFA Matchups</h1>
      <section>
        <h2>Add Player</h2>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="username" />
        <button onClick={addPlayer}>Add</button>
        <ul>
          {players.map((p) => (
            <li key={p.id}>{p.id}: {p.username}</li>
          ))}
        </ul>
      </section>
      <section>
        <h2>Create Match</h2>
        <button onClick={randomizeTier}>Random Tier</button>
        {selectedTier && <div>Selected Tier: {selectedTier}</div>}
        <div>
          <label>Team A Club:</label>
          <select value={form.teamAClub} onChange={(e) => setForm({ ...form, teamAClub: e.target.value })}>
            <option value="">select</option>
            {(tierClubs.length ? tierClubs : Object.values(clubs).flat()).map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Team B Club:</label>
          <select value={form.teamBClub} onChange={(e) => setForm({ ...form, teamBClub: e.target.value })}>
            <option value="">select</option>
            {(tierClubs.length ? tierClubs : Object.values(clubs).flat()).map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Team A Players (ids comma separated):</label>
          <input value={form.teamAPlayers} onChange={(e) => setForm({ ...form, teamAPlayers: e.target.value })} />
        </div>
        <div>
          <label>Team B Players (ids comma separated):</label>
          <input value={form.teamBPlayers} onChange={(e) => setForm({ ...form, teamBPlayers: e.target.value })} />
        </div>
        <div className="score-inputs">
          <div>
            <label>Score A:</label>
            <input
              type="number"
              value={form.teamAScore}
              onChange={(e) => setForm({ ...form, teamAScore: e.target.value })}
            />
          </div>
          <div>
            <label>Score B:</label>
            <input
              type="number"
              value={form.teamBScore}
              onChange={(e) => setForm({ ...form, teamBScore: e.target.value })}
            />
          </div>
        </div>
        <button onClick={createMatch}>Submit Match</button>
      </section>
      <section>
        <h2>Matches</h2>
        <ul>
          {matches.map((m) => {
            const teamAPlayers = m.players
              .filter((mp) => mp.team === 1)
              .map((mp) => mp.player.username)
              .join(', ')
            const teamBPlayers = m.players
              .filter((mp) => mp.team === 2)
              .map((mp) => mp.player.username)
              .join(', ')
            return (
              <li key={m.id} className="match-item">
                <div className="match-header">{new Date(m.date).toLocaleString()}</div>
                <div className="match-content">
                  <div className="team-info">
                    <div className="club-name">{m.team_a_club.name}</div>
                    <div className="players">{teamAPlayers}</div>
                  </div>
                  <div className="score">
                    {m.team_a_score} - {m.team_b_score}
                  </div>
                  <div className="team-info">
                    <div className="club-name">{m.team_b_club.name}</div>
                    <div className="players">{teamBPlayers}</div>
                  </div>
                </div>
              </li>
            )
          })}
        </ul>
      </section>
    </div>
  )
}
