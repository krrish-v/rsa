# -*- coding: utf-8 -*-
#
#  Copyright 2011 Sybren A. Stüvel <sybren@stuvel.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Numerical functions related to primes.

Implementation based on the book Algorithm Design by Michael T. Goodrich and
Roberto Tamassia, 2002.
"""

import rsa.randnum

__all__ = ['getprime', 'are_relatively_prime']


def gcd(p, q):
    """Returns the greatest common divisor of p and q

    >>> gcd(48, 180)
    12
    """

    while q != 0:
        (p, q) = (q, p % q)
    return p


def jacobi(a, b):
    """Calculates the value of the Jacobi symbol (a/b) where both a and b are
    positive integers, and b is odd

    :returns: -1, 0 or 1
    """

    assert a > 0
    assert b > 0

    result = 1
    while a > 1:
        if a & 1:
            if ((a - 1) * (b - 1) >> 2) & 1:
                result = -result
            a, b = b % a, a
        else:
            if (((b * b) - 1) >> 3) & 1:
                result = -result
            a >>= 1
    if a == 0:
        return 0
    return result


def jacobi_witness(x, n):
    """Returns False if n is an Euler pseudo-prime with base x, and True otherwise."""

    j = jacobi(x, n) % n

    f = pow(x, n >> 1, n)

    if j == f:
        return False
    return True


def randomized_primality_testing(n, k):
    """Calculates whether n is composite (which is always correct) or
    prime (which is incorrect with error probability 2**-k)

    Returns False if the number is composite, and True if it's
    probably prime.
    """

    # 50% of Jacobi-witnesses can report compositness of non-prime numbers

    # The implemented algorithm using the Jacobi witness function has error
    # probability q <= 0.5, according to Goodrich et. al
    #
    # q = 0.5
    # t = int(math.ceil(k / log(1 / q, 2)))
    # So t = k / log(2, 2) = k / 1 = k
    # this means we can use range(k) rather than range(t)

    for _ in range(k):
        x = rsa.randnum.randint(n - 1)
        if jacobi_witness(x, n):
            return False

    return True


def miller_rabin_primality_testing(n, k):
    """Calculates whether n is composite (which is always correct) or prime
    (which theoretically is incorrect with error probability 4**-k), by
    applying Miller-Rabin primality testing.

    For reference and implementation example, see:
    https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test

    :param n: Integer to be tested for primality.
    :type n: int
    :param k: Number of rounds (witnesses) of Miller-Rabin testing.
    :type k: int
    :return: False if the number is composite, True if it's probably prime.
    :rtype: bool
    """

    # Decompose (n - 1) to write it as (2 ** r) * d
    # While d is even, divide it by 2 and increase the exponent.
    d = n - 1
    r = 0
    while not (d & 1):
        r += 1
        d >>= 1

    # Test k witnesses.
    for _ in range(k):
        # Generate random integer a, where 2 <= a <= (n - 2)
        a = 0
        while a < 2:
            a = rsa.randnum.randint(n - 2)

        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == 1:
                # n is composite.
                return False
            if x == n - 1:
                # Exit inner loop and continue with next witness.
                break
        else:
            # If loop doesn't break, n is composite.
            return False

    return True


def is_prime(number):
    """Returns True if the number is prime, and False otherwise.

    >>> is_prime(2)
    True
    >>> is_prime(42)
    False
    >>> is_prime(41)
    True
    >>> [x for x in range(901, 1000) if is_prime(x)]
    [907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
    """

    # Check for small numbers.
    if number < 10:
        return number in [2, 3, 5, 7]

    # Check for even numbers.
    if not (number & 1):
        return False

    # According to NIST FIPS 186-4, Appendix C, Table C.3, minimum number of
    # rounds of M-R testing, using an error probability of 2 ** (-100), for
    # different p, q bitsizes are:
    #   * p, q bitsize: 512; rounds: 7
    #   * p, q bitsize: 1024; rounds: 4
    #   * p, q bitsize: 1536; rounds: 3
    # See: http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf
    return miller_rabin_primality_testing(number, 7)


def getprime(nbits):
    """Returns a prime number that can be stored in 'nbits' bits.

    >>> p = getprime(128)
    >>> is_prime(p-1)
    False
    >>> is_prime(p)
    True
    >>> is_prime(p+1)
    False

    >>> from rsa import common
    >>> common.bit_size(p) == 128
    True
    """

    while True:
        integer = rsa.randnum.read_random_odd_int(nbits)

        # Test for primeness
        if is_prime(integer):
            return integer

            # Retry if not prime


def are_relatively_prime(a, b):
    """Returns True if a and b are relatively prime, and False if they
    are not.

    >>> are_relatively_prime(2, 3)
    True
    >>> are_relatively_prime(2, 4)
    False
    """

    d = gcd(a, b)
    return d == 1


if __name__ == '__main__':
    print('Running doctests 1000x or until failure')
    import doctest

    for count in range(1000):
        (failures, tests) = doctest.testmod()
        if failures:
            break

        if count and count % 100 == 0:
            print('%i times' % count)

    print('Doctests done')
