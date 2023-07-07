from flask import Flask, request, session
from flask_socketio import SocketIO, join_room as join_room_, send, leave_room
from uuid import uuid4 as v4

app = Flask(__name__)
app.config['SECRET_KEY'] = '5a23906e-f62b-4110-8542-eb872e6a3316'

socketio = SocketIO(app)

rooms = {}

def create_game():
    return {"game": 123}

def create_card():
    # TODO: создать карточку на основе настроек
    return {"test": '123'}

def create_player(name, card, is_host):
    # TODO: сделать создание игрока
    return {
        "id": str(v4()),
        "name": name,
        "is_host": is_host,
        **card
    }

def create_room_(name, creator, game):
    # TODO: сделать создание комнаты
    # TODO: добавить создание и генерацию игры с выбранными настройками
    return {
        "id": str(v4()), 
        "name": name, 
        "players": [creator],
        "game": game
    }

@app.route('/room', methods=['POST'])
def create_room():
    req = request.get_json()
    print(req)
    print(rooms)

    room_name, player_name = req['room_name'], req['player_name']

    # ? Подумать над добавлением настроек
    # TODO: проверка на допустимость создания комнаты с таким названием
    if room_name in rooms:
        return {"error_message": "Комната с таким названием уже существует"}, 403

    card = create_card()
    # TODO: добавление игрока в базу данных
    creator = create_player(player_name, card, True)
    game = create_game()
    # TODO: добавление комнаты в базу данных
    rooms[room_name] = create_room_(player_name, creator, game)

    session['player_name'] = player_name
    session['room_name'] = room_name

    return rooms[room_name], 200

@app.route('/room/<name>', methods=['POST'])
def join_room(name):

    print(name)
    # TODO: сделать проверку на существование комнаты с таким именем
    if name not in rooms:
        return {"error_message": "Комната с таким названием не найдена"}, 403
    
    req = request.get_json()
    print(req)
    player_name = req['player_name']

    # TODO: получить комнату по name
    room = rooms[name]

    # TODO: сделать проверку на наличие игрока в этой комнате с таким же именем
    for player in room['players']:
        if player_name == player['name']:
            return {"error_message": "В комнате уже есть игрок с таким же именем"}, 403

    card = create_card()
    # TODO: добавление игрока в базу данных
    player = create_player(player_name, card, False)
    # TODO: добавить в таблицу с игроками нового игрока с генерированной карточки
    rooms[name]['players'].append(player)

    session['player_name'] = player_name
    session['room_name'] = room["name"]

    print(rooms)
    return room, 200

@socketio.on('message')
def handle_message(data):
    room_name = session.get('room_name')
    player_name = session.get('player_name')
   
    # TODO: проверить существует ли комната
    if room_name not in rooms:
        leave_room(room_name)
        return 
    
    content = {'name': player_name, 'message': data['data']}
    send(content, to=room_name)
    # rooms[room_name]['messages'].append(content)
    print(content)
    
@socketio.on('connect')
def handle_connect():
    room_name = session.get('room_name')
    player_name = session.get('player_name')

    if not player_name or not room_name:
        return 
    
    # TODO: проверить существует ли комната
    if room_name not in rooms:
        leave_room(room_name)
        return 
    
    join_room_(room_name)
    
    send({'name': player_name, 'message': 'has entered the room'}, to=room_name)
    
@socketio.on('disconnect')
def handle_disconnect():
    room_name = session.get('room_name')
    player_name = session.get('player_name')

    # TODO: проверить существует ли комната
    if room_name not in rooms:
        return 

    session.clear()
    # TODO: получение комнаты из БД
    room = rooms[room_name]
    # TODO: в целом проверка что если ливает создатель
    creator_name = ''
    for players in room['players']:
        if players['name'] == creator_name:
            send({'name': player_name, 'message': 'Creator room has left the room'}, to=room)
            # TODO: удаление комнаты
            del rooms[room]
            return
    send({'name': player_name, 'message': 'has left the room'}, to=room)
    

if __name__ == '__main__':
    app.run(debug=True)