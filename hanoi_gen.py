from collections import namedtuple
from subprocess import call
from os import path

Action = namedtuple('Action', ['t', 's', 'w', 'p', 'W', 'P'])
Stone = namedtuple('Stone', ['t', 's', 'w', 'p'])

class Variable:
    def __init__(self, v, variable_no):
        self._v = v
        self._variable_no = variable_no

    @property
    def v(self):
        return self._v

    @property
    def variable_no(self):
        return self._variable_no

    def __neg__(self):
        return Variable(self._v, -self._variable_no)

    def __str__(self):
        return "{0}:{1}".format(self.v, self.variable_no)

    def __repr__(self):
        return str(self)

class HanoiEncoder:

    def __init__(self, stones, towers):
        self._variable_no = 1 
        self._variable_to_number = {}
        self._number_to_variable = {}

        self._stones = stones
        self._towers = towers

    def get_action(self, t, s, w, p, W, P):
        a = Action(t, s, w, p, W, P)
        return self._get_variable(a)

    def get_stone(self, t, s, w, p):
        s = Stone(t, s, w, p)
        return self._get_variable(s) 

    def _get_variable(self, v):
        if v not in self._variable_to_number:
            self._variable_to_number[v] = Variable(v, self._variable_no)
            self._variable_no += 1
        return self._variable_to_number[v]

    def encode_state(self, t):
        # ALO
        for s in range(self._stones):
            clause = []
            for w in range(self._towers):
                for p in range(self._stones):
                    clause.append(self.get_stone(t, s, w, p))
            yield clause

        # AMO
        for s in range(self._stones):
            for w in range(self._towers):
                for p in range(self._stones):
                    for W in range(self._towers):
                        for P in range(self._stones):
                            if (w, p) == (W, P):
                                continue
                            yield [-self.get_stone(t, s, w, p), -self.get_stone(t, s, W, P)]

        # At most one stone at a single pos.
        for s in range(self._stones):
            for w in range(self._towers):
                for p in range(self._stones):
                    for S in range(self._stones):
                        if s == S:
                            continue
                        yield [-self.get_stone(t, s, w, p), -self.get_stone(t, S, w, p)]

        # No smaller stone under s.
        for s in range(self._stones):
            for w in range(self._towers):
                for p in range(1, self._stones):
                    for S in range(s):
                        yield [-self.get_stone(t, s, w, p), -self.get_stone(t, S, w, p - 1)]
        
        # A bigger stone under s
        for s in range(self._stones):
            clause = []
            for w in range(self._towers):
                for p in range(1, self._stones):
                    clause = [-self.get_stone(t, s, w, p)]
                    for S in range(s + 1, self._stones):
                        clause.append(self.get_stone(t, S, w, p - 1))
                    yield clause

    def encode_initial_state(self, w):
        yield from self._encode_single_tower(0, w)

    def encode_final_state(self, t, w):
        yield from self._encode_single_tower(t, w)

    def _encode_single_tower(self, t, w):
        for s in range(self._stones):
            yield [self.get_stone(t, s, w, self._stones - s - 1)]

    def encode_action(self, t):
        # AMO
        for s in range(self._stones):
            for w in range(self._towers):
                for p in range(self._stones):
                    for W in range(self._towers):
                        for P in range(self._stones):
                            for ss in range(self._stones):
                                for ww in range(self._towers):
                                    for pp in range(self._stones):
                                        for WW in range(self._towers):
                                            for PP in range(self._stones):
                                                if (s, w, p, W, P) == (ss, ww, pp, WW, PP):
                                                    continue
                                                yield [-self.get_action(t, s, w, p, W, P), -self.get_action(t, ss, ww, pp, WW, PP)]
        clause = []
        # ALO
        for s in range(self._stones):
            for w in range(self._towers):
                for p in range(self._stones):
                    for W in range(self._towers):
                        for P in range(self._stones):
                            clause.append(self.get_action(t, s, w, p, W, P))
        yield clause

        # Transition
        clause = []
        for s in range(self._stones):
            for w in range(self._towers):
                for p in range(self._stones):
                    for W in range(self._towers):
                        for P in range(self._stones):
                            yield [-self.get_action(t, s, w, p, W, P), self.get_stone(t, s, w, p)]
                            yield [-self.get_action(t, s, w, p, W, P), self.get_stone(t + 1, s, W, P)]

                            # Transfer the rest of the state, frame axioms.
                            # This one can be improved vastly!
                            for ss in range(self._stones):
                                if s == ss:
                                    continue
                                for ww in range(self._towers):
                                    for pp in range(self._stones):
                                        yield [-self.get_action(t, s, w, p, W, P), -self.get_stone(t, ss, ww, pp), self.get_stone(t + 1, ss, ww, pp)]


def format_clauses(f, clauses, only_numbers=True):
    for clause in clauses:
        f.write(" ".join(map(
            lambda var: str(var.variable_no) if only_numbers else str(var),
            clause + [Variable(None, 0)]
        )))
        f.write("\n")

class HanoiPlanner:
    
    def __init__(self, stones, towers):
        self._stones = stones
        self._towers = towers
        self._he = HanoiEncoder(self._stones, self._towers)

    def generate_plan_formula(self, length):
        he = self._he
        yield from he.encode_initial_state(0)
        for t in range(length):
            yield from he.encode_state(t)
            yield from he.encode_action(t)
        yield from he.encode_final_state(length, 1)
        yield from he.encode_state(length)

    def print_solution(self, length, valuation):
        he = self._he
        for t in range(length + 1):
            state = [[-1] * self._stones] * self._towers
            for i in range(len(state)):
                state[i] = list(state[i])
            for s in range(self._stones):
                for w in range(self._towers):
                    for p in range(self._stones):
                        if valuation[he.get_stone(t, s, w, p).variable_no]:
                            print("{0}: Stone {1} at tower {2} at position {3}.".format(t, s, w, p))
                            state[w][p] = s
            print(state)
            if t == length:
                break
            for s in range(self._stones):
                for w in range(self._towers):
                    for p in range(self._stones):
                        for W in range(self._towers):
                            for P in range(self._stones):
                                if valuation[he.get_action(t, s, w, p, W, P).variable_no]:
                                    print("{0}: Move stone {1} at tower {2} at position {3} to tower {4} to position {5}.".format(t, s, w, p, W, P))

if __name__ == "__main__":
    stones = 3
    towers = 3
    length = 7
    tmp_dir = '.'

    hp = HanoiPlanner(stones, towers)
    # print(hp.generate_plan_formula(length, False))
    fla_path = path.join('.', 'hanoi.cnf')
    solution_path = path.join(tmp_dir, 'hanoi.out')
    with open(fla_path, 'w') as f:
        format_clauses(f, hp.generate_plan_formula(length))
    call('minisat.exe {0} {1}'.format(fla_path, solution_path), shell=True)
    with open(solution_path, 'r') as f:
        lines = f.readlines() 
        sat = lines[0].strip()
        if sat != "SAT":
            print("Solution not found.")
            exit(0)
        solution = map(int, lines[1].strip().split(' '))

    valuation = {}
    for literal in solution:
        if literal < 0:
            valuation[-literal] = False
        else:
            valuation[literal] = True

    hp.print_solution(length, valuation)


