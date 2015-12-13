from godata import make_neighbors


def test_make_neighbors():
    """Test neighbor making by counting occurrences of neighbors

    Corners have two neighbors; Edges points have 3, and Centre points have 4.
    """
    def result_row(i, size):
        return [i] + [i+1]*(size-2) + [i]
    try:
        next(make_neighbors(0))
    except StopIteration:
        pass
    next(make_neighbors(1))

    for size in range(2, 23):
        neigh_counts = [0]*(size**2)
        first_row = result_row(2, size)
        last_row = result_row(2, size)
        middle_row = result_row(3, size)
        desired_result = first_row + (middle_row)*(size-2) + last_row
        for c, neighs in make_neighbors(size=size):
            for pt in list(neighs):
                neigh_counts[pt] += 1

        assert desired_result == neigh_counts

