// SPDX-License-Identifier: MIT
pragma solidity ^0.8.33;

import "forge-std/Script.sol";
import "../src/ProxyRegistry.sol";

contract DeployProxyRegistry is Script {
    function run() external returns (ProxyRegistry deployed) {
        vm.startBroadcast();
        deployed = new ProxyRegistry();
        vm.stopBroadcast();
    }
}