import base58
import pytest
import re

import time

from plenum.common.constants import TXN_TYPE, GET_TXN, DATA, NODE, \
    CURRENT_PROTOCOL_VERSION, DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.common.types import f
from plenum.common.util import getTimeBasedId
from plenum.server.validator_info_tool import ValidatorNodeInfoTool
from plenum.test import waits
from plenum.test.helper import check_sufficient_replies_received, \
    sdk_send_random_and_check
from plenum.test.node_catchup.helper import ensureClientConnectedToNodesAndPoolLedgerSame
from plenum.test.pool_transactions.helper import disconnect_node_and_ensure_disconnected
from plenum.test.test_client import genTestClient
from stp_core.common.constants import ZMQ_NETWORK_PROTOCOL
from stp_core.loop.eventually import eventually
from plenum.server.validator_info_tool import NUMBER_TXNS_FOR_DISPLAY

TEST_NODE_NAME = 'Alpha'
INFO_FILENAME = '{}_info.json'.format(TEST_NODE_NAME.lower())
PERIOD_SEC = 1
nodeCount = 5
MAX_TIME_FOR_INFO_BUILDING = 2


def test_validator_info_file_schema_is_valid(info):
    assert isinstance(info, dict)
    assert 'alias' in info

    assert 'bindings' in info
    assert 'client' in info['bindings']
    assert 'ip' not in info['bindings']['client']
    assert 'port' in info['bindings']['client']
    assert 'protocol' in info['bindings']['client']
    assert 'node' in info['bindings']
    assert 'ip' not in info['bindings']['node']
    assert 'port' in info['bindings']['node']
    assert 'protocol' in info['bindings']['node']

    assert 'did' in info
    assert 'response-version' in info
    assert 'timestamp' in info
    assert 'verkey' in info

    assert 'metrics' in info
    assert 'average-per-second' in info['metrics']
    assert 'read-transactions' in info['metrics']['average-per-second']
    assert 'write-transactions' in info['metrics']['average-per-second']
    assert 'transaction-count' in info['metrics']
    assert 'ledger' in info['metrics']['transaction-count']
    assert 'pool' in info['metrics']['transaction-count']
    assert 'uptime' in info['metrics']

    assert 'pool' in info
    assert 'reachable' in info['pool']
    assert 'count' in info['pool']['reachable']
    assert 'list' in info['pool']['reachable']
    assert 'unreachable' in info['pool']
    assert 'count' in info['pool']['unreachable']
    assert 'list' in info['pool']['unreachable']
    assert 'total-count' in info['pool']


def test_validator_info_file_alias_field_valid(info):
    assert info['alias'] == 'Alpha'


def test_validator_info_file_bindings_field_valid(info, node):
    # don't forget enable this check if ip comes back
    # assert info['bindings']['client']['ip'] == node.clientstack.ha.host
    assert 'ip' not in info['bindings']['client']
    assert info['bindings']['client']['port'] == node.clientstack.ha.port
    assert info['bindings']['client']['protocol'] == ZMQ_NETWORK_PROTOCOL

    # don't forget enable this check if ip comes back
    # assert info['bindings']['node']['ip'] == node.nodestack.ha.host
    assert 'ip' not in info['bindings']['node']
    assert info['bindings']['node']['port'] == node.nodestack.ha.port
    assert info['bindings']['node']['protocol'] == ZMQ_NETWORK_PROTOCOL


def test_validator_info_file_did_field_valid(info):
    assert info['did'] == 'JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ'


def test_validator_info_file_response_version_field_valid(info):
    assert info['response-version'] == ValidatorNodeInfoTool.JSON_SCHEMA_VERSION


def test_validator_info_file_timestamp_field_valid(node,
                                                   info,
                                                   looper):
    looper.runFor(2)
    assert re.match('\d{10}', str(info['timestamp']))
    latest_info = node._info_tool.info
    assert latest_info['timestamp'] > info['timestamp']


def test_validator_info_file_verkey_field_valid(node, info):
    assert info['verkey'] == base58.b58encode(node.nodestack.verKey)


def test_validator_info_file_metrics_avg_write_field_valid(info,
                                                           write_txn_and_get_latest_info):
    assert info['metrics']['average-per-second']['write-transactions'] == 0
    latest_info = write_txn_and_get_latest_info()
    assert latest_info['metrics']['average-per-second']['write-transactions'] > 0


def test_validator_info_file_metrics_avg_read_field_valid(info,
                                                          read_txn_and_get_latest_info
                                                          ):
    assert info['metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_TXN)
    assert latest_info['metrics']['average-per-second']['read-transactions'] > 0


def test_validator_info_file_metrics_count_ledger_field_valid(poolTxnData, info):
    txns_num = sum(1 for item in poolTxnData["txns"] if item.get(TXN_TYPE) != NODE)
    assert info['metrics']['transaction-count']['ledger'] == txns_num


def test_validator_info_file_metrics_count_pool_field_valid(info):
    assert info['metrics']['transaction-count']['pool'] == nodeCount


def test_validator_info_file_metrics_uptime_field_valid(node,
                                                        info):
    assert info['metrics']['uptime'] > 0
    latest_info = node._info_tool.info
    assert latest_info['metrics']['uptime'] > info['metrics']['uptime']


def test_validator_info_file_pool_fields_valid(looper, info, txnPoolNodesLooper, txnPoolNodeSet, node):
    assert info['pool']['reachable']['count'] == nodeCount
    assert info['pool']['reachable']['list'] == sorted(list(node.name for node in txnPoolNodeSet))
    assert info['pool']['unreachable']['count'] == 0
    assert info['pool']['unreachable']['list'] == []
    assert info['pool']['total-count'] == nodeCount

    others, disconnected = txnPoolNodeSet[:-1], txnPoolNodeSet[-1]
    disconnect_node_and_ensure_disconnected(txnPoolNodesLooper, txnPoolNodeSet, disconnected)
    latest_info = node._info_tool.info

    assert latest_info['pool']['reachable']['count'] == nodeCount - 1
    assert latest_info['pool']['reachable']['list'] == sorted(list(node.name for node in others))
    assert latest_info['pool']['unreachable']['count'] == 1
    assert latest_info['pool']['unreachable']['list'] == [txnPoolNodeSet[-1].name]
    assert latest_info['pool']['total-count'] == nodeCount


def test_validator_info_file_handle_fails(info,
                                          node):
    node_instance  = node._info_tool._node
    node._info_tool._node = None
    latest_info = node._info_tool.info

    assert latest_info['alias'] is None
    # assert latest_info['bindings']['client']['ip'] is None
    assert 'ip' not in info['bindings']['client']
    assert latest_info['bindings']['client']['port'] is None
    # assert latest_info['bindings']['node']['ip'] is None
    assert 'ip' not in info['bindings']['node']
    assert latest_info['bindings']['node']['port'] is None
    assert latest_info['did'] is None
    assert latest_info['timestamp'] is not None
    assert latest_info['verkey'] is None
    assert latest_info['metrics']['average-per-second']['read-transactions'] is None
    assert latest_info['metrics']['average-per-second']['write-transactions'] is None
    assert latest_info['metrics']['transaction-count']['ledger'] is None
    assert latest_info['metrics']['transaction-count']['pool'] is None
    assert latest_info['metrics']['uptime'] is None
    assert latest_info['pool']['reachable']['count'] is None
    assert latest_info['pool']['reachable']['list'] is None
    assert latest_info['pool']['unreachable']['count'] is None
    assert latest_info['pool']['unreachable']['list'] is None
    assert latest_info['pool']['total-count'] is None
    node._info_tool._node = node_instance


def test_hardware_info_section(info):
    assert info['Hardware']
    assert info['Hardware']['HDD_all']
    assert info['Hardware']['RAM_all_free']
    assert info['Hardware']['RAM_used_by_node']
    assert info['Hardware']['HDD_used_by_node']


def test_software_info_section(info):
    assert info['Software']
    assert info['Software']['OS_version']
    assert info['Software']['Installed_packages']
    assert info['Software']['Indy_packages']


def test_node_info_section(info):
    assert info['Node info']
    assert info['Node info']['Catchup_status']
    assert info['Node info']['Catchup_status']['Last_txn_3PC_keys']
    assert len(info['Node info']['Catchup_status']['Last_txn_3PC_keys']) == 3
    assert info['Node info']['Catchup_status']['Ledger_statuses']
    assert len(info['Node info']['Catchup_status']['Ledger_statuses']) == 3
    assert info['Node info']['Catchup_status']['Number_txns_in_catchup']
    # TODO uncomment this, when this field would be implemented
    # assert info['Node info']['Catchup_status']['Received_LedgerStatus']
    assert info['Node info']['Catchup_status']['Waiting_consistency_proof_msgs']
    assert len(info['Node info']['Catchup_status']['Waiting_consistency_proof_msgs']) == 3
    assert info['Node info']['Count_of_replicas']
    # TODO uncomment this, when this field would be implemented
    # assert info['Node info']['Last N pool ledger txns']
    assert info['Node info']['Metrics']
    assert info['Node info']['Mode']
    assert info['Node info']['Name']
    assert info['Node info']['Replicas_status']
    assert info['Node info']['Root_hashes']
    assert info['Node info']['Root_hashes'][0]
    assert info['Node info']['Root_hashes'][1]
    assert info['Node info']['Root_hashes'][2]
    assert 'Uncommitted_root_hashes' in info['Node info']
    assert 'Uncommitted_txns' in info['Node info']
    assert info['Node info']['View_change_status']
    assert 'IC_queue'       in info['Node info']['View_change_status']
    assert 'VCDone_queue'   in info['Node info']['View_change_status']
    assert 'VC_in_progress' in info['Node info']['View_change_status']
    assert 'View_No'        in info['Node info']['View_change_status']


def test_pool_info_section(info):
    assert info['Pool info']
    assert 'Blacklisted_nodes' in info['Pool info']
    assert info['Pool info']['Quorums']
    assert info['Pool info']['Reachable_nodes']
    assert 'Read_only' in info['Pool info']
    assert 'Suspicious_nodes' in info['Pool info']
    assert info['Pool info']['Total_nodes']
    assert 'Unreachable_nodes' in info['Pool info']
    assert info['Pool info']['f_value']


def test_config_info_section(node):
    info = node._info_tool.additional_info
    assert 'Main_config' in info['Configuration']['Config']
    assert 'Network_config' in info['Configuration']['Config']
    assert 'User_config' in info['Configuration']['Config']
    assert info['Configuration']['Config']['Main_config']
    assert info['Configuration']['Config']['Network_config']
    assert info['Configuration']['Genesis_txns']
    assert 'indy.env' in info['Configuration']
    assert 'node_control.conf' in info['Configuration']
    assert 'indy-node.service' in info['Configuration']
    assert 'indy-node-control.service' in info['Configuration']
    assert 'iptables_config' in info['Configuration']


def test_extractions_section(node):
    info = node._info_tool.additional_info
    assert "journalctl_exceptions" in info["Extractions"]
    assert "indy-node_status" in info["Extractions"]
    assert "node-control status" in info["Extractions"]
    assert "upgrade_log" in info["Extractions"]
    assert "Last_N_pool_ledger_txns" in info["Extractions"]
    assert "Last_N_domain_ledger_txns" in info["Extractions"]
    assert "Last_N_config_ledger_txns" in info["Extractions"]
    assert "Pool_ledger_size" in info["Extractions"]
    assert "Domain_ledger_size" in info["Extractions"]
    assert "Config_ledger_size" in info["Extractions"]
    assert info["Extractions"]['Pool_ledger_size'] == node.poolLedger.size
    assert info["Extractions"]['Domain_ledger_size'] == node.domainLedger.size
    assert info["Extractions"]['Config_ledger_size'] == node.configLedger.size


def test_last_exactly_N_txn_from_ledger(node,
                                        looper,
                                        txnPoolNodeSet,
                                        sdk_pool_handle,
                                        sdk_wallet_steward):
    txnCount = 10
    sdk_send_random_and_check(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_steward, txnCount)
    assert node.domainLedger.size > NUMBER_TXNS_FOR_DISPLAY
    extractions = node._info_tool.additional_info['Extractions']
    assert len(extractions["Last_N_domain_ledger_txns"]) == NUMBER_TXNS_FOR_DISPLAY


def test_build_node_info_time(node):
    after = time.perf_counter()
    node._info_tool.info
    before = time.perf_counter()
    assert before - after < MAX_TIME_FOR_INFO_BUILDING


def test_protocol_info_section(info):
    assert 'Protocol' in info


@pytest.fixture(scope='module')
def info(node):
    return node._info_tool.info


@pytest.fixture(scope='module')
def node(txnPoolNodeSet):
    for n in txnPoolNodeSet:
        if n.name == TEST_NODE_NAME:
            return n
    assert False, 'Pool does not have "{}" node'.format(TEST_NODE_NAME)


@pytest.fixture
def read_txn_and_get_latest_info(txnPoolNodesLooper,
                                 client_and_wallet, node):
    client, wallet = client_and_wallet

    def read_wrapped(txn_type):
        op = {
            TXN_TYPE: txn_type,
            f.LEDGER_ID.nm: DOMAIN_LEDGER_ID,
            DATA: 1
        }
        req = Request(identifier=wallet.defaultId,
                      operation=op, reqId=getTimeBasedId(),
                      protocolVersion=CURRENT_PROTOCOL_VERSION)
        client.submitReqs(req)

        timeout = waits.expectedTransactionExecutionTime(
            len(client.inBox))

        txnPoolNodesLooper.run(
            eventually(check_sufficient_replies_received,
                       client, req.identifier, req.reqId,
                       retryWait=1, timeout=timeout))
        return node._info_tool.info

    return read_wrapped


@pytest.fixture
def write_txn_and_get_latest_info(txnPoolNodesLooper,
                                  sdk_pool_handle,
                                  sdk_wallet_client,
                                  node):
    def write_wrapped():
        sdk_send_random_and_check(txnPoolNodesLooper, range(nodeCount),
                                  sdk_pool_handle,
                                  sdk_wallet_client,
                                  1)
        return node._info_tool.info

    return write_wrapped


@pytest.fixture(scope="function")
def load_latest_info(node):
    def wrapped():
        return node._info_tool.info

    return wrapped


@pytest.fixture
def client_and_wallet(txnPoolNodesLooper, tdirWithClientPoolTxns, txnPoolNodeSet):
    client, wallet = genTestClient(tmpdir=tdirWithClientPoolTxns, nodes=txnPoolNodeSet,
                                   name='reader', usePoolLedger=True)
    txnPoolNodesLooper.add(client)
    ensureClientConnectedToNodesAndPoolLedgerSame(txnPoolNodesLooper, client,
                                                  *txnPoolNodeSet)
    return client, wallet
