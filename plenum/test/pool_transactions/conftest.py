import pytest

from stp_core.loop.looper import Looper
from plenum.common.util import randomString
from plenum.test.test_node import checkNodesConnected
from plenum.test.node_catchup.helper import \
    ensureClientConnectedToNodesAndPoolLedgerSame
from plenum.test.pool_transactions.helper import addNewStewardAndNode, \
    buildPoolClientAndWallet


@pytest.yield_fixture(scope="module")
def looper(txnPoolNodesLooper):
    yield txnPoolNodesLooper


@pytest.fixture(scope="module")
def stewardAndWallet1(looper, txnPoolNodeSet, poolTxnStewardData,
                      tdirWithPoolTxns):
    return buildPoolClientAndWallet(poolTxnStewardData, tdirWithPoolTxns)


@pytest.fixture(scope="module")
def steward1(looper, txnPoolNodeSet, stewardAndWallet1):
    steward, wallet = stewardAndWallet1
    looper.add(steward)
    ensureClientConnectedToNodesAndPoolLedgerSame(looper, steward,
                                                  *txnPoolNodeSet)
    return steward


@pytest.fixture(scope="module")
def stewardWallet(stewardAndWallet1):
    return stewardAndWallet1[1]


@pytest.fixture("module")
def nodeThetaAdded(looper, txnPoolNodeSet, tdirWithPoolTxns, tconf, steward1,
                   stewardWallet, allPluginsPath, testNodeClass,
                   testClientClass):
    newStewardName = "testClientSteward" + randomString(3)
    newNodeName = "Theta"
    newSteward, newStewardWallet, newNode = addNewStewardAndNode(looper,
                                                                 steward1,
                                                                 stewardWallet,
                                                                 newStewardName,
                                                                 newNodeName,
                                                                 tdirWithPoolTxns,
                                                                 tconf,
                                                                 allPluginsPath,
                                                                 nodeClass=testNodeClass,
                                                                 clientClass=testClientClass)
    txnPoolNodeSet.append(newNode)
    looper.run(checkNodesConnected(txnPoolNodeSet))
    ensureClientConnectedToNodesAndPoolLedgerSame(looper, steward1,
                                                  *txnPoolNodeSet)
    ensureClientConnectedToNodesAndPoolLedgerSame(looper, newSteward,
                                                  *txnPoolNodeSet)
    return newSteward, newStewardWallet, newNode


@pytest.fixture(scope="module")
def clientAndWallet1(txnPoolNodeSet, poolTxnClientData, tdirWithPoolTxns):
    return buildPoolClientAndWallet(poolTxnClientData, tdirWithPoolTxns)


@pytest.fixture(scope="module")
def client1(clientAndWallet1):
    return clientAndWallet1[0]


@pytest.fixture(scope="module")
def wallet1(clientAndWallet1):
    return clientAndWallet1[1]


@pytest.fixture(scope="module")
def client1Connected(looper, client1):
    looper.add(client1)
    looper.run(client1.ensureConnectedToNodes())
    return client1
