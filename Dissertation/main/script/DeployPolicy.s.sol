// SPDX-License-Identifier: MIT
pragma solidity ^0.8.33;

import "forge-std/Script.sol";
import "../src/PolicyRegistry.sol";

contract DeployPolicy is Script {
    function run() external {
        vm.startBroadcast();
        new PolicyRegistry();
        vm.stopBroadcast();
    }
}