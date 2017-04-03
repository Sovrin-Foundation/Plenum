from functools import partial

import pytest

from stp_core.loop.eventually import eventually
from plenum.test.cli.helper import checkReply, \
    checkSuccess, checkBalance, assertNoClient, loadPlugin, \
    createClientAndConnect


@pytest.fixture("module")
def loadBankReqPlugin(cli):
    loadPlugin(cli, 'bank_req_validation')
    loadPlugin(cli, 'bank_req_processor')


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-457')
def testReqForNonExistentClient(cli, loadBankReqPlugin, createAllNodes):
    cli.enterCmd("client Random balance")
    assertNoClient(cli)
    cli.enterCmd("client Random credit 400 to RandomNew")
    assertNoClient(cli)
    cli.enterCmd("client Random transactions")
    assertNoClient(cli)


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-457')
def testTransactions(cli, loadBankReqPlugin, createAllNodes, validNodeNames):
    nodeCount = len(validNodeNames)
    createClientAndConnect(cli, validNodeNames, "Alice")
    createClientAndConnect(cli, validNodeNames, "Bob")
    cli.enterCmd("client Alice credit 500 to Bob")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 1,
                              checkSuccess, retryWait=1, timeout=5))
    cli.enterCmd("client Alice balance")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 2,
                              checkSuccess, retryWait=1, timeout=5))
    cli.looper.run(eventually(checkReply, cli, len(validNodeNames),
                              partial(checkBalance, 500), retryWait=1,
                              timeout=5))
    cli.enterCmd("client Bob balance")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 3,
                              checkSuccess, retryWait=1, timeout=5))
    cli.looper.run(eventually(checkReply, cli, nodeCount,
                              partial(checkBalance, 1500), retryWait=1,
                              timeout=5))
    cli.enterCmd("client Bob credit 10 to Alice")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 4,
                              checkSuccess, retryWait=1, timeout=5))
    cli.enterCmd("client Bob balance")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 5,
                              checkSuccess, retryWait=1, timeout=5))
    cli.looper.run(eventually(checkReply, cli, nodeCount,
                              partial(checkBalance, 1490), retryWait=1,
                              timeout=5))
    cli.enterCmd("client Bob credit 100 to Alice")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 6,
                              checkSuccess, retryWait=1, timeout=5))
    cli.enterCmd("client Alice balance")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 7,
                              checkSuccess, retryWait=1, timeout=5))
    cli.looper.run(eventually(checkReply, cli, nodeCount,
                              partial(checkBalance, 610), retryWait=1,
                              timeout=10))
    cli.enterCmd("client Bob balance")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 8,
                              checkSuccess, retryWait=1, timeout=5))
    cli.looper.run(eventually(checkReply, cli, nodeCount,
                              partial(checkBalance, 1390), retryWait=1,
                              timeout=5))
    createClientAndConnect(cli, validNodeNames, "Carol")
    cli.enterCmd("client Carol credit 50 to Bob")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 9,
                              checkSuccess, retryWait=1, timeout=5))
    cli.enterCmd("client Bob balance")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 10,
                              checkSuccess, retryWait=1, timeout=5))
    cli.looper.run(eventually(checkReply, cli, nodeCount,
                              partial(checkBalance, 1440), retryWait=1,
                              timeout=10))
    cli.enterCmd("client Carol balance")
    cli.looper.run(eventually(checkReply, cli, nodeCount * 11,
                              checkSuccess, retryWait=1, timeout=5))
    cli.looper.run(eventually(checkReply, cli, nodeCount,
                              partial(checkBalance, 950), retryWait=1,
                              timeout=5))
