import time

from stp_core.loop.eventually import eventually
from plenum.common.exceptions import SuspiciousNode
from plenum.common.types import Prepare
from plenum.server.suspicion_codes import Suspicions
from plenum.test.helper import getNodeSuspicions
from plenum.test.spy_helpers import getAllArgs
from plenum.test.test_node import TestNode, getNonPrimaryReplicas, \
    getPrimaryReplica

nodeCount = 7


def testPrimarySendsAPrepareAndMarkedSuspicious(looper, nodeSet, preprepared1):
    def sendPrepareFromPrimary(instId):
        primary = getPrimaryReplica(nodeSet, instId)
        viewNo, ppSeqNo = next(iter(primary.sentPrePrepares.keys()))
        prepare = Prepare(instId,
                          viewNo,
                          ppSeqNo,
                          preprepared1.digest,
                          time.time())
        primary.doPrepare(prepare)

        def chk():
            for r in getNonPrimaryReplicas(nodeSet, instId):
                l = len([param for param in getAllArgs(r, r.processPrepare)
                         if param['sender'] == primary.name])
                assert l == 1

        looper.run(eventually(chk))

    sendPrepareFromPrimary(0)

    for node in nodeSet:
        if node in getNonPrimaryReplicas(nodeSet, 0):
            frm, reason, code = getAllArgs(node, TestNode.reportSuspiciousNode)
            assert frm == getPrimaryReplica(nodeSet, 0).node.name
            assert isinstance(reason, SuspiciousNode)
            assert len(getNodeSuspicions(node,
                                         Suspicions.PR_FRM_PRIMARY.code)) == 10
