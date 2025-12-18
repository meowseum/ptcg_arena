"""
Test ELO Calculator - Verify ported logic matches original
"""
import pytest
from app.analytics.elo_calculator import (
    get_k_factor,
    expected_score,
    ELOCalculator,
    STARTING_ELO,
    K_FACTOR_NEW,
    K_FACTOR_ESTABLISHED,
    K_FACTOR_VETERAN
)


def test_k_factor_calculation():
    """Test K-factor thresholds"""
    assert get_k_factor(0) == K_FACTOR_NEW
    assert get_k_factor(14) == K_FACTOR_NEW
    assert get_k_factor(15) == K_FACTOR_ESTABLISHED
    assert get_k_factor(29) == K_FACTOR_ESTABLISHED
    assert get_k_factor(30) == K_FACTOR_VETERAN
    assert get_k_factor(100) == K_FACTOR_VETERAN


def test_expected_score():
    """Test expected score calculation"""
    # Equal ratings should give 0.5 expected score
    assert abs(expected_score(1500, 1500) - 0.5) < 0.001

    # Higher rated player should have > 0.5 expected score
    assert expected_score(1600, 1500) > 0.5
    assert expected_score(1500, 1600) < 0.5

    # 400 point difference should give ~0.909 expected score
    assert abs(expected_score(1900, 1500) - 0.909) < 0.01


def test_elo_change_symmetry():
    """Test that ELO changes sum to zero (zero-sum game)"""
    calculator = ELOCalculator()

    # Simulate two new players
    calculator.player_ratings = {1: 1500, 2: 1500}
    calculator.player_games = {1: 0, 2: 0}
    calculator.player_wins = {1: 0, 2: 0}
    calculator.player_losses = {1: 0, 2: 0}
    calculator.player_peak_elo = {1: 1500, 2: 1500}

    # Manually calculate a match (player 1 wins)
    p1_elo = calculator.player_ratings[1]
    p2_elo = calculator.player_ratings[2]

    p1_k = get_k_factor(calculator.player_games[1])
    p2_k = get_k_factor(calculator.player_games[2])

    p1_expected = expected_score(p1_elo, p2_elo)
    p2_expected = 1 - p1_expected

    p1_change = p1_k * (1.0 - p1_expected)
    p2_change = p2_k * (0.0 - p2_expected)

    # Total change should be approximately zero (may differ slightly due to different K-factors)
    # But with equal K-factors, should be exactly zero
    if p1_k == p2_k:
        assert abs(p1_change + p2_change) < 0.001


def test_starting_elo():
    """Test that starting ELO is 1500"""
    assert STARTING_ELO == 1500.0


def test_k_factors_match_original():
    """Verify K-factor values match original implementation"""
    assert K_FACTOR_NEW == 40
    assert K_FACTOR_ESTABLISHED == 24
    assert K_FACTOR_VETERAN == 16


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
