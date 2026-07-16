// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract PolicyRegistry {
    struct Asset {
        address owner;
        address recipient;
        bytes32 capsuleHash;
        string cid;
        bool active;
    }

    struct Account {
        address user;
        string publicKey;
    }

    uint256 public assetCount;
    mapping(uint256 => Asset) public assets;

    mapping(address => Account) public accounts;

    event AccountRegistered(address indexed user, string publicKey);
    
    function registerAccount(string calldata publicKey) external {
        accounts[msg.sender] = Account(msg.sender, publicKey);
        emit AccountRegistered(msg.sender, publicKey);
    }

    event AssetRegistered(
        uint256 indexed assetId,
        address indexed owner,
        address indexed recipient,
        bytes32 capsuleHash,
        string cid
    );

    function registerAsset(
        address recipient,
        bytes32 capsuleHash,
        string calldata cid
    ) external returns (uint256) {
        assets[++assetCount] = Asset(
            msg.sender,
            recipient,
            capsuleHash,
            cid,
            true
        );

        emit AssetRegistered(
            assetCount,
            msg.sender,
            recipient,
            capsuleHash,
            cid
        );

        return assetCount;
    }

    event AccessRequested(uint256 indexed assetId, address indexed recipient);

    function requestAccess(uint256 assetId) external {
        require(assets[assetId].active, "Asset not active");
        emit AccessRequested(assetId, msg.sender);
    }

}
