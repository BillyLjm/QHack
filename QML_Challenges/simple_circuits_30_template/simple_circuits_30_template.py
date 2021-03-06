#! /usr/bin/python3
import pennylane as qml
from pennylane import numpy as np
import sys


def simple_circuits_30(angle):
    """The code you write for this challenge should be completely contained within this function
        between the # QHACK # comment markers.

    In this function:
        * Rotate a qubit around the y-axis by angle
        * Measure the expectation value of `PauliX`

    Args:
        angle (float): how much to rotate a state around the y-axis

    Returns:
        float: the expectation value of a PauliX measurement
    """
    dev = qml.device('default.qubit', wires=1)

    @qml.qnode(dev)
    def simplecircuit(param):
        qml.RY(param, wires=0)
        return qml.expval(qml.PauliX(0))

    x_expectation = simplecircuit(angle)
    return x_expectation


if __name__ == "__main__":
    # DO NOT MODIFY anything in this code block

    # Load and process input
    angle_str = sys.stdin.read()
    angle = float(angle_str)

    ans = simple_circuits_30(angle)

    if isinstance(ans, np.tensor):
        ans = ans.item()

    if not isinstance(ans, float):
        raise TypeError("the simple_circuits_30 function needs to return a float")

    print(ans)