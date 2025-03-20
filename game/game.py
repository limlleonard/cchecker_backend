from math import pi, cos, sin
from .models import Game_state

width_board, height_board = 720, 720
CENTERX, CENTERY = width_board / 2, height_board / 2
diameterField = 30
diameterPiece = 24
DISTCC = 40  # center-center distance
Middle_Layer = 4  # This is the number of layers of circles outside of the center circle, it builds up the middle of the board as a hexagon. Beyond this layer will be 6 corners


def rotate_point(
    pc: tuple[int, int], p1: tuple[int, int], nr_angle: int
) -> tuple[int, int]:
    """
    Rotate one point (p1) a certain angle around another point (pc). In the game, it should only rotate 60*nr_angle degree. nr_angle should be a int between 0-5
    Args:
        pc (tuple[int,int]): center point.
        p1 (tuple[int,int]): rotate point.
    Returns:
        tuple[int,int]: rotated point.
    """
    cx, cy = pc
    x1, y1 = p1
    angle_rad = 2 * pi * nr_angle / 6
    # Translate point to origin
    translated_x = x1 - cx
    translated_y = y1 - cy
    # Rotate point
    x2 = translated_x * cos(angle_rad) - translated_y * sin(angle_rad)
    y2 = translated_x * sin(angle_rad) + translated_y * cos(angle_rad)
    # Translate point back
    x2 += cx
    y2 += cy
    return (x2, y2)


class Board:
    def __init__(self):
        """
        A customized coordinate is used for defining all the poitns on board but not used yet.
        (nr_layer, nr_beam(0-5), nr_side perpendicular to beam):(x,y)
        lst_board, lst_board_round saves the coord of all positions in the same order"""
        self.dct_board = self.init_dict()
        self.lst_board = [self.dct_board[a1] for a1 in self.dct_board]
        self.lst_board_int = [
            (round(coord[0]), round(coord[1])) for coord in self.lst_board
        ]

    def init_dict(self) -> dict:
        dct_board = {}
        dct_board[(0, 0, 0)] = (CENTERX, CENTERY)
        for nr_layer in range(1, Middle_Layer * 2 + 1):
            r1 = DISTCC * nr_layer  # Distance from center to the current layer
            nr_circles_layer = nr_layer  # Number of circles on this layer
            nr_skip = nr_layer - Middle_Layer
            for direction in range(6):
                angle1 = (direction * 2 * pi) / 6
                x1, y1 = CENTERX + r1 * cos(angle1), CENTERY + r1 * sin(angle1)
                # fantacy next point to calculate the coordinate of points in between
                angle2 = ((direction + 1) * 2 * pi) / 6
                x2, y2 = CENTERX + r1 * cos(angle2), CENTERY + r1 * sin(angle2)
                if nr_skip < 1:  # inside the middle layer
                    for nr_circle_layer in range(nr_circles_layer):
                        x3 = x1 + (x2 - x1) * nr_circle_layer / nr_circles_layer
                        y3 = y1 + (y2 - y1) * nr_circle_layer / nr_circles_layer
                        dct_board[(nr_layer, direction, nr_circle_layer)] = (x3, y3)
                else:  # outer layers / corners
                    for nr_circle_layer in range(
                        nr_skip, nr_circles_layer - nr_skip + 1
                    ):
                        x3 = x1 + (x2 - x1) * nr_circle_layer / nr_circles_layer
                        y3 = y1 + (y2 - y1) * nr_circle_layer / nr_circles_layer
                        dct_board[(nr_layer, direction, nr_circle_layer)] = (x3, y3)
        return dct_board


class Player:
    def __init__(self, init_dir=1, state: list | None = None):
        """
        Args:
            init_dir: int: initial direction 0-5. (In which corner does it start playing)
            state: save lst_piece and lst_target
        """
        if state is not None:
            self.lst_piece = [tuple(coord) for coord in state[0]]
            self.lst_target = [tuple(coord) for coord in state[1]]
        else:
            self.lst_piece = self.init_pieces(init_dir)
            self.lst_target = self.init_pieces(
                init_dir + 3
            )  # +3 means + 180°, to the opposite side
        self.lst_piece_int = [
            (round(coord[0]), round(coord[1])) for coord in self.lst_piece
        ]
        self.lst_target_int = [
            (round(coord[0]), round(coord[1])) for coord in self.lst_target
        ]
        self.selected = None  # coord of the selected figur
        self.valid_pos = []
        self.gewonnen = False

    def init_pieces(self, init_dir):
        """Initialize the pieces, it is similar to init board, but just create one corner"""
        lst_piece = []
        for k in range(Middle_Layer + 1, Middle_Layer * 2 + 1):
            radius = DISTCC * k  # Distance for the current layer
            num_circles_layer = k  # Number of circles in this layer
            num_to_skip = k - Middle_Layer

            angle = (init_dir * 2 * pi) / 6
            x = CENTERX + radius * cos(angle)
            y = CENTERY + radius * sin(angle)
            # Fantacy 'next point' to calculate the coordinate of points in between
            angle1 = ((init_dir + 1) * 2 * pi) / 6
            x1 = CENTERX + radius * cos(angle1)
            y1 = CENTERY + radius * sin(angle1)

            for j in range(num_to_skip, num_circles_layer - num_to_skip + 1):
                x2 = x + (x1 - x) * j / num_circles_layer
                y2 = y + (y1 - y) * j / num_circles_layer
                lst_piece.append((round(x2), round(y2)))
        return lst_piece

    def win_check(self) -> bool:
        sorted_lst_piece = sorted(self.lst_piece_int)
        sorted_lst_ziel = sorted(self.lst_target_int)
        if sorted_lst_piece == sorted_lst_ziel:
            self.gewonnen = True

    def rotate(self, lst_piece: tuple) -> tuple:
        return [(2 * CENTERX - x, 2 * CENTERY - y) for (x, y) in lst_piece]

    def get_state(self):
        return [
            self.lst_piece,
            self.lst_target,
        ]


class Game:
    def __init__(
        self, roomnr=0, nr_player=0, state_players: list | None = None, order=0
    ):
        """game will be either initialized from 0 or from a given state"""
        self.board = Board()
        self.roomnr = roomnr
        self.dct_dir = {
            1: [1],
            2: [1, 4],
            3: [1, 3, 5],
            4: [1, 4, 2, 5],
            5: [1, 3, 5, 2, 4],
            6: [1, 3, 5, 2, 4, 6],
        }  # depending on nr of players, the position of each player
        if nr_player > 0 and state_players is None:
            self.order = 0  # who is in turn
            self.players = []
            for nr1 in range(nr_player):
                init_dir = self.dct_dir[nr_player][nr1]
                self.players.append(Player(init_dir))
        elif nr_player == 0 and state_players is not None:
            self.order = order
            self.players = [Player(state=state) for state in state_players]
        else:
            print(
                f"roomnr: {roomnr}, nr_player: {nr_player}, ll_pieces: {state_players}, order: {order}"
            )
            raise Exception("Given vars cannot create a new game")

    def get_precise_coord(self, coord_int: tuple[int, ...]) -> tuple[float, ...]:
        """find the index in lst_board_int, then return the value from lst_board since they have the same order"""
        return self.board.lst_board[self.board.lst_board_int.index(coord_int)]

    def find_neighbors(self, coord_int: tuple[int, ...]) -> tuple[int, ...]:
        """6 positions around the figure + 6 positionen over them"""
        x, y = self.get_precise_coord(coord_int)
        lst_neighbor = []
        for i in range(6):
            angle = i * 2 * pi / 6
            x1 = round(x + DISTCC * cos(angle))
            y1 = round(y + DISTCC * sin(angle))
            x2 = round(
                x + 2 * DISTCC * cos(angle)
            )  # position über dem direkten Nachbar
            y2 = round(y + 2 * DISTCC * sin(angle))
            lst_neighbor.append(((x1, y1), (x2, y2)))
        return lst_neighbor

    def get_ll_piece(self) -> list[list[tuple[int, int]]]:
        """get a list (players) of list (pieces)"""
        ll_piece = []  # Figuren aller Farben berückwichtigen
        for player1 in self.players:
            ll_piece.append(player1.lst_piece_int)
        return ll_piece

    def find_valid_pos(self, coord_int: tuple[int, int]) -> list[tuple[int, int]]:
        """find valid position where a piece could go"""
        visited = set()
        valid_pos = []
        ll_piece = self.get_ll_piece()
        lst_piece = [
            coord for figuren in ll_piece for coord in figuren
        ]  # Figuren aller Farben berückwichtigen
        lst_neighbor = self.find_neighbors(coord_int)
        for coord1, _ in lst_neighbor:  # no jump
            if (
                coord1 in self.board.lst_board_int and coord1 not in lst_piece
            ):  # if it is in board but not in pieces
                valid_pos.append(coord1)

        def dfs(coord_int: tuple[int, int]):
            """depth first search algorithm"""
            if coord_int in visited:
                return  # Skip if already visited
            visited.add(coord_int)  # Mark node as visited
            valid_pos.append(coord_int)  # Add node to connected list

            lst_neighbor1 = self.find_neighbors(coord_int)
            for coord1, coord2 in lst_neighbor1:
                if (
                    coord2 not in visited
                    and coord1 in lst_piece  # there is one piece to jump over
                    and coord2 not in lst_piece  # over the piece there is space
                    and coord2 in self.board.lst_board_int
                ):
                    dfs(coord2)

        dfs(coord_int)
        return valid_pos

    def klicken(self, coord_int: tuple[int, int]):
        """klicking on a piece or a field,"""
        new_figures = None
        players = self.players[self.order]
        if coord_int in players.lst_piece_int:  # click on a piece
            players.valid_pos = self.find_valid_pos(coord_int)
            if (
                len(players.valid_pos) > 0
            ):  # you can only select a piece, that can be moved
                players.selected = coord_int
        elif players.selected and coord_int in players.valid_pos:  # click on a field
            # move piece, pop the old piece and insert the new piece
            index_from = players.lst_piece_int.index(players.selected)
            # coord_from=player.selected
            players.lst_piece_int.pop(index_from)
            players.lst_piece.pop(index_from)
            players.lst_piece_int.append(coord_int)
            players.lst_piece.append(self.get_precise_coord(coord_int))
            # coord_to=coord_round
            players.selected = None
            players.valid_pos = []
            players.win_check()
            self.order = (self.order + 1) % len(self.players)
            new_figures = (
                self.get_ll_piece()
            )  # if new_figures is not none, it means a piece is moved
        else:
            print(coord_int, players.lst_piece_int)
        return (
            players.selected,
            players.valid_pos,
            new_figures,
            self.order,
            players.gewonnen,
        )

    def get_rotate_player(self, nr_angle: int):
        """Rotate all the player and return them"""
        player_rotate = []
        for player_old in self.players:
            player_new = player_old.copy()
            player_new.lst_piece = [
                rotate_point((CENTERX, CENTERY), p1, nr_angle)
                for p1 in player_new.lst_piece
            ]
            player_new.lst_piece_int = [
                (round(coord[0]), round(coord[1])) for coord in player_new.lst_piece
            ]
            player_new.lst_target = [
                rotate_point((CENTERX, CENTERY), p1, nr_angle)
                for p1 in player_new.lst_target
            ]
            player_new.lst_target_round = [
                (round(coord[0]), round(coord[1])) for coord in player_new.lst_target
            ]
        return player_rotate

    def save_state(self) -> None:
        state_players = [p1.get_state() for p1 in self.players]
        Game_state.objects.filter(roomnr=self.roomnr).delete()
        Game_state.objects.create(
            order=self.order, roomnr=self.roomnr, state_players=state_players
        )


class Games:
    def __init__(self):
        self.lst_game = []

    def create_game(self):
        game1 = Game()
        self.lst_game.append(game1)


# todos: reset, win check, add player, turn board, swap turns
