import pytest

from common.exceptions import PlenumValueError
from plenum.common.messages.node_messages import ViewChangeDone
from plenum.server.view_change.view_changer import ViewChanger, FutureViewChangeDone
from plenum.test.testing_utils import FakeSomething
from plenum.server.quorums import Quorums


@pytest.fixture(scope='module')
def view_changer():
    config = FakeSomething(
        ViewChangeWindowSize=1,
        ForceViewChangeFreq=0
    )
    node = FakeSomething(
        name="fake node",
        ledger_ids=[0],
        config=config,
        quorums=Quorums(7)
    )
    view_changer = ViewChanger(node)
    return view_changer


def test_on_future_view_vchd_msg(view_changer):
    view_no = 0

    assert view_no == view_changer.view_no
    with pytest.raises(PlenumValueError) as excinfo:
        view_changer.process_future_view_vchd_msg(
            FutureViewChangeDone(ViewChangeDone(view_no, "Node1", []), False), "Node1")
    assert ("expected: > {}"
            .format(view_changer.view_no)) in str(excinfo.value)

    view_changer.view_no = 1
    with pytest.raises(PlenumValueError) as excinfo:
        view_changer.process_future_view_vchd_msg(
            FutureViewChangeDone(ViewChangeDone(view_no, "Node1", []), True), "Node1")
    assert ("expected: = 0 or > {}"
            .format(view_changer.view_no)) in str(excinfo.value)
