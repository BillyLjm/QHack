#! /usr/bin/python3

import sys
import pennylane as qml
import autograd.numpy as np


def find_excited_states(H):
    """
    Fill in the missing parts between the # QHACK # markers below. Implement
    a variational method that can find the three lowest energies of the provided
    Hamiltonian.

    Args:
        H (qml.Hamiltonian): The input Hamiltonian

    Returns:
        The lowest three eigenenergies of the Hamiltonian as a comma-separated string,
        sorted from smallest to largest.
    """

    energies = np.zeros(3)

    # QHACK #
    ## Overlap Cost Function
    ## This measures the energy and state overlap of each ansatz independently
    ## then combines them classically to give a new cost function

    def variational_ansatz(params, wires):
        """variational ansatz circuit"""
        for param in params:
            qml.broadcast(qml.Rot, wires, pattern="single", parameters=param)
            qml.broadcast(qml.CNOT, wires, pattern="ring")

    # calculate energy of parameters/ansatz
    num_qubits = len(H.wires)
    dev1 = qml.device("default.qubit", wires=num_qubits)
    energy = qml.ExpvalCost(variational_ansatz, H, dev1)

    # calculate overlap of 2 parameters/ansatz
    dev2 = qml.device("default.qubit", wires=2*num_qubits+1)
    @qml.qnode(dev2)
    def overlap(paramsX, paramsY):
        """calculate overlap of 2 parameters/ansatz"""
        wires = range(2*num_qubits+1)
        variational_ansatz(paramsX, wires[:num_qubits])
        variational_ansatz(paramsY, wires[num_qubits:-1])
        qml.Hadamard(wires=wires[-1])
        for i in range(num_qubits):
            qml.CSWAP(wires=(wires[-1], wires[i], wires[i+num_qubits]))
        qml.Hadamard(wires=wires[-1])
        return qml.expval(qml.PauliZ(wires=wires[-1]))

    # fixed variables
    opt = qml.MomentumOptimizer(0.1)
    overlap_weight = 50 # weight of state overlap in cost function
    num_layers = 2 # number of layers in variational ansatz
    num_iter = 500 # number of VQE iterations
    num_eigen = 3 # number of eigen-energies to output
    threshold = 1e-8 # threshold to stop

    def cost_fn(params, overlap_params):
        """training cost function. Includes H and state overlap"""
        cost = energy(params)
        for i in overlap_params:
            cost += overlap_weight * overlap(params, i)
        return cost

    # VQE
    prev_params = []
    for i in range(num_eigen):
        params = np.random.uniform(size=(num_layers, num_qubits, 3))

        for _ in range(num_iter):
            params, prev_cost = opt.step_and_cost(lambda x: cost_fn(x, prev_params), params)
            cost = cost_fn(params, prev_params)
            if np.abs(cost - prev_cost) < threshold:
                break

            # # print progress
            # if _ % 20 == 0:
            #     print('Iteration = {:},  cost = {:.8f}'.format(_, cost))

        energies[i] = energy(params)
        prev_params.append(params)

    # QHACK #

    return ",".join([str(E) for E in energies])


def pauli_token_to_operator(token):
    """
    DO NOT MODIFY anything in this function! It is used to judge your solution.

    Helper function to turn strings into qml operators.

    Args:
        token (str): A Pauli operator input in string form.

    Returns:
        A qml.Operator instance of the Pauli.
    """
    qubit_terms = []

    for term in token:
        # Special case of identity
        if term == "I":
            qubit_terms.append(qml.Identity(0))
        else:
            pauli, qubit_idx = term[0], term[1:]
            if pauli == "X":
                qubit_terms.append(qml.PauliX(int(qubit_idx)))
            elif pauli == "Y":
                qubit_terms.append(qml.PauliY(int(qubit_idx)))
            elif pauli == "Z":
                qubit_terms.append(qml.PauliZ(int(qubit_idx)))
            else:
                print("Invalid input.")

    full_term = qubit_terms[0]
    for term in qubit_terms[1:]:
        full_term = full_term @ term

    return full_term


def parse_hamiltonian_input(input_data):
    """
    DO NOT MODIFY anything in this function! It is used to judge your solution.

    Turns the contents of the input file into a Hamiltonian.

    Args:
        filename(str): Name of the input file that contains the Hamiltonian.

    Returns:
        qml.Hamiltonian object of the Hamiltonian specified in the file.
    """
    # Get the input
    coeffs = []
    pauli_terms = []

    # Go through line by line and build up the Hamiltonian
    for line in input_data.split("S"):
        line = line.strip()
        tokens = line.split(" ")

        # Parse coefficients
        sign, value = tokens[0], tokens[1]

        coeff = float(value)
        if sign == "-":
            coeff *= -1
        coeffs.append(coeff)

        # Parse Pauli component
        pauli = tokens[2:]
        pauli_terms.append(pauli_token_to_operator(pauli))

    return qml.Hamiltonian(coeffs, pauli_terms)


if __name__ == "__main__":
    # DO NOT MODIFY anything in this code block

    # Turn input to Hamiltonian
    H = parse_hamiltonian_input(sys.stdin.read())

    # Send Hamiltonian through VQE routine and output the solution
    lowest_three_energies = find_excited_states(H)
    print(lowest_three_energies)
