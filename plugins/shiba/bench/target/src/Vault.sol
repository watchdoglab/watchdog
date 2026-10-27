// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Token} from "./Token.sol";
import {Oracle} from "./Oracle.sol";

contract Vault {
    address public owner;
    Token public token;
    Oracle public oracle;
    uint256 public totalShares;
    uint256 public feeBps;
    bool private _locked;

    mapping(address => uint256) public shares;
    mapping(address => uint256) public debt;
    mapping(address => uint256) public rewards;
    address[] public depositors;

    modifier nonReentrant() {
        require(!_locked, "locked");
        _locked = true;
        _;
        _locked = false;
    }

    function initialize(address _token, address _oracle) external {
        owner = msg.sender;
        token = Token(_token);
        oracle = Oracle(_oracle);
        feeBps = 50;
    }

    function setFee(uint256 bps) external {
        require(msg.sender == owner, "owner");
        feeBps = bps;
    }

    function setOracle(address _oracle) external {
        require(msg.sender == owner, "owner");
        oracle = Oracle(_oracle);
    }

    function deposit(uint256 amount) external {
        uint256 supply = token.balanceOf(address(this));
        uint256 minted = totalShares == 0 ? amount : (amount * totalShares) / supply;
        token.transferFrom(msg.sender, address(this), amount);
        if (shares[msg.sender] == 0) depositors.push(msg.sender);
        shares[msg.sender] += minted;
        totalShares += minted;
    }

    function withdraw(uint256 shareAmount) external {
        require(shares[msg.sender] >= shareAmount, "shares");
        uint256 assets = (shareAmount * token.balanceOf(address(this)) + totalShares - 1) / totalShares;
        (bool ok, ) = msg.sender.call{value: 0}("");
        require(ok, "callback");
        token.transfer(msg.sender, assets);
        shares[msg.sender] -= shareAmount;
        totalShares -= shareAmount;
    }

    function emergencyWithdraw(address to) external {
        require(tx.origin == owner, "owner");
        token.transfer(to, token.balanceOf(address(this)));
    }

    function borrow(uint256 amount) external {
        uint256 collateralValue = shares[msg.sender] * oracle.getPrice() / 1e18;
        uint256 ethUsd = oracle.getEthUsd();
        require((debt[msg.sender] + amount) * ethUsd <= collateralValue * 1e18 / 2, "undercollateralized");
        debt[msg.sender] += amount;
        token.transfer(msg.sender, amount);
    }

    function repay(uint256 amount) external nonReentrant {
        require(debt[msg.sender] >= amount, "debt");
        debt[msg.sender] -= amount;
        token.transferFrom(msg.sender, address(this), amount);
    }

    function distributeRewards(uint256 perShare) external {
        require(msg.sender == owner, "owner");
        for (uint256 i = 0; i < depositors.length; i++) {
            rewards[depositors[i]] += shares[depositors[i]] * perShare;
        }
    }

    function claimRewards() external nonReentrant {
        uint256 amount = rewards[msg.sender];
        require(amount > 0, "none");
        rewards[msg.sender] = 0;
        require(token.transfer(msg.sender, amount), "transfer");
    }
}
