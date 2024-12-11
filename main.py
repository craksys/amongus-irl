from flask import Flask, render_template, redirect, url_for, session, request, flash, get_flashed_messages
from threading import Timer
from functools import wraps
from threading import Thread
import uuid
import threading
import time
import datetime
import random

app = Flask(__name__)
app.secret_key = 'haslo'

# In-memory storage for simplicity
games = {}
players = {}

# Admin login required decorator
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Player login required decorator
def player_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'player_id' not in session:
            return redirect(url_for('join_game'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin_password':  # Replace with secure password checking
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Incorrect password.')
    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
@admin_login_required
def admin_dashboard():
    if request.method == 'POST':
        short_tasks = int(request.form['short_tasks'])
        long_tasks = int(request.form['long_tasks'])
        impostor_kill_cooldown = int(request.form['impostor_kill_cooldown'])
        set_emergency_cooldown = int(request.form['set_emergency_cooldown'])
        game_id = str(uuid.uuid4())[:5]
        games[game_id] = {
            'short_tasks': short_tasks,
            'long_tasks': long_tasks,
            'players': [],
            'started': False,
            'reports': [],
            'votes': {},
            'impostor': None,
            'sabotage': False,
            'repair_attempts': [],
            'sabotage_timer': None,
            'impostors_win': False,
            'voting_end_time': None,
            'sabotage_end_time': None,
            'game_end': False,
            'impostor_kill_cooldown': impostor_kill_cooldown,
            'impostor_kill_timer': None,
            'total_tasks' : None,
            'completed_tasks' : None,
            'sound_played' : False,
            'set_emergency_cooldown': set_emergency_cooldown,
            'emergency_meeting_cooldown_end': None,
        }
        session['game_id'] = game_id
        return redirect(url_for('admin_game', game_id=game_id))
    return render_template('admin_dashboard.html')

@app.route('/admin/game/<game_id>')
@admin_login_required
def admin_game(game_id):
    game = games.get(game_id)
    if not game:
        return 'Game not found.', 404
    return render_template('admin_game.html', game=game, game_id=game_id, players=players)

@app.route('/start_game/<game_id>')
@admin_login_required
def start_game(game_id):
    game = games.get(game_id)
    if game:
        game['started'] = True
        assign_impostor(game)
        assign_tasks(game)
        assign_kill_cooldown(game)
        return redirect(url_for('admin_game', game_id=game_id))
    else:
        return 'Game not found.', 404
    
@app.route('/reset_game/<game_id>', methods=['POST'])
@admin_login_required
def reset_game(game_id):
    game = games.get(game_id)
    if game:
        # Upewnij się, że gra istnieje
        game['completed_tasks'] = 0  # Reset liczby ukończonych zadań
        game['started'] = False  # Zatrzymaj aktualną grę

        impostor_id = game['impostor']
        impostor = players[impostor_id]
        impostor['role'] = 'crewmate'
        for player_id in game['players']:
            player = players[player_id]
            player['alive'] = True
        game['impostor'] = None
        game['impostors_win']= False,
        game['sabotage_end_time']= None
        game['game_end']= False
        return start_game(game_id)
    else:
        return 'Game not found.', 404

def assign_tasks(game):
    task_pool = list(range(1, 21))
    total_tasks = game['short_tasks'] + game['long_tasks']
    total_tasks_crewmates = 0
    total_player_tasks = len(task_pool)
    game['completed_tasks'] = 0
    for player_id in game['players']:
        player_task = {'tasks': [], 'completed_tasks': []}
        if total_tasks > total_player_tasks:
            total_tasks = total_player_tasks
        
        player_task['tasks'] = random.sample(task_pool, total_tasks)
        players[player_id]['tasks'] = player_task

        print(f"Assigning tasks to player {player_id} with role {players[player_id]['role']}")
        if players[player_id]['role'] == 'crewmate':
            total_tasks_crewmates += len(player_task['tasks'])

    game['total_tasks'] = total_tasks_crewmates
    game['completed_tasks'] = sum(len(player['tasks']['completed_tasks']) for player in players.values() if player['alive'] and player['role'] == 'crewmate')

def sabotage_timeout(game):
    game['sabotage'] = False
    game['impostors_win'] = True
    game['game_end'] = True

def assign_impostor(game):
    if game['players']:
        impostor_index = random.randint(0, len(game['players']) - 1)
        impostor = game['players'][impostor_index]  
        game['impostor'] = impostor
        players[impostor]['role'] = 'impostor'
    else:
        game['impostor'] = None

def assign_kill_cooldown(game):
    game['impostor_kill_cooldown'] =  game['impostor_kill_cooldown']   # Domyślny cooldown eliminacji w sekundach
    game['impostor_kill_timer'] = None

def update_cooldown_timer(game):
    while game['impostor_kill_timer'] > 0:
        time.sleep(1)
        game['impostor_kill_timer'] -= 1
    game['impostor_kill_timer'] = None

def hide_voting_result(game):
    time.sleep(5)
    game['show_voting_result'] = False

def check_game_end(game):
    alive_players = [p for p in game['players'] if players[p]['alive']]
    impostors = [p for p in alive_players if players[p]['role'] == 'impostor']
    crewmates = [p for p in alive_players if players[p]['role'] == 'crewmate']
    if not impostors:
        game['game_end'] = True
        game['impostors_win'] = False
    elif len(impostors) >= len(crewmates):
        game['game_end'] = True
        game['impostors_win'] = True
    elif game['completed_tasks'] >= game['total_tasks']:
        game['game_end'] = True
        game['impostors_win'] = False

@app.route('/join', methods=['GET', 'POST'])
def join_game():
    if request.method == 'POST':
        game_id = request.form['game_id']
        player_name = request.form['player_name']
        if game_id in games:
            player_id = str(uuid.uuid4())
            session['player_id'] = player_id
            session['game_id'] = game_id
            players[player_id] = {
                'name': player_name,
                'tasks': {},
                'role': 'crewmate',
                'alive': True
            }
            games[game_id]['players'].append(player_id)
            return redirect(url_for('player_game'))
        else:
            flash('Invalid game ID.')
    return render_template('join_game.html')

@app.route('/game')
@player_required
def player_game():
    player_id = session['player_id']
    game_id = session['game_id']
    game = games.get(game_id)
    player = players.get(player_id)
    if not game or not player:
        return 'Game not found or player not registered.', 404
    alive_players_count = sum(1 for p_id in game['players'] if players[p_id]['alive'])
    return render_template(
        'player_game.html',
        game=game,
        player=player,
        players=players,
        player_id=player_id,
        messages=get_flashed_messages(),
        alive_players_count=alive_players_count
    )

@app.route('/complete_task', methods=['POST'])
@player_required
def complete_task():
    player_id = session['player_id']
    game_id = session['game_id']
    task_number = int(request.form['task_number'])
    player = players[player_id]
    if task_number in player['tasks']['tasks']:
        player['tasks']['completed_tasks'].append(task_number)
        game = games[game_id]
        game['completed_tasks'] = sum(len(player['tasks']['completed_tasks']) for player in players.values() if player['role'] == 'crewmate')
        check_game_end(game)
    return redirect(url_for('player_game'))

@app.route('/report_body')
@player_required
def report_body():
    game_id = session['game_id']
    game = games[game_id]
    game['reports'].append('Body reported by {}'.format(players[session['player_id']]['name']))
    start_voting(game)
    return redirect(url_for('player_game'))

@app.route('/emergency_meeting')
@player_required
def emergency_meeting():
    game_id = session['game_id']
    game = games[game_id]

    current_time = datetime.datetime.utcnow()
    cooldown_end = game.get('emergency_meeting_cooldown_end')
    print(f"Current time: {current_time}, Cooldown ends: {cooldown_end}")
    
    
    if game['emergency_meeting_cooldown_end'] and current_time < game['emergency_meeting_cooldown_end']:
        flash("Emergency meeting is on cooldown. Please wait.")
        return redirect(url_for('player_game'))
    
    game['reports'].append('Emergency meeting called by {}'.format(players[session['player_id']]['name']))
    start_voting(game)
    return redirect(url_for('player_game'))

def start_voting(game):
    game['voting'] = True
    game['votes'] = {}  # Reset votes
    game['voted_players'] = []  # Reset voted players list
    game['voting_end_time'] = (datetime.datetime.utcnow() + datetime.timedelta(seconds=30)).isoformat()
    threading.Thread(target=voting_timer, args=(game,)).start()
    
def voting_timer(game):
    time.sleep(30)  # Voting lasts for 30 seconds
    if game['voting']:
        game['voting'] = False
        game['voting_end_time'] = None
        process_votes(game)
        game['show_voting_result'] = True
        time.sleep(5)
        game['show_voting_result'] = False
        check_game_end(game)

@app.route('/vote', methods=['POST'])
@player_required
def vote():
    vote_for = request.form['vote_for']
    game_id = session['game_id']
    game = games[game_id]
    player_id = session['player_id']

    # Check if the player is alive
    if not players[player_id]['alive']:
        flash("You are eliminated and cannot vote.")
        return redirect(url_for('player_game'))

    if game['voting']:
        if player_id not in game['voted_players']:
            game['votes'][player_id] = vote_for
            game['voted_players'].append(player_id)

            # Get lists of alive players and alive players who have voted
            alive_players = [p_id for p_id in game['players'] if players[p_id]['alive']]
            voted_alive_players = [p_id for p_id in game['voted_players'] if players[p_id]['alive']]

            # Debugging statements
            print(f"Total alive players: {len(alive_players)}")
            print(f"Alive players who have voted: {len(voted_alive_players)}")
            print(f"Voted players list: {game['voted_players']}")

            if len(voted_alive_players) >= len(alive_players):
                # All alive players have voted; end voting early
                game['voting'] = False
                game['voting_end_time'] = None
                process_votes(game)
                # Display voting result for 5 seconds
                game['show_voting_result'] = True
                Thread(target=hide_voting_result, args=(game,)).start()
        else:
            flash("You have already voted.")
    else:
        flash("Voting is not currently active.")
    return redirect(url_for('player_game'))

def process_votes(game):
    print("Processing votes...")
    votes = game['votes']
    vote_counts = {}
    for vote in votes.values():
        if vote not in vote_counts:
            vote_counts[vote] = 0
        vote_counts[vote] += 1

    if vote_counts:
        max_votes = max(vote_counts.values())
        candidates = [k for k, v in vote_counts.items() if v == max_votes]
        if 'skip' in candidates or len(candidates) > 1:
            game['voting_result'] = "No one was eliminated."
        else:
            eliminated_player_id = candidates[0]
            if eliminated_player_id in players:
                players[eliminated_player_id]['alive'] = False
                game['reports'].append('Player {} was ejected.'.format(players[eliminated_player_id]['name']))
                game['voting_result'] = 'Player {} was ejected.'.format(players[eliminated_player_id]['name'])
    else:
        game['voting_result'] = "No votes were cast."

    game['impostor_kill_timer'] = game['impostor_kill_cooldown']
    threading.Thread(target=update_cooldown_timer, args=(game,)).start()
    
    game['emergency_meeting_cooldown_end'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=game['set_emergency_cooldown'] )

    game['votes'] = {}  # Reset votes
    game['voted_players'] = []  # Reset voted players list
    check_game_end(game)

@app.route('/sabotage')
@player_required
def sabotage():
    player_id = session['player_id']
    game_id = session['game_id']
    game = games[game_id]
    if game['impostor'] == player_id and not game['sabotage']:
        game['sabotage'] = True
        game['repair_attempts'] = []
        # Ustawiamy czas zakończenia sabotażu
        game['sabotage_end_time'] = (datetime.datetime.utcnow() + datetime.timedelta(seconds=45)).isoformat()
        # Uruchomienie timera 45 sekund
        game['sabotage_timer'] = Timer(45.0, sabotage_timeout, [game])
        game['sabotage_timer'].start()
        return redirect(url_for('player_game'))
    else:
        return 'Only the impostor can sabotage.', 403
    
@app.route('/repair')
@player_required
def repair():
    player_id = session['player_id']
    game_id = session['game_id']
    game = games[game_id]
    if game['sabotage']:
        if player_id not in game['repair_attempts']:
            game['repair_attempts'].append(player_id)
        if len(game['repair_attempts']) >= 2:
            game['sabotage'] = False
            game['repair_attempts'] = []
            game['sabotage_end_time'] = None
            # Anulowanie timera sabotażu
            if game['sabotage_timer']:
                game['sabotage_timer'].cancel()
                game['sabotage_timer'] = None
        return redirect(url_for('player_game'))
    else:
        return redirect(url_for('player_game'))

@app.route('/eliminate', methods=['POST'])
@player_required
def eliminate():
    target_id = request.form['target_id']
    player_id = session['player_id']
    game_id = session['game_id']
    game = games[game_id]
    if game['impostor'] == player_id and players[target_id]['alive'] and game['impostor_kill_timer'] is None:
        players[target_id]['alive'] = False
        game['impostor_kill_timer'] = game['impostor_kill_cooldown']
        threading.Thread(target=update_cooldown_timer, args=(game,)).start()
        check_game_end(game)
        return redirect(url_for('player_game'))
    else:
        return 'Cannot eliminate this player.', 403

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    current_theme = session.get('theme', 'light')
    session['theme'] = 'dark' if current_theme == 'light' else 'light'
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')