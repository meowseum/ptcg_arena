"""
PTCG ELO Rating Calculator
Ported from PTCG_Stat/elo_calculator.py - DO NOT MODIFY ORIGINAL
"""
from collections import defaultdict
from datetime import datetime
from typing import Dict, Tuple, List
from app.models import db, Player, Match, Tournament, TournamentPlayer, ELOHistory, Deck

# ELO Parameters
STARTING_ELO = 1500.0
K_FACTOR_NEW = 40      # < 15 games
K_FACTOR_ESTABLISHED = 24  # 15-29 games
K_FACTOR_VETERAN = 16  # 30+ games
DOUBLE_LOSS_PENALTY = 8
DECK_K_FACTOR = 24  # Fixed K-factor for decks


def get_k_factor(games_played: int) -> int:
    """Determine K-factor based on experience level"""
    if games_played < 15:
        return K_FACTOR_NEW
    elif games_played < 30:
        return K_FACTOR_ESTABLISHED
    else:
        return K_FACTOR_VETERAN


def expected_score(rating_a: float, rating_b: float) -> float:
    """Calculate expected score for player A against player B"""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


class ELOCalculator:
    """Calculate and update ELO ratings for players and decks"""

    def __init__(self):
        self.player_ratings = {}
        self.player_games = {}
        self.player_wins = {}
        self.player_losses = {}
        self.player_peak_elo = {}

    def calculate_match_elo(self, match: Match) -> Tuple[float, float]:
        """
        Calculate ELO changes for a single match.
        Returns: (p1_elo_change, p2_elo_change)
        """
        tp1 = match.player1
        tp2 = match.player2

        if not tp2:  # Bye match
            return 0.0, 0.0

        player1 = tp1.player
        player2 = tp2.player

        # Initialize ratings if needed
        if player1.id not in self.player_ratings:
            self.player_ratings[player1.id] = player1.elo
            self.player_games[player1.id] = player1.games_played
            self.player_wins[player1.id] = player1.wins
            self.player_losses[player1.id] = player1.losses
            self.player_peak_elo[player1.id] = player1.peak_elo

        if player2.id not in self.player_ratings:
            self.player_ratings[player2.id] = player2.elo
            self.player_games[player2.id] = player2.games_played
            self.player_wins[player2.id] = player2.wins
            self.player_losses[player2.id] = player2.losses
            self.player_peak_elo[player2.id] = player2.peak_elo

        # Get current ratings
        p1_elo_before = self.player_ratings[player1.id]
        p2_elo_before = self.player_ratings[player2.id]

        # Handle double loss
        if match.result == 'double_loss':
            self.player_ratings[player1.id] -= DOUBLE_LOSS_PENALTY
            self.player_ratings[player2.id] -= DOUBLE_LOSS_PENALTY
            self.player_games[player1.id] += 1
            self.player_games[player2.id] += 1
            self.player_losses[player1.id] += 1
            self.player_losses[player2.id] += 1
            return -DOUBLE_LOSS_PENALTY, -DOUBLE_LOSS_PENALTY

        # Normal match
        p1_k = get_k_factor(self.player_games[player1.id])
        p2_k = get_k_factor(self.player_games[player2.id])

        # Calculate expected scores
        p1_expected = expected_score(p1_elo_before, p2_elo_before)
        p2_expected = 1 - p1_expected

        # Determine actual scores
        if match.result == 'player1':
            p1_actual = 1.0
            p2_actual = 0.0
            self.player_wins[player1.id] += 1
            self.player_losses[player2.id] += 1
        elif match.result == 'player2':
            p1_actual = 0.0
            p2_actual = 1.0
            self.player_wins[player2.id] += 1
            self.player_losses[player1.id] += 1
        elif match.result == 'draw':
            p1_actual = 0.5
            p2_actual = 0.5
        else:
            return 0.0, 0.0

        # Calculate ELO changes
        p1_change = p1_k * (p1_actual - p1_expected)
        p2_change = p2_k * (p2_actual - p2_expected)

        # Update ratings
        self.player_ratings[player1.id] += p1_change
        self.player_ratings[player2.id] += p2_change

        # Update peak ELO
        self.player_peak_elo[player1.id] = max(self.player_peak_elo[player1.id], self.player_ratings[player1.id])
        self.player_peak_elo[player2.id] = max(self.player_peak_elo[player2.id], self.player_ratings[player2.id])

        # Increment game counts
        self.player_games[player1.id] += 1
        self.player_games[player2.id] += 1

        return p1_change, p2_change

    def update_tournament_elo(self, tournament: Tournament):
        """
        Calculate and update ELO for all players in a completed tournament.
        Creates ELOHistory records for tracking.
        """
        # Get all matches for this tournament, ordered chronologically
        matches = Match.query.filter_by(tournament_id=tournament.id)\
            .filter(Match.result.isnot(None))\
            .order_by(Match.round_number, Match.id).all()

        # Reset calculator state
        self.player_ratings = {}
        self.player_games = {}
        self.player_wins = {}
        self.player_losses = {}
        self.player_peak_elo = {}

        # Calculate ELO changes for each match
        for match in matches:
            if match.result == 'bye':
                continue

            tp1 = match.player1
            tp2 = match.player2

            if not tp2:
                continue

            player1 = tp1.player
            player2 = tp2.player

            # Get ELO before this match
            p1_elo_before = self.player_ratings.get(player1.id, player1.elo)
            p2_elo_before = self.player_ratings.get(player2.id, player2.elo)

            # Calculate changes
            p1_change, p2_change = self.calculate_match_elo(match)

            # Get ELO after
            p1_elo_after = self.player_ratings[player1.id]
            p2_elo_after = self.player_ratings[player2.id]

            # Create history records
            history1 = ELOHistory(
                player_id=player1.id,
                match_id=match.id,
                tournament_id=tournament.id,
                elo_before=p1_elo_before,
                elo_after=p1_elo_after,
                elo_change=p1_change
            )
            history2 = ELOHistory(
                player_id=player2.id,
                match_id=match.id,
                tournament_id=tournament.id,
                elo_before=p2_elo_before,
                elo_after=p2_elo_after,
                elo_change=p2_change
            )
            db.session.add(history1)
            db.session.add(history2)

        # Update final player ratings in database
        for player_id, final_elo in self.player_ratings.items():
            player = Player.query.get(player_id)
            if player:
                player.elo = final_elo
                player.peak_elo = self.player_peak_elo[player_id]
                player.games_played = self.player_games[player_id]
                player.wins = self.player_wins[player_id]
                player.losses = self.player_losses[player_id]

        db.session.commit()

    def calculate_deck_elo(self, tournament: Tournament):
        """
        Calculate and update ELO for decks used in a tournament.
        """
        # Get all matches with deck data
        matches = Match.query.filter_by(tournament_id=tournament.id)\
            .filter(Match.result.isnot(None))\
            .join(TournamentPlayer, Match.player1_id == TournamentPlayer.id)\
            .filter(TournamentPlayer.deck_id.isnot(None))\
            .order_by(Match.round_number).all()

        deck_ratings = {}
        deck_games = {}
        deck_wins = {}

        for match in matches:
            if match.result in ['bye', 'double_loss']:
                continue

            tp1 = match.player1
            tp2 = match.player2

            if not tp2 or not tp1.deck_id or not tp2.deck_id:
                continue

            deck1 = tp1.deck
            deck2 = tp2.deck

            # Initialize deck ratings
            if deck1.id not in deck_ratings:
                deck_ratings[deck1.id] = deck1.elo
                deck_games[deck1.id] = deck1.games_played
                deck_wins[deck1.id] = deck1.wins

            if deck2.id not in deck_ratings:
                deck_ratings[deck2.id] = deck2.elo
                deck_games[deck2.id] = deck2.games_played
                deck_wins[deck2.id] = deck2.wins

            # Get current ratings
            deck1_elo = deck_ratings[deck1.id]
            deck2_elo = deck_ratings[deck2.id]

            # Calculate expected score
            deck1_expected = expected_score(deck1_elo, deck2_elo)

            # Determine actual score
            if match.result == 'player1':
                deck1_actual = 1.0
                deck_wins[deck1.id] += 1
            elif match.result == 'player2':
                deck1_actual = 0.0
                deck_wins[deck2.id] += 1
            elif match.result == 'draw':
                deck1_actual = 0.5
            else:
                continue

            # Update deck ratings
            deck1_change = DECK_K_FACTOR * (deck1_actual - deck1_expected)
            deck_ratings[deck1.id] += deck1_change
            deck_ratings[deck2.id] -= deck1_change

            deck_games[deck1.id] += 1
            deck_games[deck2.id] += 1

        # Update database
        for deck_id, final_elo in deck_ratings.items():
            deck = Deck.query.get(deck_id)
            if deck:
                deck.elo = final_elo
                deck.games_played = deck_games[deck_id]
                deck.wins = deck_wins[deck_id]

        db.session.commit()


def calculate_radar_attributes(player: Player) -> Dict[str, float]:
    """
    Calculate 5 radar chart attributes for a player (0-100 scale).
    Based on PTCG_Stat RadarChart.gs logic.
    """
    import math

    # Get all players for percentile calculations
    all_players = Player.query.filter(Player.games_played > 0).all()

    # 1. Skill (ELO percentile)
    if all_players:
        elo_values = sorted([p.elo for p in all_players])
        percentile_rank = sum(1 for elo in elo_values if elo <= player.elo) / len(elo_values)
        skill = percentile_rank * 100
    else:
        skill = 50.0

    # 2. Consistency (Adjusted win rate × 100)
    consistency = player.adjusted_win_rate * 100

    # 3. Experience (log scale of games played)
    if player.games_played > 0:
        # LN(Games+1) / LN(31) × 100, capped at 100
        experience = min(100, (math.log(player.games_played + 1) / math.log(31)) * 100)
    else:
        experience = 0.0

    # 4. Clutch (Win rate vs higher-rated opponents)
    # Get matches where opponent had higher ELO
    clutch_wins = 0
    clutch_games = 0

    # This requires match history - simplified for now
    # In full implementation, would query ELOHistory
    clutch = 50.0  # Placeholder

    # 5. Top Cut (Tournament top 4 finish rate × 100)
    # Would require tournament placement tracking
    top_cut = 0.0  # Placeholder

    return {
        'skill': round(skill, 1),
        'consistency': round(consistency, 1),
        'experience': round(experience, 1),
        'clutch': round(clutch, 1),
        'top_cut': round(top_cut, 1)
    }


def update_all_radar_attributes():
    """Update radar attributes for all players"""
    players = Player.query.filter(Player.games_played > 0).all()

    for player in players:
        attributes = calculate_radar_attributes(player)
        player.skill = attributes['skill']
        player.consistency = attributes['consistency']
        player.experience = attributes['experience']
        player.clutch = attributes['clutch']
        player.top_cut = attributes['top_cut']

    db.session.commit()
