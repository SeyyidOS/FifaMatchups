from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from collections import defaultdict

from . import models, schemas
from .database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FIFA Matchup Generator")

# Allow frontend applications (e.g. Vite dev server) to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Predefined clubs with tiers
DEFAULT_CLUBS = {
    1: ["Real Madrid", "PSG"],
    2: ["Chelsea", "Liverpool"],
}

# Simple token used to authorize admin actions
ADMIN_TOKEN = "secret"

def admin_required(x_admin_token: str | None = Header(default=None)):
    """Dependency to verify admin token."""
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin credentials required")

@app.on_event("startup")
def populate_clubs():
    db = next(get_db())
    for tier, clubs in DEFAULT_CLUBS.items():
        for name in clubs:
            if not db.query(models.Club).filter_by(name=name).first():
                db.add(models.Club(name=name, tier=tier))
    db.commit()

@app.get("/clubs", response_model=dict)
def get_clubs(tier: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Club)
    if tier is not None:
        query = query.filter(models.Club.tier == tier)
    clubs = query.all()
    by_tier = defaultdict(list)
    for c in clubs:
        by_tier[c.tier].append(schemas.ClubRead.from_orm(c))
    return {tier: [club.model_dump() for club in clubs] for tier, clubs in by_tier.items()}

@app.post("/players", response_model=schemas.PlayerRead)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = models.Player(username=player.username)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/players", response_model=list[schemas.PlayerRead])
def list_players(db: Session = Depends(get_db)):
    return db.query(models.Player).order_by(models.Player.username).all()

@app.post("/matches", response_model=schemas.MatchRead)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    db_match = models.Match(
        team_a_club_id=match.team_a_club_id,
        team_b_club_id=match.team_b_club_id,
        team_a_score=match.team_a_score,
        team_b_score=match.team_b_score,
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    # players
    for mp in match.players:
        db_mp = models.MatchPlayer(match_id=db_match.id, player_id=mp.player_id, team=mp.team)
        db.add(db_mp)
    db.commit()
    db.refresh(db_match)
    return db_match

@app.get("/matches", response_model=list[schemas.MatchRead])
def list_matches(db: Session = Depends(get_db), user: int | None = None, club: int | None = None):
    query = db.query(models.Match)
    if club:
        query = query.filter((models.Match.team_a_club_id == club) | (models.Match.team_b_club_id == club))
    matches = query.order_by(models.Match.date.desc()).all()
    result = []
    for m in matches:
        if user:
            if not any(mp.player_id == user for mp in m.players):
                continue
        result.append(m)
    return result

@app.get("/leaderboard/individual", response_model=list[schemas.LeaderboardEntry])
def individual_leaderboard(db: Session = Depends(get_db)):
    players = db.query(models.Player).all()
    entries = []
    for p in players:
        matches = db.query(models.MatchPlayer).filter_by(player_id=p.id).all()
        stats = {
            "matches": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "goals_for": 0,
            "goals_against": 0,
        }
        for mp in matches:
            stats["matches"] += 1
            match = db.query(models.Match).get(mp.match_id)
            if mp.team == 1:
                gf = match.team_a_score
                ga = match.team_b_score
            else:
                gf = match.team_b_score
                ga = match.team_a_score
            stats["goals_for"] += gf
            stats["goals_against"] += ga
            if gf > ga:
                stats["wins"] += 1
            elif gf < ga:
                stats["losses"] += 1
            else:
                stats["draws"] += 1
        win_rate = stats["wins"] / stats["matches"] * 100 if stats["matches"] else 0
        entries.append(schemas.LeaderboardEntry(name=p.username, win_rate=win_rate, **stats))
    entries.sort(key=lambda e: e.win_rate, reverse=True)
    return entries

@app.get("/leaderboard/team", response_model=list[schemas.LeaderboardEntry])
def team_leaderboard(db: Session = Depends(get_db)):
    # compute team combinations
    combos: dict[tuple[int, ...], dict] = {}
    matches = db.query(models.Match).all()
    for m in matches:
        team_players = {1: [], 2: []}
        for mp in m.players:
            team_players[mp.team].append(mp.player_id)
        for team, players in team_players.items():
            key = tuple(sorted(players))
            stats = combos.setdefault(key, {
                'matches': 0, 'wins': 0, 'losses': 0,
                'draws': 0, 'goals_for': 0, 'goals_against': 0,
            })
            stats['matches'] += 1
            if team == 1:
                gf = m.team_a_score
                ga = m.team_b_score
            else:
                gf = m.team_b_score
                ga = m.team_a_score
            stats['goals_for'] += gf
            stats['goals_against'] += ga
            if gf > ga:
                stats['wins'] += 1
            elif gf < ga:
                stats['losses'] += 1
            else:
                stats['draws'] += 1
    results = []
    for players, stats in combos.items():
        names = db.query(models.Player).filter(models.Player.id.in_(players)).all()
        name = ' + '.join(p.username for p in names)
        win_rate = stats['wins'] / stats['matches'] * 100 if stats['matches'] else 0
        results.append(schemas.LeaderboardEntry(name=name, win_rate=win_rate, **stats))
    results.sort(key=lambda e: e.win_rate, reverse=True)
    return results


@app.delete("/players/{player_id}", dependencies=[Depends(admin_required)])
def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).get(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    db.query(models.MatchPlayer).filter_by(player_id=player_id).delete()
    db.delete(player)
    db.commit()
    return {"detail": "Player deleted"}


@app.delete("/matches/{match_id}", dependencies=[Depends(admin_required)])
def delete_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(models.Match).get(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.query(models.MatchPlayer).filter_by(match_id=match_id).delete()
    db.delete(match)
    db.commit()
    return {"detail": "Match deleted"}
