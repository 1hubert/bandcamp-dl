import time

import numpy

songs_in_album = numpy.zeros(10)


def add_zeros(num):
        """Prettify the file names."""
        max_num = len(songs_in_album)

        if max_num > 99:
            return str(num).zfill(3) + " "

        elif max_num > 9:
            return str(num).zfill(2) + " "

        elif max_num < 10:
            return str(num) + " "


def add_leading_zeros(num):
    """Prettify the file names."""
    max_num = len(songs_in_album)
    max_digits = len(str(max_num))
    return str(num).zfill(max_digits) + " "


def add_leading_zeros_oneliner(num):
    """Prettify the file names."""
    return str(num).zfill(len(str(len(songs_in_album)))) + " "

start = time.perf_counter()
for i in range(1, len(songs_in_album+1)):
    add_leading_zeros(i)
print(f"Original function completed in {time.perf_counter() - start} seconds")

start = time.perf_counter()
for i in range(1, len(songs_in_album+1)):
    add_leading_zeros(i)
print(f"Improved function completed in {time.perf_counter() - start} seconds")

start = time.perf_counter()
for i in range(1, len(songs_in_album+1)):
    add_leading_zeros(i)
print(f"Improved function (one-liner) completed in {time.perf_counter() - start} seconds")
