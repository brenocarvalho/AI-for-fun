from random import shuffle, choice
from puzzle import Puzzle, MovementException
from bisect import insort as insertOrdered

class SolutionNotFoundException(Exception):
    def __str__(self):
        return "SolutionNotFoundException"

class SearchNode:
    def __init__(self, state, parent, transition, f = 0):
        self.state = state
        self.parent = parent
        self.transition = transition
        self._f = f

    def get_path(self):
        out = []
        node = self
        while node is not None:
            out.insert(0, (node.transition, node.state))
            node = node.parent

    def __comp__(self, other):
        return other.f - self.f

class Player(object):
    def __init__(self, limit = None):
        self._limit = limit

    def _find_path(*args, **kargs):
        pass

    def play(self, *args, **kargs):
        if '_sequence' not in dir(self):
            self._sequence = []
            self._find_path(*self._args)
        if len(self._sequence) <= 0:
            raise SolutionNotFoundException

        key, state = self._sequence.pop()
        if key is None: key = 'No move'
        print key
        return state

#-----------------------------------

class TextHumanPlayer(Player):
    d = {'u': 'up',
         'up': 'up',
         'd': 'down',
         'l': 'left',
         'left': 'left',
         'r': 'right',
         'right': 'right'}

    def play(self, puzzle, state):
        user = str(raw_input())
        direction = puzzle.directions[self.d[user]]
        newState = puzzle.move(direction, state)
        if newState is not None:
            return newState
        raise MovementException


class RandomPlayer(Player):
    def __init__(self, limit = None):
        super(RandomPlayer, self).__init__(limit)

    def play(self, puzzle, state):
        if self._limit is not None:
            if self._limit <= 0:
                raise SolutionNotFoundException
            self._limit -= 1
        keys = puzzle.directions.keys()
        try:
            keys.remove(self._lastKey)
        except:
            pass
        nextState = None
        while len(keys) > 0 and nextState is None:
            key = keys.pop(choice(xrange(len(keys))))
            self._lastKey = key
            nextState = state.move(puzzle.directions[key])
        print key
        return nextState

#-----------------------------------

class BreadthSearch(Player):
    def __init__(self, limit = None):
        super(BreadthSearch, self).__init__(limit)


    def _find_path(self, directions, opDirection, victory_test, border, limit):
        for key, parent_indice, state in border:
            if victory_test(state):
                return (key, parent_indice, state)
        newBorder = []
        if limit is None or limit > 0:
            i = 0
            for key, parent_indice, state in border:
                for newKey, direction in directions.items():
                    if key is None or newKey != opDirection[key]:
                        newState = state.move(direction)
                        if newState is not None:
                            newBorder.append((newKey, i, newState))
                i+=1
            if limit is not None:
                limit -= 1
            result = self._find_path(directions, opDirection,\
                                     victory_test, newBorder, limit)
            if result is not None:
                self._sequence.append((result[0], result[2]))
                return border[result[1]]
        del newBorder
        return None


    def play(self, puzzle, state):
        victory_test = lambda *x: puzzle.victory_test(*x)
        if victory_test(state):
            print 'No Move'
            return state

        self._args = puzzle.directions, puzzle.opositeDirectionsKeys,\
                     victory_test, [(None, 0, state)], self._limit
        return super(BreadthSearch, self).play()

#-----------------------------------

class DephSearch(Player):
    def __init__(self, limit = None):
        super(DephSearch, self).__init__(limit)

    def _find_path(self, state, lastKey, directions, opDirection, victory_test, limit):
        if victory_test(state):
            return state
        if limit is None or limit > 0:
            for key, direction in directions.items():
                if lastKey is None or key != opDirection[lastKey]:
                    newState = state.move(direction)
                    if newState is not None:
                        if limit is None:
                            result = self._find_path(newState, key, directions,\
                                                    opDirection, victory_test, limit)
                        else:
                            result = self._find_path(newState, key, directions,\
                                                    opDirection, victory_test, limit - 1)
                        if result is not None:
                            self._sequence.append((key, newState))
                            return state
        return None

    def play(self, puzzle, state):
        victory_test = lambda *x: puzzle.victory_test(*x)
        self._args = state, None, puzzle.directions, puzzle.opositeDirectionsKeys,\
                            victory_test, self._limit
        return super(DephSearch, self).play()

#-----------------------------------

class InteractiveDephSearch(Player):
    def __init__(self, limit = None):
        super(InteractiveDephSearch, self).__init__(limit)

    def _find_path(self, state, directions, opDirection, victory_test):
        level = 1
        while self._limit is None or level < self._limit:
            slaveSearcher = DephSearch(limit = level)
            slaveSearcher._sequence = []
            slaveSearcher._find_path(state, None, directions, opDirection, victory_test, level)
            if len(slaveSearcher._sequence):
                self._sequence = slaveSearcher._sequence
                return
            level += 1
        raise SolutionNotFoundException
            
    def play(self, puzzle, state):
        victory_test = lambda *x: puzzle.victory_test(*x)
        self._args = state, puzzle.directions, puzzle.opositeDirectionsKeys, victory_test
        return super(InteractiveDephSearch, self).play()

#-----------------------------------

class BidirectionalSearch(Player):
    def __init__(self, limit = None):
        super(BidirectionalSearch, self).__init__(limit/2+1)

    def _expand_border(self, border, directions):
        newBorder = {}

        for state in border.keys():
            for newKey, direction in directions.items():
                if newKey != border[state][0]:
                    newState = state.move(direction)
                    if newState is not None:
                        newBorder[newState] = (newKey, state)
        return newBorder

    def victory_test(self, border, objBorder):
        for state in border.keys():
            if objBorder.has_key(state):
                    return state
        return None

    def _find_path(self, border, directions, opDirections, objBorder, limit):
        if limit is None or limit > 0:
            state = self.victory_test(border, objBorder)
            if state is not None:
                self._sequence.append((border[state][0], state))
                return border[state][1], objBorder[state][1], border[state][0]
            else:
                newObjBorder = self._expand_border(objBorder, directions)

                vTestResult = self.victory_test(border, newObjBorder)

                if vTestResult is None:
                    if limit is not None:
                        limit -= 1
                    newBorder = self._expand_border(border, directions)
                    args = newBorder, directions, opDirections, newObjBorder, limit
                    initState, objState, objDirection = self._find_path(*args)
                    del newBorder
                else:
                    initState = objState = vTestResult
                    self._sequence.insert(0, (opDirections[ newObjBorder[objState][0] ], objState))
                    objDirection, objState = newObjBorder[objState]
                del newObjBorder
                self._sequence.append((border[initState][0], initState))
                self._sequence.insert(0, (opDirections[ objDirection ], objState))
                return border[initState][1], objBorder[objState][1], objBorder[objState][0]
        else:
            raise SolutionNotFoundException

    def play(self, puzzle, state):
        if puzzle.victory_test(state):
            print "No move"
            return state

        objectivesBorder = {obj:(None, None) for obj in puzzle.objectives}
        initBorder = self._expand_border({state:(None, None)}, puzzle.directions)
        self._args = initBorder, puzzle.directions,\
                     puzzle.opositeDirectionsKeys, objectivesBorder, self._limit
        s = super(BidirectionalSearch, self).play()
        #for state, direction in self._sequence: print direction, state
        #raw_input()
        return s

#-----------------------------------

class AStarSearch(Player):
    def __init__(self, limit = None, heuristic = lambda x: 0):
        super(AStarSearch, self).__init__(limit)
        self._heuristic = heuristic
        self._f = lambda parent, state: parent._f + heuristic(state)

    def _find_path(self, frontier, lastKey, directions, opDirection, victory_test, limit, heuristic):
        a = 0
        while len(frontier) != 0:
            node = frontier.pop(0)
            if victory_test(node.state):
                self._sequence = node.get_path()
                return node
            for key, direction in directions.items():
                if lastKey is None or key != opDirection[lastKey]:
                    newState = node.state.move(direction)
                    if newState is not None:
                        newNode = SearchNode( newState, node.state, key, self._f(node, newState))
                        if newState is not None:
                            insertOrdered(frontier, newNode)
                        for i in frontier: print i.state,

        return None

    def play(self, puzzle, state):
        victory_test = lambda *x: puzzle.victory_test(*x)
        self._args = [SearchNode(state, None, None, self._heuristic(state))], None, puzzle.directions,\
                     puzzle.opositeDirectionsKeys, victory_test, self._limit, self._f
        return super(AStarSearch, self).play()

