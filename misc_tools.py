from qiskit import QuantumCircuit, execute, Aer
import numpy as np
from random import random
from copy import deepcopy

class Job ():
    def __init__(self, circuits, counts):
        self._circuits = circuits
        self._counts = counts
        
    def result(self):
        return Results(self._circuits, self._counts)

class Results ():
    def __init__(self, circuits, counts):
        self._circuits = circuits
        self._counts = counts
        
    def get_counts(self,index=0):
        if type(index)==QuantumCircuit:
            index = self._circuits.index(index)
        return self._counts[index]

def product_execute(circuits, shots=1024):
    
    if type(circuits)!=list:
        circuits = [circuits]
    
    counts = []
    for qc in circuits:
        
        n = qc.n_qubits
        m = len((qc).clbits)
        
        sq_qc = [ QuantumCircuit(1,1) for j in range(n) ]
        for j in range(n):
            sq_qc[j].iden(0)
        measure = [ None  for j in range(n) ]
        for gate in qc:
            assert gate[0].num_qubits==1,\
            'Multiqubit gates are not compatible with product_execute'
            name = gate[0].name
            q = gate[1][0].index
            
            if name =='measure':
                assert (q not in measure),\
                'Multiply measured qubits are not compatible with product_execute'
                measure[gate[2][0].index] = q
            else:
                qubit = sq_qc[q].data[0][1]
                sq_qc[q].data  = sq_qc[q].data + [(gate[0], [qubit], [])]
    
        probs = []
        for j in range(n):
            ket = execute(sq_qc[j],Aer.get_backend('statevector_simulator')
                         ).result().get_statevector()
            probs.append( [ np.real(ket[b]*np.conj(ket[b])) for b in [0,1] ] )
    
        counts_qc = {}
        for _ in range(shots):
            string = [ '0' for j in range(m) ]
            for b,q in enumerate(measure):
                if q!=None:
                    string[m-b-1] = str(int(random()<probs[q][1]))
            string = ''.join(string)
            if string in counts_qc:
                counts_qc[string] += 1
            else:
                counts_qc[string] = 1
        
        counts.append(counts_qc)
                
    return Job(circuits,counts)