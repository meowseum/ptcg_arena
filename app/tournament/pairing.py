"""
Swiss Tournament Pairing Algorithm
Ported from Swiss/main.py - DO NOT MODIFY ORIGINAL
"""
import random
from typing import List, Tuple, Optional, Set
from app.models import TournamentPlayer, Tournament


class PairingEngine:
    """
    Swiss tournament pairing engine with rematch prevention.
    Based on official PTCG Swiss system rules.
    """

    def __init__(self, tournament: Tournament):
        self.tournament = tournament
        self.players = []  # Will be populated with TournamentPlayer objects

    def calculate_omw(self, player: TournamentPlayer) -> float:
        """
        Calculate Opponent Match Win percentage with 25% floor.
        """
        if not player.player.tournament_participations or self.tournament.current_round == 0:
            return 0.0

        total_opponent_win_percent = 0.0
        opponent_count = 0

        # Get opponents from match history
        matches_as_p1 = [m for m in player.tournament.matches if m.player1_id == player.id and m.result]
        matches_as_p2 = [m for m in player.tournament.matches if m.player2_id == player.id and m.result]

        for match in matches_as_p1:
            if match.player2:
                opp = match.player2
                matches_played = opp.wins + opp.losses
                if matches_played == 0:
                    win_percent = 0.25
                else:
                    win_percent = max(0.25, opp.wins / matches_played)
                total_opponent_win_percent += win_percent
                opponent_count += 1

        for match in matches_as_p2:
            if match.player1:
                opp = match.player1
                matches_played = opp.wins + opp.losses
                if matches_played == 0:
                    win_percent = 0.25
                else:
                    win_percent = max(0.25, opp.wins / matches_played)
                total_opponent_win_percent += win_percent
                opponent_count += 1

        if opponent_count == 0:
            return 0.0

        return total_opponent_win_percent / opponent_count

    def calculate_oowp(self, player: TournamentPlayer) -> float:
        """
        Calculate Opponent's Opponent's Win Percentage - secondary tiebreaker.
        """
        if self.tournament.current_round == 0:
            return 0.0

        # Get opponents
        matches_as_p1 = [m for m in player.tournament.matches if m.player1_id == player.id and m.result]
        matches_as_p2 = [m for m in player.tournament.matches if m.player2_id == player.id and m.result]

        opponents = []
        for match in matches_as_p1:
            if match.player2:
                opponents.append(match.player2)
        for match in matches_as_p2:
            if match.player1:
                opponents.append(match.player1)

        if not opponents:
            return 0.0

        total_opponent_omw = sum(self.calculate_omw(opp) for opp in opponents)
        return total_opponent_omw / len(opponents)

    def has_played(self, player1: TournamentPlayer, player2: TournamentPlayer) -> bool:
        """Check if two players have played against each other."""
        matches = self.tournament.matches
        for match in matches:
            if match.result:  # Only count completed matches
                if (match.player1_id == player1.id and match.player2_id == player2.id) or \
                   (match.player1_id == player2.id and match.player2_id == player1.id):
                    return True
        return False

    def find_optimal_pairings(self, remaining: List[TournamentPlayer],
                            current_solution: List[Tuple[TournamentPlayer, TournamentPlayer]]) -> Optional[List[Tuple]]:
        """
        Recursive backtracking to find pairings with no rematches.
        """
        if len(remaining) == 0:
            return current_solution

        if len(remaining) == 1:
            return None  # Odd number, needs bye

        # Try pairing first player with each possible opponent
        p1 = remaining[0]

        for i in range(1, len(remaining)):
            p2 = remaining[i]

            # Check if this would be a rematch
            if not self.has_played(p1, p2):
                # Try this pairing
                new_remaining = remaining[1:i] + remaining[i+1:]
                new_solution = current_solution + [(p1, p2)]

                # Recursively try to complete the pairing
                result = self.find_optimal_pairings(new_remaining, new_solution)
                if result is not None:
                    return result

        # No valid pairing found
        return None

    def find_minimal_rematch_pairings(self, unpaired: List[TournamentPlayer]) -> List[Tuple]:
        """
        When perfect pairing isn't possible, create pairings with minimal rematches.
        """
        pairings = []
        remaining = unpaired.copy()

        while len(remaining) >= 2:
            p1 = remaining[0]
            best_opponent = None

            # Try to find non-rematch opponent
            for p2 in remaining[1:]:
                if not self.has_played(p1, p2):
                    best_opponent = p2
                    break

            # If no non-rematch found, pair with closest points
            if best_opponent is None:
                p1_points = p1.points
                best_opponent = min(remaining[1:],
                                  key=lambda p: abs(p.points - p1_points))
                print(f"FORCED REMATCH: {p1.player.name} vs {best_opponent.player.name}")

            # Make the pairing
            pairings.append((p1, best_opponent))
            remaining.remove(p1)
            remaining.remove(best_opponent)

        return pairings

    def get_bye_counts(self) -> dict:
        """Count how many byes each player has received."""
        bye_counts = {}
        for match in self.tournament.matches:
            if match.result == 'bye' and match.player1:
                player_name = match.player1.player.name
                bye_counts[player_name] = bye_counts.get(player_name, 0) + 1
        return bye_counts

    def pair_round(self, round_num: int) -> Tuple[List[Tuple], Optional[TournamentPlayer]]:
        """
        Create pairings for a round using Swiss tournament algorithm.
        Returns: (pairings, bye_player)
        """
        participants = self.tournament.participants
        active_players = [p for p in participants if not p.dropped]

        if len(active_players) < 2:
            raise ValueError("Need at least 2 active players to pair")

        # Round 1: Random pairing
        if round_num == 1:
            sorted_players = random.sample(active_players, len(active_players))
        else:
            # Sort by points, then OMW
            sorted_players = sorted(
                active_players,
                key=lambda p: (p.points, self.calculate_omw(p)),
                reverse=True
            )

        # Handle bye for odd number of players
        bye_player = None
        if len(sorted_players) % 2 == 1:
            # Prefer players with zero byes, then lowest points + OMW
            bye_counts = self.get_bye_counts()
            bye_candidates = sorted(
                sorted_players,
                key=lambda p: (
                    bye_counts.get(p.player.name, 0),
                    p.points,
                    self.calculate_omw(p)
                )
            )
            bye_player = bye_candidates[0]
            sorted_players.remove(bye_player)

        # Try to find optimal pairings (no rematches)
        pairings = self.find_optimal_pairings(sorted_players, [])

        # If perfect pairing not possible, use minimal rematch strategy
        if pairings is None:
            print("WARNING: Could not find pairing without rematches")
            pairings = self.find_minimal_rematch_pairings(sorted_players)

        return pairings, bye_player

    def get_standings(self) -> List[dict]:
        """
        Calculate current standings with all tiebreakers.
        """
        participants = self.tournament.participants

        standings = []
        for player in participants:
            if player.dropped:
                continue

            omw = self.calculate_omw(player)
            oowp = self.calculate_oowp(player)

            if self.tournament.mode == 'bo3':
                # BO3 mode: use GWP and OGWP
                total_games = player.game_wins + player.game_losses
                gwp = max(0.33, player.game_wins / total_games) if total_games > 0 else 0.33
                # Calculate OGWP (simplified)
                ogwp = 0.33  # Placeholder - would need opponent game stats

                standings.append({
                    'player': player,
                    'points': player.points,
                    'wins': player.wins,
                    'losses': player.losses,
                    'ties': player.ties,
                    'omw': omw,
                    'oowp': oowp,
                    'gwp': gwp,
                    'ogwp': ogwp,
                    'tardy': player.is_tardy
                })
            else:
                # Normal mode
                standings.append({
                    'player': player,
                    'points': player.points,
                    'wins': player.wins,
                    'losses': player.losses,
                    'ties': player.ties,
                    'omw': omw,
                    'oowp': oowp
                })

        # Sort by tiebreakers
        if self.tournament.mode == 'bo3':
            standings.sort(
                key=lambda x: (x['points'], not x['tardy'], x['omw'], x['oowp'], x['gwp'], x['ogwp']),
                reverse=True
            )
        else:
            standings.sort(
                key=lambda x: (x['points'], x['omw'], x['oowp']),
                reverse=True
            )

        return standings
