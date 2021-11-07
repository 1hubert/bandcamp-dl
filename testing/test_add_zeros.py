import numpy
songs_in_album = numpy.zeros(1)


def add_leading_zeros(num):
    """Prettify the file names."""
    max_num = len(songs_in_album)
    max_digits = len(str(max_num))
    return str(num).zfill(max_digits)


for num in range(1, len(songs_in_album)+1):
    print(add_leading_zeros(num), 'compl')

