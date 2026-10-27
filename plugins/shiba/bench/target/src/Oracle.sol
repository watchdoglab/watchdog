// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

interface IPair {
    function getReserves() external view returns (uint112, uint112, uint32);
}

interface IFeed {
    function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80);
}

contract Oracle {
    address public owner;
    IPair public pair;
    IFeed public feed;

    constructor(address _pair, address _feed) {
        owner = msg.sender;
        pair = IPair(_pair);
        feed = IFeed(_feed);
    }

    function setPair(address _pair) external {
        require(msg.sender == owner, "owner");
        pair = IPair(_pair);
    }

    function getPrice() public view returns (uint256) {
        (uint112 r0, uint112 r1, ) = pair.getReserves();
        return (uint256(r1) * 1e18) / uint256(r0);
    }

    function getEthUsd() public view returns (uint256) {
        (, int256 answer, , , ) = feed.latestRoundData();
        return uint256(answer);
    }
}
