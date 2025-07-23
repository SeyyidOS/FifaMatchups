import { useEffect, useState } from 'react'
import './App.css'

const API = 'http://127.0.0.1:8000'

function App() {
  const [clubs, setClubs] = useState({})
  const [players, setPlayers] = useState([])
  const [matches, setMatches] = useState([])
  const [selectedTier, setSelectedTier] = useState(null)
  const [tierClubs, setTierClubs] = useState([])
  const [username, setUsername] = useState('')
  const [form, setForm] = useState({
    teamAClub: '',
    teamBClub: '',
    teamAScore: 0,
    teamBScore: 0,
    teamAPlayers: '',
    teamBPlayers: '',
  })

  const fetchData = async () => {
    const clubsRes = await fetch(`${API}/clubs`)
    setClubs(await clubsRes.json())
    const playersRes = await fetch(`${API}/players`)
    if (playersRes.ok) setPlayers(await playersRes.json())
    const matchesRes = await fetch(`${API}/matches`)
    if (matchesRes.ok) setMatches(await matchesRes.json())
  }

  const randomizeTier = async () => {
    const tiers = Object.keys(clubs)
    if (tiers.length === 0) return
    const randTier = tiers[Math.floor(Math.random() * tiers.length)]
    setSelectedTier(parseInt(randTier))
    const res = await fetch(`${API}/clubs?tier=${randTier}`)
    if (res.ok) {
      const data = await res.json()
      setTierClubs(data[randTier] || [])
      setForm({ ...form, teamAClub: '', teamBClub: '' })
    }
  }


  useEffect(() => {
    fetchData()
  }, [])

  const addPlayer = async () => {
    const res = await fetch(`${API}/players`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username }),
    })
    if (res.ok) {
      setUsername('')
      fetchData()
    }
  }

  const createMatch = async () => {
    const body = {
      team_a_club_id: parseInt(form.teamAClub),
      team_b_club_id: parseInt(form.teamBClub),
      team_a_score: parseInt(form.teamAScore),
      team_b_score: parseInt(form.teamBScore),
      players: [
        ...form.teamAPlayers.split(',').map((id) => ({ player_id: parseInt(id), team: 1 })),
        ...form.teamBPlayers.split(',').map((id) => ({ player_id: parseInt(id), team: 2 })),
      ],
    }
    const res = await fetch(`${API}/matches`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (res.ok) {
      setForm({ teamAClub: '', teamBClub: '', teamAScore: 0, teamBScore: 0, teamAPlayers: '', teamBPlayers: '' })
      fetchData()
    } else {
      alert('error creating match')
    }
  }

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

export default App
