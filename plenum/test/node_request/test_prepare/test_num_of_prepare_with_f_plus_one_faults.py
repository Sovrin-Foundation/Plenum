from functools import partial

import pytest
from plenum.common.util import adict, getNoInstances
from plenum.test import waits

from plenum.test.malicious_behaviors_node import makeNodeFaulty, \
    delaysPrePrepareProcessing, \
    changesRequest
from plenum.test.node_request.node_request_helper import checkPrePrepared

nodeCount = 7
# f + 1 faults, i.e, num of faults greater than system can tolerate
faultyNodes = 3
whitelist = ['InvalidSignature',
             'cannot process incoming PREPARE']
delayPrePrepareSec = 60


@pytest.fixture(scope="module")
def setup(startedNodes):
    A = startedNodes.Alpha
    B = startedNodes.Beta
    G = startedNodes.Gamma
    for node in A, B, G:
        makeNodeFaulty(node,
                       changesRequest,
                       partial(delaysPrePrepareProcessing, delay=delayPrePrepareSec))
        node.delaySelfNomination(10)
    return adict(faulties=(A, B, G))


@pytest.fixture(scope="module")
def afterElection(setup, up):
    for n in setup.faulties:
        for r in n.replicas:
            assert not r.isPrimary


@pytest.fixture(scope="module")
def preprepared1WithDelay(looper, nodeSet, propagated1, faultyNodes):
    timeouts = waits.expectedPrePrepareTime(len(nodeSet)) + delayPrePrepareSec
    checkPrePrepared(looper,
                     nodeSet,
                     propagated1,
                     range(getNoInstances(len(nodeSet))),
                     faultyNodes,
                     timeout=timeouts)


@pytest.mark.skip(reason='SOV-944')
def testNumOfPrepareWithFPlusOneFaults(afterElection, noRetryReq, preprepared1WithDelay):
    pass
