from sys import argv

def encode(i, j, n):
    return i * (n - 1) + j + 1

if __name__ == "__main__":
    n = int(argv[1])
    # x_{i, j} means pigeon i is in the hole j
    variables = n * (n - 1)
    clauses = []

    # AMO a.k.a at most one
    # in each hole j there is at most one pigeon i
    # if pigeon i is in hole j, then no other pigeon ii is in hole j, i.e. x_{i, j} => -x_{ii, j'} for each ii != i
    # notice a => b is equivalent to -a or b
    for j in range(n - 1):
        for i in range(n):
            for ii in range(n):
                if i == ii:
                    continue
                clauses.append([-encode(i, j, n), -encode(ii, j, n)])

    # ALO a.k.a at least one
    # for each pigeon i there should be a hole j
    for i in range(n):
        clause = []
        for j in range(n - 1):
            clause.append(encode(i, j, n))
        clauses.append(clause)

    # Observe that a single pigeon may be assigned to two holes ;).
    # When modelling a problem in SAT such things occur frequently!

    print("p cnf {0} {1}".format(variables, len(clauses)))
    print("\n".join(
        map(
            lambda clause: " ".join(map(lambda v: str(v), clause + [0])), 
            clauses
        )
    ))

