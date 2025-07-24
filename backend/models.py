from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Club(Base):
    __tablename__ = "clubs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    tier = Column(Integer, nullable=False)


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    team_a_club_id = Column(Integer, ForeignKey("clubs.id"))
    team_b_club_id = Column(Integer, ForeignKey("clubs.id"))
    team_a_score = Column(Integer)
    team_b_score = Column(Integer)

    team_a_club = relationship("Club", foreign_keys=[team_a_club_id])
    team_b_club = relationship("Club", foreign_keys=[team_b_club_id])
    players = relationship("MatchPlayer", back_populates="match")


class MatchPlayer(Base):
    __tablename__ = "match_players"
    match_id = Column(Integer, ForeignKey("matches.id"), primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    team = Column(Integer, nullable=False)  # 1 or 2

    match = relationship("Match", back_populates="players")
    player = relationship("Player")
