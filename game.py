from random import randint
from cryptography.fernet import Fernet


# setrecursionlimit(10 ** 9)

def write_key():
    key = Fernet.generate_key()
    with open('crypto.key', 'wb') as key_file:
        key_file.write(key)


def load_key():
    return open('crypto.key', 'rb').read()


def encrypt(filename, key):
    f = Fernet(key)

    with open(filename, 'rb') as file:
        file_data = file.read()
        encrypted_data = f.encrypt(file_data)
    with open(filename, 'wb') as file:
        file.write(encrypted_data)


def decrypt(filename, key):
    f = Fernet(key)
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    with open(filename, 'wb') as file:
        file.write(decrypted_data)


class Field():
    def __init__(self, game_params):
        self.field = [[0] * game_params['width'] for _ in range(game_params['height'])]
        self.opened = set()
        if game_params['bomb_min'] < game_params['width'] * game_params['height']:
            bombs_count = randint(game_params['bomb_min'], game_params['bomb_max'])
            while bombs_count >= game_params['width'] * game_params['height']:
                bombs_count = randint(game_params['bomb_min'], game_params['bomb_max'])
            self.flags_count = bombs_count
            bombs = []
            for i in range(bombs_count):
                x, y = randint(0, game_params['width'] - 1), randint(0, game_params['height'] - 1)
                while self.field[y][x] < 0:
                    x, y = randint(0, game_params['width'] - 1), randint(0, game_params['height'] - 1)
                self.field[y][x] = -1

                for i in (
                        (x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x - 1, y), (x + 1, y), (x - 1, y + 1),
                        (x, y + 1),
                        (x + 1, y + 1)):
                    if 0 <= i[0] < game_params['width'] and 0 <= i[1] < game_params['height']:
                        self.field[i[1]][i[0]] += 1

        else:
            print('Invalid game params')
            exit(0)

    def cell_check(self, x, y):
        if 0 <= x < len(self.field[0]) and 0 <= y < len(self.field):
            return self.field[y][x]
        return -3

    def set_loaded_field(self, field, opened, flags):
        self.field = field
        self.opened = opened
        self.flags_count = flags

    def add_opened_cell(self, x, y):
        self.opened.add((x, y))
        if len(self.opened) == len(self.field) * len(self.field[0]):
            print('You WIN!!!')

    def __str__(self):
        res = f'{len(self.field)}\n'
        for i in self.field:
            res += ' '.join([str(j) for j in i]) + '\n'
        res += f'{len(self.opened)}\n'
        for i in self.opened:
            res += f"{i[0]} {i[1]}\n"
        res += str(self.flags_count)
        return res

    def check_opened(self, x, y):
        return (x, y) in self.opened

    def open_cell(self, x, y):
        if 0 <= x < len(self.field[0]) and 0 <= y < len(self.field) and not self.check_opened(x, y):
            self.add_opened_cell(x, y)
            if self.cell_check(x, y) == 0:
                for i in (
                        (x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x - 1, y), (x + 1, y), (x - 1, y + 1), (x, y + 1),
                        (x + 1, y + 1)):
                    if self.cell_check(i[0], i[1]) >= 0:
                        self.open_cell(i[0], i[1])
            elif self.cell_check(x, y) == -1:
                for i in range(len(self.field)):
                    for j in range(len(self.field[i])):
                        if self.cell_check(j, i) == -1:
                            self.add_opened_cell(j, i)
            return self.cell_check(x, y)

    def set_flag(self, x, y):
        if self.flags_count > 0:
            self.field[y][x] = -2
            self.add_opened_cell(x, y)
            if not self.check_opened(x, y):
                self.flags_count -= 1
        else:
            print('No more Flags!!')


class Game():
    def __init__(self, width=5, height=5, bomb_min=2, bomb_max=5):
        self.game_params = {'width': width, 'height': height, 'bomb_min': bomb_min, 'bomb_max': bomb_max}
        self.field = Field(self.game_params)
        self.gameover = False

    def game_input(self):
        player_input = input().split()
        player_input[0], player_input[1] = int(player_input[0]) - 1, int(player_input[1]) - 1
        return player_input

    def gameplay(self):
        self.visualize()
        while not self.gameover:
            inp = self.game_input()
            if inp[2] == 'Flag':
                self.field.set_flag(inp[0], inp[1])
            elif inp[2] == 'Open':
                cell = self.field.open_cell(inp[0], inp[1])
                if cell == -1:
                    self.gameover = True
            elif inp[2] == 'Save':
                self.save_game()
                exit(0)
            self.visualize()

    def visualize(self):
        for i in range(self.game_params['height']):
            v_str = []
            for j in range(self.game_params['width']):
                if self.field.check_opened(j, i):
                    if self.field.cell_check(j, i) == -1:
                        v_str.append('*')
                    elif self.field.cell_check(j, i) == -2:
                        v_str.append('f')
                    else:
                        v_str.append(self.field.cell_check(j, i))
                else:
                    v_str.append('#')
            print(*v_str)

    def save_game(self):
        with open('saved_game.gachi', 'w') as f:
            f.write(str(self.field))
        write_key()
        key = load_key()
        encrypt('saved_game.gachi', key)

    def load_game(self):
        try:
            key = load_key()
            decrypt('saved_game.gachi', key)
            opened = set()
            with open('saved_game.gachi', 'r') as f:
                field = [list(map(int, f.readline().split())) for _ in range(int(f.readline()))]
                for i in range(int(f.readline())):
                    opened.add(tuple(map(int, f.readline().split())))
                flags = int(f.readline())
            self.game_params['width'] = len(field[0])
            self.game_params['height'] = len(field[0])
            self.field.set_loaded_field(field, opened, flags)
            encrypt('saved_game.gachi', key)
        except FileNotFoundError:
            print('Cохраненная игра не найдена будет запущена стандартная игра')


print("формат команды: x y действие(Open или Flag). например: 1 1 Open")
c = input('Введите load чтобы загрузить последнюю сохраненную игру или нажмите enter для продолжения ')
if c.strip() == 'load':
    game = Game()
    game.load_game()
else:
    c = input(
        'Введите customize чтобы задать длину, ширну, минимальное и максимальное количество бомб или нажмите enter для запуска стандартной игры ')
    if c.strip() == 'customize':
        w, h, minn, maxx = map(int, input('Введите параметры игры ').split())
        game = Game(w, h, minn, maxx)
    else:
        game = Game()
game.gameplay()
