import random, math, copy
import gomoku
from gomoku import Move, GameState


class mcts:
    def __init__(self, state, parent=None, last_move=None):
        self.state = state
        self.parent = parent
        self.last_move = last_move
        self.children = []
        self.N = 0  # Number of visits from this node
        self.Q = 0  # Number of wins to this node

    def is_terminal(self): #returns whether the game is finished or not
        if gomoku.check_win(self.state[0], self.last_move) or len(gomoku.valid_moves(self.state)) == 0:
            return True
        return False

    def uct_formula(self): #returns the uct result of the child
        exploit_term = self.Q / self.N  # Amount of wins / number of visits
        c = math.sqrt(2)  # constant
        sqr_p_n = math.sqrt((math.log(self.parent.N)) / self.N)  #Squareroot of n ’s parent is visited n.parent.N versus how often this node is visited n.N
        result = exploit_term + c * sqr_p_n #The result of the calculation

        return result

    def uct(self): #Returns the child with the highest uct value
        val = -math.inf
        highest_uct_child = None

        for ch in self.children:
            if ch.uct_formula() > val:
                val = ch.uct_formula()
                highest_uct_child = ch

        return highest_uct_child

    def in_children(self, last_move): #Returns whether the last move is in children or not
        for ch in self.children:
            if ch.last_move == last_move:
                return True
        return False


def best_move(n):  #Returns the best possible move(child)
    best_child = None
    val = -math.inf

    for ch in n.children:
        child_val = ch.Q / ch.N
        if child_val > val:
            val = child_val
            best_child = ch.last_move

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

    def who_won(self, n): #Returns a value on the basis of the result of the game
        if gomoku.check_win(n.state[0], n.last_move):
            if n.state[1] % 2 != self.black:
                return 1
            if n.state[1] % 2 == self.black:
                return -1
        return 0

    def FindSpotToExpand(self, n):
        if n.is_terminal(): #Returns the root node if the game is finished
            return n

        copy_valid_moves = copy.deepcopy(gomoku.valid_moves(n.state))

        if len(n.children) != len(copy_valid_moves): #Returns a new child_node with a copy of all attributes if it is not fully expanded
            copy_state = copy.deepcopy(n.state)
            random.shuffle(copy_valid_moves)
            action = copy_valid_moves.pop()

            while n.in_children(action):
                action = copy_valid_moves.pop()

            is_valid, is_win, new_state = gomoku.move(copy_state, action)

            new_child_node = mcts(new_state, n, action)
            n.children.append(new_child_node)

            return new_child_node

        return self.FindSpotToExpand(n.uct()) #Returns the child with the highest uct

    def roll_out(self, n, s):
        copy_valid_moves = copy.deepcopy(gomoku.valid_moves(n.state))
        random.shuffle(copy_valid_moves)

        while not gomoku.check_win(s[0], n.last_move) and len(copy_valid_moves) != 0: #Randomly picks a possible move out of the list and uses that move till the game is finished
            a = copy_valid_moves.pop()
            is_valid, is_win, s = gomoku.move(s, a)

        return self.who_won(n) #Returns who won

    def BackupValue(self, val, n): #Counts the results of the games
        while n is not None:
            n.N += 1
            if n.state[1] % 2 == self.black:
                n.Q -= val
            else:
                n.Q += val

            n = n.parent

    def move(self, state: GameState, last_move: Move, max_time_to_move: int = 1000) -> Move: #Returns the best_move
        """This is the most important method: the agent will get:
        1) the current state of the game
        2) the last move by the opponent
        3) the available moves you can play (this is a special service we provide ;-) )
        4) the maximum time until the agent is required to make a move in milliseconds [diverging from this will lead to disqualification].
        """

        n_root = mcts(copy.deepcopy(state), None, last_move)

        while max_time_to_move != 0:
            n_leaf = self.FindSpotToExpand(n_root)
            val = self.roll_out(n_leaf, copy.deepcopy(state))
            self.BackupValue(val, n_leaf)
            max_time_to_move -= 1

        return best_move(n_root)

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "Berke Ozmuk (1762463)"
