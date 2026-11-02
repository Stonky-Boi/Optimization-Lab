from fractions import Fraction

MAX_ITERATIONS = 100

def create_initial_tableau():
    tableau = [
        [Fraction(1, 4), -8, -1, 9, 1, 0, 0, 0],
        [Fraction(1, 2), -12, Fraction(-1, 2), 3, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 1]
    ]
    basis = [4, 5, 6]
    costs = [Fraction(3, 4), -20, Fraction(1, 2), -6, 0, 0, 0]
    return tableau, basis, costs

def calculate_reduced_costs(tableau, basis, costs):
    reduced_costs = []
    for j in range(len(costs)):
        z_j = Fraction(0)
        for i in range(len(basis)):
            z_j += costs[basis[i]] * tableau[i][j]
        reduced_costs.append(costs[j] - z_j)
    return reduced_costs

def choose_entering_variable(reduced_costs):
    entering_variable = -1
    maximum_reduced_cost = Fraction(0)
    for j, value in enumerate(reduced_costs):
        if value > maximum_reduced_cost:
            maximum_reduced_cost = value
            entering_variable = j
    return entering_variable

def calculate_perturbed_ratio(row, entering_variable):
    pivot_element = row[entering_variable]
    if pivot_element <= 0:
        raise ValueError("Pivot element must be positive.")
    return tuple(value / pivot_element for value in [row[-1]] + row[:-1])

def choose_leaving_row(tableau, basis, entering_variable, lexicographic):
    leaving_row = -1
    minimum_ratio = None
    for i, row in enumerate(tableau):
        pivot_element = row[entering_variable]
        if pivot_element <= 0:
            continue
        if lexicographic:
            ratio = calculate_perturbed_ratio(row, entering_variable)
        else:
            ratio = (row[-1] / pivot_element,)
        if minimum_ratio is None or ratio < minimum_ratio:
            minimum_ratio = ratio
            leaving_row = i
        elif ratio == minimum_ratio and basis[i] < basis[leaving_row]:
            leaving_row = i
    return leaving_row, minimum_ratio

def perform_pivot(tableau, basis, entering_variable, leaving_row):
    pivot_element = tableau[leaving_row][entering_variable]
    column_count = len(tableau[0])
    tableau[leaving_row] = [value / pivot_element for value in tableau[leaving_row]]
    for i in range(len(tableau)):
        if i == leaving_row:
            continue
        factor = tableau[i][entering_variable]
        for j in range(column_count):
            tableau[i][j] -= factor * tableau[leaving_row][j]
    basis[leaving_row] = entering_variable

def calculate_objective_value(tableau, basis, costs):
    objective_value = Fraction(0)
    for i in range(len(basis)):
        objective_value += costs[basis[i]] * tableau[i][-1]
    return objective_value

def format_polynomial(coefficients):
    terms = []
    for power, coefficient in enumerate(coefficients):
        if coefficient == 0:
            continue
        if power == 0:
            term = f"({coefficient})"
        elif power == 1:
            term = f"({coefficient})*eps"
        else:
            term = f"({coefficient})*eps^{power}"
        terms.append(term)
    return " + ".join(terms) if terms else "0"

def print_iteration(iteration, tableau, basis, costs, lexicographic):
    print(f"\nIteration {iteration}")
    print("Basis:", tuple(index + 1 for index in basis))
    reduced_costs = calculate_reduced_costs(tableau, basis, costs)
    print("Reduced costs (c_j - z_j):")
    for j, value in enumerate(reduced_costs):
        print(f"x{j + 1}: {value}", end="  ")
    print("\nObjective value:", calculate_objective_value(tableau, basis, costs))
    return reduced_costs

def simplex(tableau, basis, costs, lexicographic):
    visited_bases = {}
    basis_history = []

    for iteration in range(MAX_ITERATIONS + 1):
        current_basis = tuple(basis)

        if current_basis in visited_bases:
            cycle_start = visited_bases[current_basis]
            cycle = basis_history[cycle_start:] + [current_basis]
            print("\nCycling detected!")
            for current in cycle:
                print(tuple(index + 1 for index in current))
            return "cycling", iteration

        visited_bases[current_basis] = iteration
        basis_history.append(current_basis)
        reduced_costs = print_iteration(iteration, tableau, basis, costs, lexicographic)
        entering_variable = choose_entering_variable(reduced_costs)
        if entering_variable == -1:
            return "optimal", iteration
        leaving_row, minimum_ratio = choose_leaving_row(tableau, basis, entering_variable, lexicographic)
        if leaving_row == -1:
            return "unbounded", iteration
        print(f"Entering variable: x{entering_variable + 1}")
        print(f"Leaving variable: x{basis[leaving_row] + 1}")
        perform_pivot(tableau, basis, entering_variable, leaving_row)

    return "iteration_limit", MAX_ITERATIONS

def print_solution(tableau, basis, costs):
    solution = [Fraction(0)] * len(costs)
    for i in range(len(basis)):
        solution[basis[i]] = tableau[i][-1]
    print("\nOptimal solution:")
    for j, value in enumerate(solution):
        print(f"x{j + 1} = {value}")
    print("Optimal objective value:", calculate_objective_value(tableau, basis, costs))

def solve():
    tableau, basis, costs = create_initial_tableau()
    print("\nORIGINAL SIMPLEX")
    original_tableau = [row[:] for row in tableau]
    original_basis = basis[:]
    status, iterations = simplex(original_tableau, original_basis, costs, False)
    print(f"Status: {status}")
    print(f"Iterations: {iterations}")
    print("\nPERTURBED SIMPLEX")
    perturbed_tableau = [row[:] for row in tableau]
    perturbed_basis = basis[:]
    status, iterations = simplex(perturbed_tableau, perturbed_basis, costs, True)
    print(f"Status: {status}")
    print(f"Iterations: {iterations}")
    if status == "optimal":
        print_solution(perturbed_tableau, perturbed_basis, costs)

if __name__ == "__main__":
    solve()