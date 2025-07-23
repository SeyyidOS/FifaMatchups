from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel

class ClubBase(BaseModel):
    name: str
    tier: int

class ClubCreate(ClubBase):
    pass

class ClubRead(ClubBase):
    id: int
    model_config = dict(from_attributes=True)

class PlayerBase(BaseModel):
    username: str

class PlayerCreate(PlayerBase):
    pass

class PlayerRead(PlayerBase):
    id: int
    model_config = dict(from_attributes=True)

class MatchPlayerCreate(BaseModel):
    player_id: int
    team: int

class MatchCreate(BaseModel):
    team_a_club_id: int
    team_b_club_id: int
    team_a_score: int
    team_b_score: int
    players: List[MatchPlayerCreate]

class MatchPlayerRead(BaseModel):
    player: PlayerRead
    team: int
    model_config = dict(from_attributes=True)

class MatchRead(BaseModel):
    id: int
    date: datetime
    team_a_club: ClubRead
    team_b_club: ClubRead
    team_a_score: int
    team_b_score: int
    players: List[MatchPlayerRead]
    model_config = dict(from_attributes=True)

class LeaderboardEntry(BaseModel):
    name: str
    matches: int
    wins: int
    losses: int
    draws: int
    goals_for: int
    goals_against: int
    win_rate: float
