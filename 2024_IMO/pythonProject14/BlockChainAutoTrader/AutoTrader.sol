// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AutoTrader {
    address public owner;
    uint256 public value;

    event PurchaseMade(uint256 value);
    event SaleMade(uint256 value);

    constructor() {
        owner = msg.sender;
    }

    function setValue(uint256 _value) public {
        require(msg.sender == owner, "Only the owner can set the value");
        value = _value;
    }

    function purchase() public payable {
        require(value > 500, "Value must be greater than 500 to purchase");
        // Example purchase logic, should include actual logic
        emit PurchaseMade(value);
    }

    function sell() public {
        require(value < 300, "Value must be less than 300 to sell");
        // Example sale logic, should include actual logic
        emit SaleMade(value);
    }
}
