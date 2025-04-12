import copy
from math import pi, cos, sin
from .models import GameStateEnd, GameStateTemp, Moves

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
    Not used yet
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
    dct_board = lst_board = lst_board_int = None

    @classmethod
    def init_dict(cls) -> dict:
        dct_board = {}
        dct_board[(0, 0, 0)] = (CENTERX, CENTERY)
        for nr_layer in range(1, Middle_Layer * 2 + 1):
            r1 = DISTCC * nr_layer  # Distance from center to the current layer
            nr_circles_layer = nr_layer  # Number of circles on this layer
            nr_skip = nr_layer - Middle_Layer
            for direction in range(6):
                angle1 = (direction * 2 * pi) / 6
                x1, y1 = CENTERX + r1 * cos(angle1), CENTERY + r1 * sin(angle1)
                # calculate the fantacy "next point" first to calculate the coordinate of points in between
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

    """
    A customized coordinate is used for defining all the points on board but not used yet.
    (nr_layer, nr_beam(0-5), nr_side perpendicular to beam):(x,y)
    lst_board, lst_board_round saves the coord of all positions in the same order"""

    @classmethod
    def setup_class(cls):
        cls.dct_board = cls.init_dict()
        cls.lst_board = list(cls.dct_board.values())
        cls.lst_board_int = [(round(x), round(y)) for x, y in cls.lst_board]

    @classmethod
    def get_precise_coord(cls, coord_int: tuple[int, ...]) -> tuple[float, ...]:
        """
        Args: coord_int
        Returns: coord_float
        find the index in lst_board_int, then return the value from lst_board since they have the same order
        """
        return cls.lst_board[cls.lst_board_int.index(coord_int)]


Board.setup_class()


class Player:
    def __init__(self, init_dir=1, state: list | None = None):
        """
        Args:
            init_dir: int: initial direction 0-5. (In which corner does it start playing)
            state: saved lst_piece and lst_target, used to reload a player
        """
        if state is not None:
            self.lst_piece = state[0]
            self.lst_target = state[1]
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

    @staticmethod
    def init_pieces(init_dir):
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

    @staticmethod
    def rotate(lst_piece: tuple) -> tuple:
        return [(2 * CENTERX - x, 2 * CENTERY - y) for (x, y) in lst_piece]

    def get_state(self):
        return [self.lst_piece, self.lst_target]


class Game:
    """Not in use"""

    def __init__(
        self,
        roomnr=0,
        nr_player=0,
        state_players: list[list[tuple[int, int]]] | None = None,
        turnwise=0,
    ):
        """game will be either initialized from 0 or from a given state"""
        self.roomnr = roomnr
        self.dct_dir = {
            1: [1],
            2: [1, 4],
            3: [1, 3, 5],
            4: [1, 4, 2, 5],
            5: [1, 3, 5, 2, 4],
            6: [1, 3, 5, 2, 4, 6],
        }  # depending on nr of players, the position of each player
        if not isinstance(nr_player, int) or not isinstance(roomnr, int):
            raise TypeError("nr_player and roomnr must be an integer.")
        if nr_player > 0 and state_players is None:
            self.turnwise = 0
            self.players = []
            for nr1 in range(nr_player):
                init_dir = self.dct_dir[nr_player][nr1]
                self.players.append(Player(init_dir))
        elif nr_player == 0 and state_players is not None:
            self.turnwise = turnwise
            self.players = [Player(state=state) for state in state_players]
        else:
            print(
                f"roomnr: {roomnr}, nr_player: {nr_player}, ll_pieces: {state_players}, turnwise: {turnwise}"
            )
            raise Exception("Given vars cannot create a new game")

    def find_neighbors(self, coord_int: tuple[int, ...]) -> tuple[int, ...]:
        """6 positions around the figure + 6 positionen over them"""
        x, y = Board.get_precise_coord(coord_int)
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
                coord1 in Board.lst_board_int and coord1 not in lst_piece
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
                    and coord2 in Board.lst_board_int
                ):
                    dfs(coord2)

        dfs(coord_int)
        return valid_pos

    def klicken(self, coord_int: tuple[int, int]):
        """Args:
        coord_int: coordinate clicked
        state_players: coordinates of all players, get from DB probably
        Returns:
        selected: coordinate of the selected piece
        valid_position: coordinates of valid positions to move to
        new_pieces: the same as state_players, in case a piece is moved, otherwise none
        turnwise: int to indicate who is in turn
        gewonnen: win?
        """
        new_figures = None
        player_inturn = self.players[self.turnwise]
        if coord_int in player_inturn.lst_piece_int:  # click on a piece
            player_inturn.valid_pos = self.find_valid_pos(coord_int)
            if (
                len(player_inturn.valid_pos) > 0
            ):  # you can only select a piece, that can be moved
                player_inturn.selected = coord_int
        elif (
            player_inturn.selected and coord_int in player_inturn.valid_pos
        ):  # click on a field
            # move piece, pop the old piece and insert the new piece
            index_from = player_inturn.lst_piece_int.index(player_inturn.selected)
            # coord_from=player.selected
            player_inturn.lst_piece_int.pop(index_from)
            player_inturn.lst_piece.pop(index_from)
            player_inturn.lst_piece_int.append(coord_int)
            player_inturn.lst_piece.append(Board.get_precise_coord(coord_int))
            # coord_to=coord_round
            player_inturn.selected = None
            player_inturn.valid_pos = []
            player_inturn.win_check()
            self.turnwise = (self.turnwise + 1) % len(self.players)
            new_figures = (
                self.get_ll_piece()
            )  # if new_figures is not none, it means a piece is moved
        else:
            print("Invalid move", coord_int, player_inturn.lst_piece_int)
        return (
            player_inturn.selected,
            player_inturn.valid_pos,
            new_figures,
            self.turnwise,
            player_inturn.gewonnen,
        )

    def get_rotate_player(self, nr_angle: int):
        """Not used yet. Rotate all the player and return them"""
        player_rotate = []
        for player_old in self.players:
            player_new = player_old.copy()
            player_new.lst_piece = [
                rotate_point((CENTERX, CENTERY), p1, nr_angle)
                for p1 in player_new.lst_piece
            ]
            player_new.lst_piece_int = [
                [round(coord[0]), round(coord[1])] for coord in player_new.lst_piece
            ]
            player_new.lst_target = [
                rotate_point((CENTERX, CENTERY), p1, nr_angle)
                for p1 in player_new.lst_target
            ]
            player_new.lst_target_int = [
                (round(coord[0]), round(coord[1])) for coord in player_new.lst_target
            ]
        return player_rotate

    def save_state(self) -> None:
        state_players = [p1.get_state() for p1 in self.players]
        GameStateEnd.objects.filter(roomnr=self.roomnr).delete()
        GameStateEnd.objects.create(
            turnwise=self.turnwise, roomnr=self.roomnr, state_players=state_players
        )


class GameStateless:
    _dct_dir = {
        1: [1],
        2: [1, 4],
        3: [1, 3, 5],
        4: [1, 4, 2, 5],
        5: [1, 3, 5, 2, 4],
        6: [1, 3, 5, 2, 4, 6],
    }
    dct_ll_piece_init = {}
    dct_ll_target = {}
    for playernr, init_dirs in _dct_dir.items():
        ll_piece_init = []
        ll_target = []
        for dir1 in init_dirs:
            p1 = Player(dir1)
            ll_piece_init.append(p1.lst_piece_int)
            ll_target.append(p1.lst_target_int)
        dct_ll_piece_init[playernr] = ll_piece_init
        dct_ll_target[playernr] = ll_target

    @staticmethod
    def get_valid_pos(
        coord_int: tuple[int, int], turnwise, current_pos
    ) -> list[tuple[int, int]]:
        """
        check if click on a piece of the player in turn, if yes, check if it has available place to go
        """
        if coord_int not in current_pos[turnwise]:
            return []
        visited = set()
        valid_pos = []
        ll_piece = current_pos
        lst_piece = [
            coord for pieces in ll_piece for coord in pieces
        ]  # Figuren aller Farben berückwichtigen
        lst_neighbor = GameStateless._find_neighbors(coord_int)
        for coord1, _ in lst_neighbor:  # no jump
            if (
                coord1 in Board.lst_board_int and coord1 not in lst_piece
            ):  # if it is in board but not in pieces
                valid_pos.append(coord1)

        def dfs(coord_int: tuple[int, int]):
            """depth first search algorithm"""
            if coord_int in visited:
                return  # Skip if already visited
            visited.add(coord_int)  # Mark node as visited
            valid_pos.append(coord_int)  # Add node to connected list

            lst_neighbor1 = GameStateless._find_neighbors(coord_int)
            for coord1, coord2 in lst_neighbor1:
                if (
                    coord2 not in visited
                    and coord1 in lst_piece  # there is one piece to jump over
                    and coord2 not in lst_piece  # over the piece there is space
                    and coord2 in Board.lst_board_int
                ):
                    dfs(coord2)

        dfs(coord_int)
        return valid_pos

    @staticmethod
    def get_ll_piece(state, moves):
        """
        Start from initial place, play the moves one by one to reach the final state
        """
        current_piece = copy.deepcopy(GameStateless.dct_ll_piece_init[state.playernr])
        for movenr in range(state.movenr):
            move1 = moves.filter(movenr=movenr).first()
            for lst_pieces in current_piece:
                if tuple(move1.coord_from) in lst_pieces:
                    index_from = lst_pieces.index(tuple(move1.coord_from))
                    lst_pieces.pop(index_from)
                    lst_pieces.append(tuple(move1.coord_to))
        return current_piece

    @staticmethod
    def click(roomnr: int, coord_int: tuple[int, int]) -> None:
        """Datas in DB are directly changed here"""
        try:
            state = GameStateTemp.objects.get(roomnr=roomnr)
        except GameStateTemp.DoesNotExist:
            print("Game should have been created but not exist")
            return
        moves = Moves.objects.filter(roomnr=roomnr)
        ll_piece = GameStateless.get_ll_piece(state, moves)

        if not state.selected:  # to select piece
            GameStateless._click_piece(coord_int, state, ll_piece, roomnr)
        else:  # a piece is selected, now to move a piece
            if list(coord_int) in state.valid_pos:
                GameStateless._click_move(state, roomnr, coord_int)
            else:
                GameStateless._click_piece(coord_int, state, ll_piece, roomnr)

    @staticmethod
    def _find_neighbors(coord_int: tuple[int, ...]) -> tuple[int, ...]:
        """
        Args: coord_int
        Returns: lst_neighbor [(coord_inner_neighbor, coord_outer_neighbor), ()]
        neighbors are 6 positions around the figure + 6 positionen over them
        """
        x, y = Board.get_precise_coord(coord_int)
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

    @staticmethod
    def _click_piece(coord_int, state, current_piece, roomnr):
        valid_pos1 = GameStateless.get_valid_pos(
            coord_int, state.turnwise, current_piece
        )
        if valid_pos1:
            selected1 = coord_int
            GameStateTemp.objects.update_or_create(
                roomnr=roomnr,
                defaults={
                    "selected": selected1,
                    "valid_pos": valid_pos1,
                },
            )

    @staticmethod
    def _click_move(state, roomnr, coord_int):
        GameStateTemp.objects.update_or_create(
            roomnr=roomnr,
            defaults={
                "selected": [],
                "valid_pos": [],
                "turnwise": (state.turnwise + 1) % state.playernr,
                "movenr": state.movenr + 1,
            },
        )
        Moves.objects.update_or_create(
            roomnr=roomnr,
            movenr=state.movenr,
            defaults={
                "coord_from": state.selected,
                "coord_to": coord_int,
            },
        )
        # win check
        state2 = GameStateTemp.objects.get(roomnr=roomnr)
        moves = Moves.objects.filter(roomnr=roomnr)
        ll_piece = GameStateless.get_ll_piece(state, moves)
        for nr in range(state2.playernr):
            lst_piece = ll_piece[nr]
            lst_target = GameStateless.dct_ll_target[state2.playernr][nr]
            if sorted(lst_piece) == sorted(lst_target):
                GameStateTemp.objects.update_or_create(
                    roomnr=roomnr, defaults={"win": nr + 1}
                )


# turn board, swap turns
