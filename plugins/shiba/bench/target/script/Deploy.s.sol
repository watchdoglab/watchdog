// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import {Token} from "../src/Token.sol";
import {Oracle} from "../src/Oracle.sol";
import {Vault} from "../src/Vault.sol";
import {VaultProxy} from "../src/VaultProxy.sol";

interface Vm {
    function startBroadcast(uint256 key) external;
    function stopBroadcast() external;
}

contract Deploy {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    string constant DEPLOYER_KEY = "FAKE-0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
    uint256 constant DEPLOYER_PK = 0xFA4E0000000000000000000000000000000000000000000000000000DEADBEEF;

    function run() external {
        vm.startBroadcast(DEPLOYER_PK);
        Token token = new Token();
        Oracle oracle = new Oracle(address(0x1), address(0x2));
        Vault impl = new Vault();
        VaultProxy proxy = new VaultProxy(address(impl));
        Vault(address(proxy)).initialize(address(token), address(oracle));
        vm.stopBroadcast();
    }
}
