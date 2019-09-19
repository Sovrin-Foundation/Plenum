from plenum.common.messages.internal_messages import NeedViewChange
from plenum.common.util import getMaxFailures
from plenum.server.consensus.primary_selector import RoundRobinPrimariesSelector
from plenum.test.helper import checkViewNoForNodes, sdk_send_random_and_check
from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected
from plenum.test.test_node import ensureElectionsDone


REQ_COUNT = 10


def trigger_view_change(txnPoolNodeSet, proposed_view_no):
    for n in txnPoolNodeSet:
        for r in n.replicas.values():
            r.internal_bus.send(NeedViewChange(proposed_view_no))
            if r.isMaster:
                assert r._consensus_data.waiting_for_new_view


def get_next_primary_name(txnPoolNodeSet, expected_view_no):
    selector = RoundRobinPrimariesSelector()
    inst_count = len(txnPoolNodeSet[0].replicas)
    next_p_name = selector.select_primaries(expected_view_no, inst_count, txnPoolNodeSet[0].poolManager.node_names_ordered_by_rank())[0]
    return next_p_name


def test_view_change_triggered(looper, txnPoolNodeSet):
    current_view_no = checkViewNoForNodes(txnPoolNodeSet)
    trigger_view_change(txnPoolNodeSet, current_view_no + 1)
    ensureElectionsDone(looper, txnPoolNodeSet)


def test_view_change_triggered_after_ordering(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_client):
    sdk_send_random_and_check(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_client, REQ_COUNT)
    current_view_no = checkViewNoForNodes(txnPoolNodeSet)
    trigger_view_change(txnPoolNodeSet, current_view_no + 1)
    ensureElectionsDone(looper, txnPoolNodeSet)


def test_stopping_next_primary(looper, txnPoolNodeSet):
    old_view_no = checkViewNoForNodes(txnPoolNodeSet)
    next_primary = get_next_primary_name(txnPoolNodeSet, old_view_no + 1)
    disconnect_node_and_ensure_disconnected(looper, txnPoolNodeSet, next_primary)
    trigger_view_change(txnPoolNodeSet, old_view_no + 1)
    ensureElectionsDone(looper, txnPoolNodeSet)
    current_view_no = checkViewNoForNodes(txnPoolNodeSet)
    assert current_view_no == old_view_no + 2
