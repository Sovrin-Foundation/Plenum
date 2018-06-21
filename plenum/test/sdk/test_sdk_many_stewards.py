from plenum.test.helper import sdk_send_random_requests, sdk_get_and_check_replies


def test_sdk_many_stewards_send_many(looper, sdk_pool_handle, sdk_wallet_stewards):
    for sdk_wallet_steward in sdk_wallet_stewards:
        resp_task = sdk_send_random_requests(looper, sdk_pool_handle, sdk_wallet_steward, 30)
        repl = sdk_get_and_check_replies(looper, resp_task)
        for _, resp in repl:
            assert resp['result']