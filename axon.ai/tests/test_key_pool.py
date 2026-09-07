import time
from app.services.key_pool import KeyPoolManager

def test_key_pool_basic():
    pool = KeyPoolManager()
    assert pool.total_keys == 50, f"Expected 50 keys, got {pool.total_keys}"
    
    # Test round robin iteration
    key1, client1 = pool.get_next_key_and_client()
    key2, client2 = pool.get_next_key_and_client()
    assert key1 != key2, "Round robin should advance to next key"
    
    # Test simulated 429 cooldown
    status_before = pool.get_pool_status()
    assert status_before["cooling_down_keys"] == 0
    
    pool.report_rate_limit(key1, cooldown_seconds=300.0)
    status_after = pool.get_pool_status()
    assert status_after["cooling_down_keys"] == 1
    assert status_after["active_healthy_keys"] == 49
    
    # Key1 should now be skipped in normal rotation
    for _ in range(49):
        k, _ = pool.get_next_key_and_client()
        assert k != key1, f"Key {k} was returned despite being in cooldown"

    print("Key Pool unit tests passed successfully!")

if __name__ == "__main__":
    test_key_pool_basic()
