from cw_py import valid_range, get_random_word


# valid_range()
def test_true():
    assert (valid_range(50, 250, 70) == True)


def test_false_1():
    assert (valid_range(50, 250, 40) == False)


def test_false_2():
    assert (valid_range(50, 250, 270) == False)


def test_equal_min():
    assert (valid_range(50, 250, 50) == True)


def test_equal_max():
    assert (valid_range(50, 250, 250) == True)


# get_random_word()
def test_random():
    # assert ((get_random_word([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) > 0) == True)
    graf = {}
    for counter in xrange(0, 1000):
        spisok = range(1, 101)
        graf{get_random_word(spisok): 1}
    print graf

test_random()
