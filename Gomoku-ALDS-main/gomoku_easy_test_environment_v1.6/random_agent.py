import random, math, copy
import gomoku
from gomoku import Move, GameState


class mcts:
    def __init__(self, state_game, parent=None, valid_moves=None, last_move=None):
        """Constructor for the player."""
        self.state = state_game
        self.parent = parent
        self.valid_moves = valid_moves
        self.last_move = last_move
        self.children = []
        self.N = 0 #Number of visits to this node
        self.Q = 0 #Number of wins from this node

    def uct(self):
        value = -math.inf
        best_child = None
        if len(self.children) == 0:
            print("no children")
            return None

        exploit_term = self.Q / self.N  # Amount of wins / number of visits
        c = math.sqrt(2)  # constant
        sqr_p_n = math.sqrt((math.log(self.parent.N)) / self.N)  # Squareroot of n ’s parent is visited n.parent.N versus how often this node is visited n.N
        result = exploit_term + c * sqr_p_n

        for ch in self.children:
            if result > value:
                value = result
                best_child = ch

        return best_child

    def is_terminal(self):
        if gomoku.check_win(self.state[0], self.last_move) or len(gomoku.valid_moves(self.state)) == 0:
            print("Terminal")
            return True
        print("Not terminal")
        return False

    def who_won(self):
        if gomoku.check_win(self.state[0], self.last_move):
            if self.state[1] % 2 != 0:
                return 1
            if self.state[1] % 2 == 0:
                return -1
            return 0
        return False


def best_move(n):
    best_value = -math.inf
    best_child = None
    for ch in n.children:
        child_value = ch.Q / ch.N
        if ch.Q / ch.N > best_value:
            best_value = child_value
            best_child = ch.move

    return best_child


class berkePlayer:
    """This class specifies a player that just does random moves.
    The use of this class is two-fold: 1) You can use it as a base random roll-out policy.
    2) it specifies the required methods that will be used by the competition to run
    your player
    """
    def __init__(self, black_: bool = True):
        """Constructor for the player."""
        self.black = black_

    def new_game(self, black_: bool):
        """At the start of each new game you will be notified by the competition.
        this method has a boolean parameter that informs your agent whether you
        will play black or white.
        """
        self.black = black_

    def FindSpotToExpand(self, n):
        print("Find")
        if n.is_terminal():
            print("n.terminal true")
            return n

        elif len(n.children) != len(gomoku.valid_moves(n.state)):
            print("Making ChildNode")
            copy_valid_moves = copy.deepcopy(gomoku.valid_moves(n.state))
            action = copy_valid_moves.pop()
            new_state = gomoku.move(n.state, action)

            child_node = mcts(new_state[2], n, copy_valid_moves, action)
            n.children.append(child_node)

            print(n.state[0])
            return child_node

        highest_uct_child = n.uct()
        return self.FindSpotToExpand(highest_uct_child)

    def Rollout(self, n, s):
        print("Roll")
        print("action:", n.last_move)
        while not n.is_terminal():
            print("while loop RollOut")
            print(gomoku.valid_moves(s))

            a = random.choice((gomoku.valid_moves(s)))
            print(a)
            print(s)
            s = gomoku.move(s, a)
            print(s)

        print("return who won")
        return n.who_won()

    def BackupValue(self, val, n):
        print("adad")
        while n is not None:
            n.N += 1
            if n.state[1] % 2 != 0:
                n.Q -= val
            else:
                n.Q += val

            n = n.parent

    def move(self, state: GameState, last_move: Move, max_time_to_move: int = 1000) -> Move:
        """This is the most important method: the agent will get:
        1) the current state of the game
        2) the last move by the opponent
        3) the available moves you can play (this is a special service we provide ;-) )
        4) the maximum time until the agent is required to make a move in milliseconds [diverging from this will lead to disqualification].
        """
        n_root = mcts(state, None, gomoku.valid_moves(state), last_move)

        while max_time_to_move != 0:
            n_leaf = self.FindSpotToExpand(n_root)
            val = self.Rollout(n_leaf, copy.deepcopy(state))
            self.BackupValue(val, n_leaf)

        return best_move(n_root)

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "Berke Ozmuk (1762463)"

