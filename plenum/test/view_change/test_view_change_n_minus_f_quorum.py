from plenum.test.helper import sendReqsToNodesAndVerifySuffReplies
from plenum.test.node_catchup.helper import ensure_all_nodes_have_same_data
from plenum.test.spy_helpers import get_count
from plenum.test.test_node import ensureElectionsDone
from plenum.test.view_change.helper import ensure_view_change
from plenum.test.helper import stopNodes


def test_view_change_n_minus_f_quorum(nodeSet, up, looper):
    """
    Check that quorum n - f is used for view change 
    """

    # Quorum for view change is expected to be f + 1
    # So, switching one node off
    assert len(nodeSet) == 4

    # Stopping one node
    stopped = [nodeSet[-1]]
    active = list(nodeSet)[:-1]
    stopNodes(stopped, looper)
    looper.removeProdable(*stopped)

    # Check that view changes
    ensure_view_change(looper, active)
    ensureElectionsDone(looper=looper, nodes=active, numInstances=2)
    ensure_all_nodes_have_same_data(looper, nodes=active)
