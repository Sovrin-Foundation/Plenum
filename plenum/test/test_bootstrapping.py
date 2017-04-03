from stp_core.network.exceptions import RemoteNotFound
from plenum.common.log import getlogger
from plenum.test.greek import genNodeNames

from stp_core.loop.looper import Looper
from plenum.test.helper import msgAll
from plenum.test.test_stack import RemoteState, NOT_CONNECTED
from plenum.test.test_node import TestNodeSet, checkNodesConnected, genNodeReg

logger = getlogger()


whitelist = ['public key from disk', 'verification key from disk',
             'doesnt have enough info to connect']


# noinspection PyIncorrectDocstring
def testKeyShareParty(tdir_for_func):
    """
    connections to all nodes should be successfully established when key
    sharing is enabled.
    """
    nodeReg = genNodeReg(5)

    logger.debug("-----sharing keys-----")
    with TestNodeSet(nodeReg=nodeReg,
                     tmpdir=tdir_for_func) as nodeSet:
        with Looper(nodeSet) as looper:
            looper.run(checkNodesConnected(nodeSet))

    logger.debug("-----key sharing done, connect after key sharing-----")
    with TestNodeSet(nodeReg=nodeReg,
                     tmpdir=tdir_for_func) as nodeSet:
        with Looper(nodeSet) as loop:
            loop.run(checkNodesConnected(nodeSet),
                     msgAll(nodeSet))


# noinspection PyIncorrectDocstring
def testConnectWithoutKeySharingFails(tdir_for_func):
    """
    attempts at connecting to nodes when key sharing is disabled must fail
    """
    nodeNames = genNodeNames(5)
    with TestNodeSet(names=nodeNames, tmpdir=tdir_for_func,
                     keyshare=False) as nodes:
        with Looper(nodes) as looper:
            try:
                looper.run(
                        checkNodesConnected(nodes, NOT_CONNECTED))
            except RemoteNotFound:
                pass
            except KeyError as ex:
                assert [n for n in nodeNames
                        if n == ex.args[0]]
            except Exception:
                raise
