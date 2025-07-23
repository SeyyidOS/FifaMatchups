from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict

from . import models, schemas
from .database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FIFA Matchup Generator")

# Predefined clubs with tiers
DEFAULT_CLUBS = {
    1: ["Real Madrid", "PSG"],
    2: ["Chelsea", "Liverpool"],
}

@app.on_event("startup")
def populate_clubs():
    db = next(get_db())
    for tier, clubs in DEFAULT_CLUBS.items():
        for name in clubs:
            if not db.query(models.Club).filter_by(name=name).first():
                db.add(models.Club(name=name, tier=tier))
    db.commit()

@app.get("/clubs", response_model=dict)
def get_clubs(db: Session = Depends(get_db)):
    clubs = db.query(models.Club).all()
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
