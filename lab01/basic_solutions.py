import itertools
import sympy as sp

l1, l2, l3 = sp.symbols('l1 l2 l3')

constraints = [
    (l1 + l2 - 65, "C1"),
    (2*l2 + 3*l3 - 150, "C2"),
    (4*l1 + 4*l2 + l3 - 200, "C3"),
    (l1, "l1=0"),
    (l2, "l2=0"),
    (l3, "l3=0")
]

solutions = []

for chosen in itertools.combinations(constraints, 3):
    equations = [c[0] for c in chosen]
    names = [c[1] for c in chosen]
    answer = sp.solve(equations, (l1, l2, l3), dict=True)
    if len(answer) == 1:
        sol = answer[0]
        values = (sol[l1], sol[l2], sol[l3])
        feasible = (
            values[0] >= 0 and
            values[1] >= 0 and
            values[2] >= 0 and
            values[0] + values[1] >= 65 and
            2*values[1] + 3*values[2] >= 150 and
            4*values[0] + 4*values[1] + values[2] >= 200
        )
        objective = sum(values)
        solutions.append((names, values, objective, feasible))

print("-" * 75)
print("                         BASIC SOLUTIONS")
print("-" * 75)
print(f"{'Active Constraints':<25} {'Solution':<22} {'Objective':>12} {'Status':>12}")
print("-" * 75)
for names, values, objective, feasible in solutions:
    constraints_used = ", ".join(names)
    solution = f"({values[0]}, {values[1]}, {values[2]})"
    status = "FEASIBLE" if feasible else "INFEASIBLE"
    print(f"{constraints_used:<25} {solution:<22} {str(objective):>12} {status:>12}")
print("-" * 75)