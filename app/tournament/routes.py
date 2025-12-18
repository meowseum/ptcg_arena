"""
Tournament routes
"""
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime, date
from app.tournament import tournament_bp
from app.models import db, Tournament, TournamentPlayer, Player, Match, Season
from app.decorators import organizer_required

@tournament_bp.route('/list')
def list():
    """List all tournaments"""
    status_filter = request.args.get('status', 'all')

    query = Tournament.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    tournaments = query.order_by(Tournament.date.desc()).all()

    return render_template('tournament/list.html',
                          tournaments=tournaments,
                          status_filter=status_filter)

@tournament_bp.route('/<int:tournament_id>')
def view(tournament_id):
    """View tournament details"""
    tournament = Tournament.query.get_or_404(tournament_id)

    # Get standings (sorted by points, then tiebreakers)
    participants = sorted(
        tournament.participants,
        key=lambda p: (-p.points, -p.wins),  # TODO: Add proper tiebreakers
        reverse=False
    )

    # Get matches for this tournament
    matches_by_round = {}
    for match in tournament.matches:
        if match.round_number not in matches_by_round:
            matches_by_round[match.round_number] = []
        matches_by_round[match.round_number].append(match)

    return render_template('tournament/view.html',
                          tournament=tournament,
                          participants=participants,
                          matches_by_round=matches_by_round)

@tournament_bp.route('/create', methods=['GET', 'POST'])
@login_required
@organizer_required
def create():
    """Create a new tournament"""
    if request.method == 'POST':
        name = request.form.get('name')
        date_str = request.form.get('date')
        mode = request.form.get('mode', 'normal')
        draw_points = int(request.form.get('draw_points', 0))
        season_id = request.form.get('season_id')

        if not name or not date_str:
            flash('請填寫賽事名稱和日期', 'error')
            return redirect(url_for('tournament.create'))

        tournament_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        tournament = Tournament(
            name=name,
            date=tournament_date,
            organizer_id=current_user.id,
            mode=mode,
            draw_points=draw_points,
            season_id=int(season_id) if season_id else None,
            status='upcoming'
        )

        db.session.add(tournament)
        db.session.commit()

        flash(f'賽事「{name}」創建成功！', 'success')
        return redirect(url_for('tournament.view', tournament_id=tournament.id))

    # Get seasons for dropdown
    seasons = Season.query.order_by(Season.start_date.desc()).all()

    return render_template('tournament/create.html', seasons=seasons)
