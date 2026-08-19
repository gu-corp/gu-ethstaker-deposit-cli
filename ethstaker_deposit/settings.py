from typing import NamedTuple
from eth_utils import decode_hex

from ethstaker_deposit import __version__

DEPOSIT_CLI_VERSION = __version__


class BaseChainSetting(NamedTuple):
    NETWORK_NAME: str
    GENESIS_FORK_VERSION: bytes
    EXIT_FORK_VERSION: bytes  # capella fork version for voluntary exits (EIP-7044)
    GENESIS_VALIDATORS_ROOT: bytes | None = None
    MULTIPLIER: int = 1
    MIN_ACTIVATION_AMOUNT: float = 32
    MIN_DEPOSIT_AMOUNT: float = 1

    def __str__(self) -> str:
        gvr_value = self.GENESIS_VALIDATORS_ROOT.hex() if self.GENESIS_VALIDATORS_ROOT is not None else 'None'
        return (f'Network {self.NETWORK_NAME}\n'
                f'  - Genesis fork version: {self.GENESIS_FORK_VERSION.hex()}\n'
                f'  - Exit fork version: {self.EXIT_FORK_VERSION.hex()}\n'
                f'  - Genesis validators root: {gvr_value}\n'
                f'  - Multiplier: {self.MULTIPLIER}\n'
                f'  - Minimum activation amount: {self.MIN_ACTIVATION_AMOUNT}'
                f'  - Minimum deposit amount: {self.MIN_DEPOSIT_AMOUNT}')


MAINNET = 'mainnet'
SEPOLIA = 'sepolia'
HOODI = 'hoodi'
EPHEMERY = 'ephemery'
GNOSIS = 'gnosis'
CHIADO = 'chiado'
JOC = 'joc'
JOCT = 'joct'

# Mainnet setting
MainnetSetting = BaseChainSetting(
    NETWORK_NAME=MAINNET,
    GENESIS_FORK_VERSION=bytes.fromhex('00000000'),
    EXIT_FORK_VERSION=bytes.fromhex('03000000'),
    GENESIS_VALIDATORS_ROOT=bytes.fromhex('4b363db94e286120d76eb905340fdd4e54bfe9f06bf33ff6cf5ad27f511bfe95'))
# Sepolia setting
SepoliaSetting = BaseChainSetting(
    NETWORK_NAME=SEPOLIA,
    GENESIS_FORK_VERSION=bytes.fromhex('90000069'),
    EXIT_FORK_VERSION=bytes.fromhex('90000072'),
    GENESIS_VALIDATORS_ROOT=bytes.fromhex('d8ea171f3c94aea21ebc42a1ed61052acf3f9209c00e4efbaaddac09ed9b8078'))
# Hoodi setting
HoodiSetting = BaseChainSetting(
    NETWORK_NAME=HOODI,
    GENESIS_FORK_VERSION=bytes.fromhex('10000910'),
    EXIT_FORK_VERSION=bytes.fromhex('40000910'),
    GENESIS_VALIDATORS_ROOT=bytes.fromhex('212f13fc4df078b6cb7db228f1c8307566dcecf900867401a92023d7ba99cb5f'))
# Ephemery setting
# From https://github.com/ephemery-testnet/ephemery-genesis/blob/master/values.env
EphemerySetting = BaseChainSetting(
    NETWORK_NAME=EPHEMERY,
    EXIT_FORK_VERSION=bytes.fromhex('4000101b'),
    GENESIS_FORK_VERSION=bytes.fromhex('1000101b'),
    # There is no builtin GENESIS_VALIDATORS_ROOT since the root changes with each reset.
    # You can manually obtain the GENESIS_VALIDATORS_ROOT with each reset on
    # https://github.com/ephemery-testnet/ephemery-genesis/releases
    GENESIS_VALIDATORS_ROOT=None)
# Gnosis setting
GnosisSetting = BaseChainSetting(
    NETWORK_NAME=GNOSIS,
    GENESIS_FORK_VERSION=bytes.fromhex('00000064'),
    EXIT_FORK_VERSION=bytes.fromhex('03000064'),
    GENESIS_VALIDATORS_ROOT=bytes.fromhex('f5dcb5564e829aab27264b9becd5dfaa017085611224cb3036f573368dbb9d47'),
    MULTIPLIER=32,
    MIN_ACTIVATION_AMOUNT=1,
    MIN_DEPOSIT_AMOUNT=0.03125)
# Chiado setting
ChiadoSetting = BaseChainSetting(
    NETWORK_NAME=CHIADO,
    GENESIS_FORK_VERSION=bytes.fromhex('0000006f'),
    EXIT_FORK_VERSION=bytes.fromhex('0300006f'),
    GENESIS_VALIDATORS_ROOT=bytes.fromhex('9d642dac73058fbf39c0ae41ab1e34e4d889043cb199851ded7095bc99eb4c1e'),
    MULTIPLIER=32,
    MIN_ACTIVATION_AMOUNT=1,
    MIN_DEPOSIT_AMOUNT=0.03125)
# Japan Open Chain settings
#
# Fork versions follow the mainnet/Gnosis convention: the leading byte is the
# fork number (00 = phase0, 03 = capella) and the trailing bytes are the chain
# id. Every network in the family must therefore land on a distinct value --
# deposits are signed against a zero genesis validators root, so the genesis
# fork version is the only thing binding a deposit signature to one chain.
# Source of truth is the network's own beacon config; verify with
# `curl <beacon>/eth/v1/config/spec`.
#
# Only long-lived public networks belong here. Ephemeral or internal ones
# should go through `--devnet_chain_setting`: registering a chain reserves its
# genesis fork version, and the devnet path then rejects that value -- so
# registering a network that gets torn down and rebuilt would lock away the
# one mechanism flexible enough to describe it.
#
# GENESIS_VALIDATORS_ROOT is unset because these beacon chains have not reached
# genesis yet -- the root is the hash of the genesis validator registry, so it
# cannot be known in advance. It MUST be populated from
# `/eth/v1/beacon/genesis` once each network genesises: while it is None,
# `exit-transaction-*` refuses to run, and EIP-7002 execution-layer exits (the
# WithdrawReceiver path) only work from the Electra fork onwards, so a network
# that is past capella but not yet past electra would have no exit path at all.
# `generate-bls-to-execution-change*` is genuinely not needed -- validators here
# are required to use 0x01 credentials from the deposit onwards -- but it shares
# the same guard.

# Joc setting -- 0x51 = 81 = chain id
JocSetting = BaseChainSetting(
    NETWORK_NAME=JOC,
    GENESIS_FORK_VERSION=bytes.fromhex('00000051'),
    EXIT_FORK_VERSION=bytes.fromhex('03000051'),
    GENESIS_VALIDATORS_ROOT=None)
# Joc testnet setting -- 0x2761 = 10081 = chain id
JoctSetting = BaseChainSetting(
    NETWORK_NAME=JOCT,
    GENESIS_FORK_VERSION=bytes.fromhex('00002761'),
    EXIT_FORK_VERSION=bytes.fromhex('03002761'),
    GENESIS_VALIDATORS_ROOT=None)


ALL_CHAINS: dict[str, BaseChainSetting] = {
    MAINNET: MainnetSetting,
    SEPOLIA: SepoliaSetting,
    HOODI: HoodiSetting,
    EPHEMERY: EphemerySetting,
    GNOSIS: GnosisSetting,
    CHIADO: ChiadoSetting,
    JOC: JocSetting,
    JOCT: JoctSetting,
}

ALL_CHAIN_KEYS: tuple[str, ...] = tuple(ALL_CHAINS.keys())


def get_chain_setting(chain_name: str = MAINNET) -> BaseChainSetting:
    return ALL_CHAINS[chain_name]


def get_devnet_chain_setting(network_name: str,
                             genesis_fork_version: str,
                             exit_fork_version: str,
                             genesis_validator_root: str | None,
                             multiplier: int | None = 1,
                             min_activation_amount: float | None = 32,
                             min_deposit_amount: float | None = 1) -> BaseChainSetting:

    return BaseChainSetting(
        NETWORK_NAME=network_name,
        GENESIS_FORK_VERSION=decode_hex(genesis_fork_version),
        EXIT_FORK_VERSION=decode_hex(exit_fork_version),
        GENESIS_VALIDATORS_ROOT=decode_hex(genesis_validator_root) if genesis_validator_root is not None else None,
        MULTIPLIER=multiplier,
        MIN_ACTIVATION_AMOUNT=min_activation_amount,
        MIN_DEPOSIT_AMOUNT=min_deposit_amount,
    )
