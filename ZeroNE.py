import numpy as np
from qiskit import QuantumCircuit
from scipy.optimize import curve_fit

class ZeroNE:
    def folding(self,qc:QuantumCircuit,i:int):
        ''' Given an operator G at the position i of the circuit qc,
          the function generates the folding G->G G^(-1)G'''
        instr, qargs, cargs = qc.data[i]
        qc.data.insert(i,(instr, 
                         qargs, 
                         cargs))
        qc.data.insert(i+1,(instr.inverse(), 
                        qargs, 
                        cargs))
        return qc
    def adapt_positions(self,original_positions, inserted_index):
        '''Readapts the positions of the original operators original_positions after the folding at the positions inserted_index'''
        return [pos + 2 if pos > inserted_index else pos for pos in original_positions]
    def fold_random(self, 
                    qc: QuantumCircuit,
                    scale_factor: float) -> QuantumCircuit:
        '''Generates a random folding of the circuit qc by an scaling scale_factor.
          The new circuit has approximate a lenght given by scale_factor*len(qc).
           '''
        new_qc = qc.copy()
        positions=list(range(len(qc)))
        if scale_factor % 2 != 0:
            for _ in range(np.int32((scale_factor-1)/2)):
                for j in range(len(qc)):
                    self.folding(new_qc,
                                 positions[j])
                    positions=self.adapt_positions(positions,
                                                   positions[j])
            return new_qc
        else:
            while len(new_qc)/(scale_factor*len(qc)) < 1:
                random_idx = np.random.choice(positions)
                self.folding(new_qc,random_idx)
                positions=self.adapt_positions(positions,random_idx)
            return new_qc
    
    def ExpectationValues(self,
                          Circuit: QuantumCircuit,
                          Scale_Factors:list,
                          Operator,
                          Simulator):
        '''Generates the expecation values using a circuit, a list of scale factors, an operator and a simulator'''
        Expectation_Values = np.array([Simulator.run(X, Operator).result().values[0] for 
                                       X in [self.fold_random(Circuit, Y)
                                            for Y in Scale_Factors
                                            ]])
        return Expectation_Values
    def ZeroNEPolynomial(self,
                          Circuit: QuantumCircuit,
                          Scale_Factors:list,
                          Operator,
                          Simulator,
                          degree
                          ):

        '''Polynomial Interpolation'''
        y=self.ExpectationValues(Circuit,
                          Scale_Factors,
                          Operator,
                          Simulator)
        x=Scale_Factors
        return np.polyfit(x, y, degree)[1]
    def exponential_func(self, x, a, b, c):
        return a * np.exp(b * x) + c
    def ZeroNEExponential(self, Circuit, Scale_Factors, Operator, Simulator):
        '''Exponential Interpolation'''
        y = self.ExpectationValues(Circuit, Scale_Factors, Operator, Simulator)
        x = Scale_Factors
        popt, pcov = curve_fit(self.exponential_func, x, y,maxfev=1000)
        return self.exponential_func(0, *popt)


        
