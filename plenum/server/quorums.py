from plenum.common.util import getMaxFailures


class Quorum:

    def __init__(self, value: int):
        self.value = value

    def is_reached(self, items: int) -> bool:
        return items >= self.value


class Quorums:

    def __init__(self, n):
        f = getMaxFailures(n)
        self.f = f
        self.propagate = Quorum(f + 1)
        self.prepare = Quorum(n - f - 1)
        self.commit = Quorum(n - f)
        self.reply = Quorum(f + 1)
        self.view_change = Quorum(n - f)
        self.election = Quorum(n - f)
        self.view_change_done = Quorum(n - f)
        self.catchup_start = Quorum(f + 1)
        self.catchup_complete = Quorum(2 * f + 1)
        self.checkpoint = Quorum(2 * f)
