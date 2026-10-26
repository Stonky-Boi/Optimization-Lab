import math

EPSILON = 1e-9

def read_problem():
    variable_count = int(input("Enter number of variables: "))
    constraint_count = int(input("Enter number of constraints: "))
    if variable_count <= 0 or constraint_count <= 0:
        raise ValueError("Numbers of variables and constraints must be positive.")

    print("Enter the constraint matrix (including RHS):")
    tableau = []
    for _ in range(constraint_count):
        row = list(map(float, input().split()))
        if len(row) != variable_count + 1:
            raise ValueError("Invalid number of values in constraint row.")
        if not all(math.isfinite(value) for value in row):
            raise ValueError("Constraint values must be finite.")
        if row[-1] < 0:
            row = [-value for value in row]
        tableau.append(row)

    print("Enter the cost function coefficients:")
    objective = list(map(float, input().split()))
    if len(objective) != variable_count:
        raise ValueError("Invalid number of objective coefficients.")
    if not all(math.isfinite(value) for value in objective):
        raise ValueError("Objective coefficients must be finite.")

    optimization_type = input("Enter optimization type (max/min): ").strip().lower()
    if optimization_type not in ("max", "min"):
        raise ValueError("Optimization type must be max or min.")

    big_m = float(input("Enter the value of M: "))
    if not math.isfinite(big_m) or big_m <= 0:
        raise ValueError("M must be a positive finite number.")

    return (variable_count, constraint_count, tableau, objective, optimization_type, big_m)

def create_initial_tableau(variable_count, constraint_count, constraints):
    total_variables = variable_count + constraint_count

    tableau = []
    for i in range(constraint_count):
        row = constraints[i][:variable_count]
        for j in range(constraint_count):
            if i == j:
                row.append(1.0)
            else:
                row.append(0.0)
        row.append(constraints[i][-1])
        tableau.append(row)

    basis = []
    for i in range(constraint_count):
        basis.append(variable_count + i)

    return tableau, basis, total_variables

def calculate_reduced_costs(tableau, basis, costs, total_variables):
    reduced_costs = []
    for j in range(total_variables):
        value = costs[j]
        for i in range(len(basis)):
            value -= costs[basis[i]] * tableau[i][j]
        reduced_costs.append(value)
    return reduced_costs

def simplex(tableau, basis, costs, total_variables):
    iteration = 0

    while True:
        iteration += 1
        reduced_costs = calculate_reduced_costs(tableau, basis, costs, total_variables)

        entering_variable = -1
        maximum_reduced_cost = EPSILON
        for j in range(total_variables):
            if reduced_costs[j] > maximum_reduced_cost:
                maximum_reduced_cost = reduced_costs[j]
                entering_variable = j
        if entering_variable == -1:
            break

        leaving_row = -1
        minimum_ratio = float("inf")
        for i in range(len(tableau)):
            pivot_element = tableau[i][entering_variable]
            if pivot_element > EPSILON:
                ratio = tableau[i][-1] / pivot_element
                if ratio < minimum_ratio - EPSILON:
                    minimum_ratio = ratio
                    leaving_row = i
                elif abs(ratio - minimum_ratio) <= EPSILON:
                    if leaving_row == -1 or basis[i] < basis[leaving_row]:
                        leaving_row = i
        if leaving_row == -1:
            return False, iteration - 1

        pivot_element = tableau[leaving_row][entering_variable]
        for j in range(total_variables + 1):
            tableau[leaving_row][j] /= pivot_element

        for i in range(len(tableau)):
            if i == leaving_row:
                continue
            factor = tableau[i][entering_variable]
            for j in range(total_variables + 1):
                tableau[i][j] -= factor * tableau[leaving_row][j]
        basis[leaving_row] = entering_variable

    return True, iteration - 1

def solve():
    (variable_count, constraint_count, constraints, objective, optimization_type, big_m) = read_problem()
    original_objective = objective[:]
    if optimization_type == "min":
        objective = [-value for value in objective]

    tableau, basis, total_variables = create_initial_tableau(variable_count, constraint_count, constraints)
    costs = objective[:]
    for i in range(constraint_count):
        costs.append(-big_m)

    bounded, iterations = simplex(tableau, basis, costs, total_variables)
    if not bounded:
        print("The linear program is unbounded.")
        return

    solution = [0.0] * total_variables
    for i in range(constraint_count):
        solution[basis[i]] = tableau[i][-1]
    for j in range(variable_count, total_variables):
        if solution[j] > EPSILON:
            print("The original linear program is infeasible.")
            return

    optimal_value = 0.0
    for j in range(variable_count):
        optimal_value += original_objective[j] * solution[j]

    print("\nOptimal solution found!")
    print("Iterations:", iterations)
    for j in range(variable_count):
        print(f"x{j + 1} = {solution[j]:.4f}")
    for j in range(constraint_count):
        print(f"y{j + 1} = {solution[variable_count + j]:.4f}")
    print(f"Optimal objective value = {optimal_value:.4f}")

if __name__ == "__main__":
    try:
        solve()
    except ValueError as error:
        print("Input error:", error)