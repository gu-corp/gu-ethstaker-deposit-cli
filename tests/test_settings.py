import pytest

from ethstaker_deposit.settings import (
    ALL_CHAINS,
    JOC,
    JOCT,
    SANDBOX1,
    get_chain_setting,
)
from ethstaker_deposit.utils.validation import ALL_FORK_VERSIONS


JOC_FAMILY = [(JOC, 81), (JOCT, 10081), (SANDBOX1, 1337)]


def test_genesis_fork_versions_are_unique() -> None:
    """
    A deposit is signed against a zero genesis validators root, so the genesis
    fork version is the only value binding a deposit signature to one chain.
    Were two chains to share one, a deposit file generated for either would be
    a byte-identical, fully valid deposit on the other.
    """
    versions = [setting.GENESIS_FORK_VERSION for setting in ALL_CHAINS.values()]
    assert len(set(versions)) == len(versions)


def test_exit_fork_versions_are_unique() -> None:
    versions = [setting.EXIT_FORK_VERSION for setting in ALL_CHAINS.values()]
    assert len(set(versions)) == len(versions)


def test_all_fork_versions_lookup_covers_every_chain() -> None:
    # ALL_FORK_VERSIONS is keyed by genesis fork version, so a collision would
    # silently drop a chain from the --devnet_chain_setting collision check
    # rather than failing loudly.
    assert len(ALL_FORK_VERSIONS) == len(ALL_CHAINS)


@pytest.mark.parametrize('chain', ALL_CHAINS.keys())
def test_fork_versions_are_four_bytes(chain: str) -> None:
    setting = get_chain_setting(chain)
    assert len(setting.GENESIS_FORK_VERSION) == 4
    assert len(setting.EXIT_FORK_VERSION) == 4


@pytest.mark.parametrize('chain,chain_id', JOC_FAMILY)
def test_joc_family_fork_versions_encode_the_chain_id(chain: str, chain_id: int) -> None:
    # Leading byte is the fork number (00 = phase0, 03 = capella), trailing
    # three bytes are the chain id.
    setting = get_chain_setting(chain)
    assert setting.GENESIS_FORK_VERSION == b'\x00' + chain_id.to_bytes(3, 'big')
    assert setting.EXIT_FORK_VERSION == b'\x03' + chain_id.to_bytes(3, 'big')


@pytest.mark.parametrize('chain,chain_id', JOC_FAMILY)
def test_joc_family_deposits_are_denominated_in_whole_native_tokens(chain: str, chain_id: int) -> None:
    # The JOC deposit contract takes the native token directly (>= 1 ether,
    # 32 to activate), so there is no Gnosis-style multiplier.
    setting = get_chain_setting(chain)
    assert setting.MULTIPLIER == 1
    assert setting.MIN_ACTIVATION_AMOUNT == 32
    assert setting.MIN_DEPOSIT_AMOUNT == 1
