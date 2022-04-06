"""
These classes are an implementation of the rings of integers modulo n.
While the code is not optimized for efficiency, it simplifies some operations such as exponentiation.
"""

from __future__ import annotations  # allows for typing a class in its definition
import functools
import itertools


class ModInt(object):

    def __init__(self, value: int, ring: ModRing):
        self.n = ring.n
        self.value = value % self.n
        self.ring = ring

    def __repr__(self):
        return f"{self.value} module {self.n}"

    def __eq__(self, other: ModInt) -> ModInt:
        assert type(other) is type(self)
        assert other.ring is self.ring, "numbers come from different rings"
        return other.value == self.value

    def __neg__(self) -> ModInt:
        return ModInt(self.n - self.value, self.ring)

    def __add__(self, addend: ModInt) -> ModInt:
        assert type(addend) is type(self)
        assert addend.ring is self.ring, "numbers come from different rings"
        return ModInt(self.value + addend.value, self.ring)

    def __sub__(self, subtrahend: ModInt) -> ModInt:
        assert type(subtrahend) is type(self)
        assert subtrahend.ring is self.ring, "numbers come from different rings"
        return ModInt(self.value - subtrahend.value, self.ring)

    def __mul__(self, factor: ModInt) -> ModInt:
        assert type(factor) is type(self)
        assert factor.ring is self.ring, "numbers come from different rings"
        return ModInt(self.value * factor.value, self.ring)

    def __pow__(self, exponent: int, short=True) -> ModInt:
        if self.value == 0:
            raise ValueError("0 cannot be eleveted to power")
        elif exponent == 0 or self.value == 1:
            return ModInt(1, self.ring)
        elif exponent < 0:
            assert self.is_coprime(), "exponent needs to be positive for non-coprimes"
            exponent %= self.ring.phi
            return ModInt(self.value ** exponent, self.ring)
        else:
            if short:
                nul_pow, k, m = self.decompose()
                if nul_pow == -1:
                    exponent %= self.ring.phi
                    return ModInt(self.value ** exponent, self.ring)
                elif exponent > nul_pow:
                    phi_m = ModRing(m).phi
                    exponent %= phi_m
                    new_value = k ** phi_m * self.value ** exponent
                    return ModInt(new_value, self.ring)
            else:
                return ModInt(self.value ** exponent, self.ring)

    def __floordiv__(self, divisor: ModInt) -> ModInt:
        assert type(divisor) is type(self)
        assert divisor.ring is self.ring, "numbers come from different rings"
        return self * divisor ** -1

    # Decompose module in two part: one where value is coprime, the other where it is nihilpotent
    # Return (-1, 1, n) if value is coprime to n else
    # (exponent after which the nihilpotent part nullifies, MCD(n, value), largest divisor of n coprime to value)
    def decompose(self):
        nul_pow = -1
        value = self.value
        # Wiki:the probability that two randomly chosen integers are coprime is 61%.
        # Therefore, get m (coprime to value) from dividing original n
        m = self.n
        k = 1
        for p, e in self.ring.prime_factors.items():
            quotient, remainder = divmod(value, p)
            if remainder == 0:
                p_e = p ** e
                m //= p_e
                k *= p_e
                value = quotient
                value_e = 1  # value of the exponent in value prime decomposition clipped to e
                for i in range(e - 1):
                    quotient, remainder = divmod(value, p)
                    if remainder == 0:
                        value_e += 1
                        value = quotient
                quotient, remainder = divmod(e, value_e)
                nul_pow_p = quotient - bool(remainder == 0)  # largest integer that multiplied by value_e is smaller than e
                nul_pow = max(nul_pow_p, nul_pow)
        return nul_pow, k, m

    # Only interested if value is coprime to z
    def is_coprime(self):
        return all(self.value % factor for factor in self.ring.prime_factors)


class ModRing(object):

    def __init__(self, n):
        self.n = n
        self.prime_factors = self.factorize()
        self.phi = self.compute_phi()

    def factorize(self):
        # keys are the prime factors, values their multiplicity
        prime_factors = {}
        # https://en.wikipedia.org/wiki/Trial_division
        z = self.n
        quotient, remainder = divmod(z, 2)
        if remainder == 0:
            prime_factors[2] = 0  # initialize key in dictionary
            while remainder == 0:
                z = quotient
                prime_factors[2] += 1
                quotient, remainder = divmod(z, 2)
        m = 3
        while m * m <= z:
            quotient, remainder = divmod(z, m)
            if remainder == 0:
                prime_factors[m] = 0  # initialize key in dictionary
                while remainder == 0:
                    z = quotient
                    prime_factors[m] += 1
                    quotient, remainder = divmod(z, m)
            m += 2
        if z != 1:  # z must be prime
            prime_factors[z] = 1
        return prime_factors

    def compute_phi(self):
        # https://en.wikipedia.org/wiki/Euler%27s_totient_function
        iter_primes = itertools.chain([self.n], self.prime_factors.keys())
        euler_product = functools.reduce(lambda x, y: x // y * (y - 1), iter_primes)
        return euler_product

    def __call__(self, value: int):
        return ModInt(value, self)


if __name__ == '__main__':
    ring12 = ModRing(n=12)
    a = ring12(value=6)
    b = ring12(value=7)
    print("Test prime factorization (should be 2^2 3^1). Result:", end = " ")
    for p, e in ring12.prime_factors.items():
        print(f"{p}^{e}", end=" ")
    print()
    print("Test phi (should be |1, 5, 7, 11| = 4). Result: ", ring12.phi)
    print("Test addition (should be 1). Result: ", a + b)
    print("Test subtraction (should be 11). Result: ", a - b)
    print("Test multiplication (should be 6). Result: ", a * b)
    try:
        a ** -1
    except Exception as e:
        print("Test inversion error. Result:", e.__class__, ":", e)
    print("Test inversion (should be 7). Result: ", b ** -1)
    print("Test division (should be 6). Result: ",  a // b)
    print("Test exponentiation:")
    exp = 100
    for n in range(2, 1000):
        ring = ModRing(n)
        for i in range(2, n):
            a = ring(i)
            res1 = a ** exp
            res2 = a.__pow__(exp, short=False)
            print("a = ", a, "Short_exp = ", res1, "Long_exp = ", res2)
            assert res1 == res2
