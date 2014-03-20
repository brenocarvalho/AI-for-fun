'''
Written by Breno Carvalho
This code implements a simple numeric puzzle and (will implements)
also some AI algoritms to solve it
'''

from artificialAgents import *

class MovementException(Exception):
    def __str__(self):
        return 'Invalid movement'

class Puzzle:
    def _up(self):
        n_pos = self._zeroPos - self._boardSideSize
        if n_pos < 0: raise MovementException
        return n_pos

    def _down(self):
        n_pos = self._zeroPos + self._boardSideSize
        if n_pos >= self._boardSideSize**2: raise MovementException
        return n_pos

    def _left(self):
        n_pos = self._zeroPos-1
        if (self._zeroPos / self._boardSideSize) != \
               (n_pos / self._boardSideSize): raise MovementException
        return n_pos

    def _right(self):
        n_pos = self._zeroPos+1
        if (self._zeroPos / self._boardSideSize) != \
               (n_pos / self._boardSideSize): raise MovementException
        return n_pos

    directions = {'up':    _up,
                  'down':  _down,
                  'left':  _left,
                  'right': _right}

    opositeDirectionsKeys = {'up':    'down',
                             'down':  'up',
                             'left':  'right',
                             'right': 'left'  }

    def __init__(self, boardSideSize = 3, objectives = []):
        self._boardSideSize = boardSideSize
        state = range(boardSideSize**2)
        self.state = PuzzleState(state, boardSideSize, 0)
        self.set_objectives(*objectives)


    def shuffle(self):
        self.state = self.state.shuffle()


    def set_objectives(self, *states):
        self.objectives = []
        self.add_objectives(*states)


    def add_objectives(self, *states):
        for state in states:
            assert state.__class__ is PuzzleState
        self.objectives.extend(states)


    def victory_test(self, state):
        totalSize = self._boardSideSize**2
        for objective in self.objectives:
            if state == objective:
                return True
        return False

    def move(self, direction, state):
        return state.move(direction)

    def __str__(self):
        return "[Puzzle]\n"+str(self.state)

class PuzzleState:
    def __init__(self, numbers, boardSideSize, zeroPos):
        self._numbers = tuple(numbers)
        self._boardSideSize = boardSideSize
        self._zeroPos = zeroPos

    def __hash__(self):
        return hash(self._numbers)

    def __eq__(self, other):
        return self._numbers == other._numbers

    def shuffle(self):
        numbers = list(self._numbers)
        shuffle(numbers)
        posZero = numbers.index(0)
        return PuzzleState(numbers, self._boardSideSize, posZero)

    def move(self, direction):
        try:
            neighbour = direction(self)
        except MovementException:
            return None
        numbers = list(self._numbers)
        
        numbers[self._zeroPos] = numbers[neighbour]
        numbers[neighbour] = 0
        posZero = neighbour
        return PuzzleState(numbers, self._boardSideSize, posZero)

    def __str__(self):
        out = []
        i = 0
        for row in xrange(self._boardSideSize):
            for col in xrange(self._boardSideSize):
                if(self._numbers[i] == 0):
                    out.append('*')    
                else:
                    out.append(str(self._numbers[i]))
                out.append('  ')
                i += 1
            out.append('\n')
        return ''.join(out)

class PuzzleInterface(object):
    def __init__(self, agent, sideSize = 3):
        self.puzzle = Puzzle(sideSize, [PuzzleState([0,1,2,3,4,5,6,7,8], 3, 0)])
        self.agent = agent

    def start(self):
        self.puzzle.shuffle()
        pass

class TextualPuzzleInterface(PuzzleInterface):
    def __init__(self, agent, sideSize = 3):
        super(TextualPuzzleInterface, self).__init__(agent)
    
    def start(self):
        super(TextualPuzzleInterface, self).start()    
        print '''Instructions:
        You should press 'u', 'd', 'l' or 'r' to move the '*' to a near position \
up, down, left or right it. You should order this board from left to right and up\
 to botton, '*' must end at the first position.
        '''
        #print self.puzzle
        state = self.puzzle.state
        state = PuzzleState([5,1,3,7,4,6,0,2,8], 3, 6)
        #state = PuzzleState([1,4,2,0,3,5,6,7,8], 3, 3)
        #state = PuzzleState([0,1,2,3,4,5,6,7,8], 3, 0)
        print state
        counter = 0
        while(True):
            try:
                print 'Your move: ',
                #try:
                state = self.agent.play(self.puzzle, state)
                if self.puzzle.victory_test(state):
                    print state
                    print "You won!!! With", counter, "steps!"
                    exit(0)
                counter += 1
                #except Exception as ex:
                #    print ex
                print state
            except KeyboardInterrupt:
                print '\nBye.'
                raise SolutionNotFoundException, 'User stopped the execution'
            #except KeyError:
            #    print 'Press Ctrl+C if you wanna end this game.'
            except SolutionNotFoundException as e:
                print '\n', e
                exit()

def manhattanHeuristic(state):
    h = 0
    for i in range(len(state._numbers)):
        if state._numbers[i] != 0:
            dist = abs( - i)
            h += abs((state._numbers[i] % state._boardSideSize) - (i % state._boardSideSize)) +\
                 abs((state._numbers[i] / state._boardSideSize) - (i / state._boardSideSize))
    return h

if __name__ == '__main__':
#    agent = RandomPlayer(100)
#    agent = BreadthSearch(50)
    agent = DephSearch(limit = 50)
#    agent = InteractiveDephSearch(25)
#    agent = BidirectionalSearch(50)
#    agent = TextHumanPlayer()
#    agent = AStarSearch(heuristic = manhattanHeuristic)
#    print agent.__name__
    game = TextualPuzzleInterface(sideSize = 3, agent = agent)
    game.start();
