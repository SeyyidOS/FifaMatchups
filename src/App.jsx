import { useEffect, useState } from "react";
import { HashRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./Home.jsx";
import AdminPage from "./AdminPage.jsx";
import Leaderboard from "./Leaderboard.jsx";
import "./App.css";

const API = "https://fifa-backend-1007444302360.us-central1.run.app";

function App() {
  const [clubs, setClubs] = useState({});
  const [players, setPlayers] = useState([]);
  const [matches, setMatches] = useState([]);
  const [selectedTier, setSelectedTier] = useState(null);
  const [tierClubs, setTierClubs] = useState([]);
  const [username, setUsername] = useState("");
  const [adminToken, setAdminToken] = useState("");
  const [creatingMatch, setCreatingMatch] = useState(false);
  const [addingPlayer, setAddingPlayer] = useState(false);
  const [randomizingTier, setRandomizingTier] = useState(false);
  const [deletingPlayerIds, setDeletingPlayerIds] = useState([]);
  const [deletingMatchIds, setDeletingMatchIds] = useState([]);
  const [form, setForm] = useState({
    teamAClub: "",
    teamBClub: "",
    teamAScore: 0,
    teamBScore: 0,
    teamAPlayers: "",
    teamBPlayers: "",
  });

  const fetchData = async () => {
    const clubsRes = await fetch(`${API}/clubs`);
    setClubs(await clubsRes.json());
    const playersRes = await fetch(`${API}/players`);
    if (playersRes.ok) setPlayers(await playersRes.json());
    const matchesRes = await fetch(`${API}/matches`);
    if (matchesRes.ok) setMatches(await matchesRes.json());
  };

  const randomizeTier = async () => {
    if (randomizingTier) return;
    const tiers = Object.keys(clubs);
    if (tiers.length === 0) return;
    setRandomizingTier(true);
    const randTier = tiers[Math.floor(Math.random() * tiers.length)];
    setSelectedTier(parseInt(randTier));
    const res = await fetch(`${API}/clubs?tier=${randTier}`);
    if (res.ok) {
      const data = await res.json();
      setTierClubs(data[randTier] || []);
      setForm({ ...form, teamAClub: "", teamBClub: "" });
    }
    setRandomizingTier(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const addPlayer = async () => {
    if (addingPlayer) return;
    setAddingPlayer(true);
    const res = await fetch(`${API}/players`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username }),
    });
    setAddingPlayer(false);
    if (res.ok) {
      setUsername("");
      fetchData();
    } else {
      alert("failed to add player");
    }
  };

  const createMatch = async () => {
    if (creatingMatch) return;
    setCreatingMatch(true);
    const body = {
      team_a_club_id: parseInt(form.teamAClub),
      team_b_club_id: parseInt(form.teamBClub),
      team_a_score: parseInt(form.teamAScore),
      team_b_score: parseInt(form.teamBScore),
      players: [
        ...form.teamAPlayers
          .split(",")
          .map((id) => ({ player_id: parseInt(id), team: 1 })),
        ...form.teamBPlayers
          .split(",")
          .map((id) => ({ player_id: parseInt(id), team: 2 })),
      ],
    };
    const res = await fetch(`${API}/matches`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    setCreatingMatch(false);
    if (res.ok) {
      setForm({
        teamAClub: "",
        teamBClub: "",
        teamAScore: 0,
        teamBScore: 0,
        teamAPlayers: "",
        teamBPlayers: "",
      });
      fetchData();
    } else {
      alert("error creating match");
    }
  };

  const deletePlayer = async (id) => {
    if (deletingPlayerIds.includes(id)) return;
    setDeletingPlayerIds((ids) => [...ids, id]);
    const res = await fetch(`${API}/players/${id}`, {
      method: "DELETE",
      headers: { "X-Admin-Token": adminToken },
    });
    setDeletingPlayerIds((ids) => ids.filter((i) => i !== id));
    if (res.ok) {
      fetchData();
    } else {
      alert("failed to delete player");
    }
  };

  const deleteMatch = async (id) => {
    if (deletingMatchIds.includes(id)) return;
    setDeletingMatchIds((ids) => [...ids, id]);
    const res = await fetch(`${API}/matches/${id}`, {
      method: "DELETE",
      headers: { "X-Admin-Token": adminToken },
    });
    setDeletingMatchIds((ids) => ids.filter((i) => i !== id));
    if (res.ok) {
      fetchData();
    } else {
      alert("failed to delete match");
    }
  };

  return (
    <Router>
      <nav>
        <Link to="/">Home</Link> | <Link to="/admin">Admin</Link> |{" "}
        <Link to="/leaderboard">Leaderboard</Link>
      </nav>
      <Routes>
        <Route
          path="/"
          element={
            <Home
              username={username}
              setUsername={setUsername}
              players={players}
              addPlayer={addPlayer}
              addingPlayer={addingPlayer}
              clubs={clubs}
              randomizeTier={randomizeTier}
              randomizingTier={randomizingTier}
              selectedTier={selectedTier}
              tierClubs={tierClubs}
              form={form}
              setForm={setForm}
              createMatch={createMatch}
              creatingMatch={creatingMatch}
              matches={matches}
            />
          }
        />
        <Route
          path="/admin"
          element={
            <AdminPage
              adminToken={adminToken}
              setAdminToken={setAdminToken}
              players={players}
              matches={matches}
              deletePlayer={deletePlayer}
              deleteMatch={deleteMatch}
              deletingPlayerIds={deletingPlayerIds}
              deletingMatchIds={deletingMatchIds}
            />
          }
        />
        <Route path="/leaderboard" element={<Leaderboard />} />
      </Routes>
    </Router>
  );
}

export default App;
