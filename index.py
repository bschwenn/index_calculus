"""
Usage: python index.py beta p alpha
where beta is some number such that beta \equiv alpha^x (mod p), where alpha is a primitive root mod p
"""
import logging
import sys
import math
import random
import numpy as np
from number_theory import gcd, egcd, prime_mod_inv, sieve_era

def precompute_prime_base(B):
    """
    :param B: bound for our index calculus
    :return: list of primes below B

    Basically just the sieve of Erastothenes
    """
    return sieve_era(B)


def prime_factorization(n, primes):
    ret = dict()
    for p in primes:
        ret[p] = 0
        while n % p == 0:
            n //= p
            ret[p] += 1
    return [ret[i] for i in ret] if n == 1 else None


def solve_relations(mat, p):
    n = len(mat)
    for r_index, row in enumerate(mat):
        for c_index in range(0, r_index):
            if mat[r_index][c_index] != 0:
                #for r_iter_index in range(r_index+1,
                r_idx_to_use, x, y = find_row_to_elim_nonzero(mat, r_index, c_index, n)
                if x == None:
                    return # Failure
                mat[r_index] = (x * row + y * mat[r_idx_to_use]) % (p-1)

    return mat


def find_row_to_elim_nonzero(mat, r_idx, c_idx, n):
    pivot_val = mat[r_idx][c_idx]

    for r_iter in range(r_idx+1, n):
        (d,x,y) = egcd(pivot_val, mat[r_iter][c_idx])
        if d == 1:
            return r_iter,x,y

    return None, None, None


def subtract_rows(row_1, row_2, multiple,p):
    row_1 -= (multiple * row_2) % p
    row_1 %= p
    return row_1


def rref(matrix, p):
    i, j = 0, 0
    while i < matrix.shape[0] and j < matrix.shape[1]:
        if matrix[i][j] == 0 or gcd(matrix[i][j], p) != 1:
            k = i
            while k < matrix.shape[0]:
                if matrix[k][j] != 0 or gcd(matrix[i][j], p)==1:
                    break
                k += 1
            if k == matrix.shape[0]:
                j += 1
                continue
            matrix[[i, k]] = matrix[[k, i]]
        div = prime_mod_inv(matrix[i][j], p)
        # print("mat[i][j]=", matrix[i][j], "and div = ", div, "and p=", p)
        for k in range(0, matrix.shape[1]):
            if k != j:
                matrix[i][k] *= div
                # matrix[i][k] /= matrix[i][j]
        matrix[i][j] = 1
        for k in range(0, matrix.shape[0]):
            if k != i:
                matrix[k] = subtract_rows(matrix[k], matrix[i], matrix[k][j], p)
        i += 1
        j += 1
    return matrix % p


def zero_row_absent(matrix):
    for i in matrix[-1]:
        if i != 0:
            return True
    return False


def linearly_independent(prime_factors, factor_products, p):
    factor_products.append(prime_factors)
    matrix = np.array(factor_products, dtype=np.float64)
    factor_products.pop()
    matrix = rref(matrix, p-1)
    return zero_row_absent(matrix)

def index_calculus(beta, p, alpha):
    """
    :param beta:
    :param p:
    :param alpha:
    :return:
    """
    factor_base = precompute_prime_base(find_bound(p))
    unused = set(factor_base)
    factor_products = []
    checked = set()
    # while True:
    while len(unused) > 0 or len(factor_products) < len(factor_base):  # arbitrary buffer number for mod inverse issues
        # print(factor_products)
        if len(checked) == p - 1:
            print("The bound B wasn't big enough!")
            exit(0)
        exp = random.randint(1, p - 1)
        if exp in checked:
            continue
        checked.add(exp)
        power = pow(alpha, exp, p)
        if power == 1:
            continue
        prime_factors = prime_factorization(power, factor_base)
        if prime_factors:
            prime_factors.append(exp)
            if linearly_independent(prime_factors, factor_products, p):
                for index, i in enumerate(prime_factors[:-1]):
                    if factor_base[index] in unused:
                        unused.remove(factor_base[index])
                factor_products.append(prime_factors)
    print(factor_products)
    prime_discrete_logs = solve_relations(np.array(factor_products, dtype=np.float64), p)
    return prime_discrete_logs


def find_bound(n):
    return int(math.exp((2**(-0.5)*(math.log(2*n)*math.log(math.log(2*n)))**0.5)))


def main():
    if len(sys.argv) < 4:
        print("Usage: python index.py beta p alpha, where beta = alpha^x (mod p)")
        return 1

    logging.basicConfig(filename='index.log', filemode='w', level=logging.DEBUG, format='%(message)s')

    beta = int(sys.argv[1])
    p = int(sys.argv[2])
    alpha = int(sys.argv[3])
    print(alpha)
    print("The value of x is",  index_calculus(beta, p, alpha))
    return 0


if __name__ == "__main__":
   main()
   #mat = np.array([[2, 1, 0, 1], [1, 1, 0, 3], [0, 0, 0, 0]], dtype=np.float64)
   #print(zero_row_absent(mat))
   # mat = np.array([[2, 1, 0, 1], [1, 1, 0, 3], [0, 0, 0, 0]], dtype=np.float64)
   # print(zero_row_absent(mat))
   # print(mod_inv(3, 101))
   # print(mod_inv(1, 100))
