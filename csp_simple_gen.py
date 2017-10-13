from sys import argv

def encode(i, j, n):
    return i * n + j + 1

if __name__ == "__main__":
    csp_variables = 2
    values = 5
    sat_variables = csp_variables * values
    clauses = []

    # AMO value
    for j in range(values):
        for i in range(csp_variables):
            for jj in range(values):
                if j == jj:
                    continue
                clauses.append([-encode(i, j, values), -encode(i, jj, values)])

    # ALO value
    for i in range(csp_variables):
        clause = []
        for j in range(values):
            clause.append(encode(i, j, values))
        clauses.append(clause)

    # Business logic
    # Constraint 1
    for j_1 in range(values):
        clause = [-encode(0, j_1, values)]
        for j_2 in range(values):
            if 7 <= j_1 + 1 + j_2 + 1 <= 11:
                clause.append(encode(1, j_2, values))
        clauses.append(clause)

    # Constraint 2
    for j_1 in range(values):
        clause = [-encode(0, j_1, values)]
        for j_2 in range(values):
            if (j_1 + 1)**2 - (j_2 + 1)**2 >= 13:
                clause.append(encode(1, j_2, values))
        clauses.append(clause)

    print("p cnf {0} {1}".format(sat_variables, len(clauses)))
    print("\n".join(
        map(
            lambda clause: " ".join(map(lambda v: str(v), clause + [0])), 
            clauses
        )
    ))

