// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Generic synthetic fixture: borrower-controlled calldata (swap route) reaches a
// value-affecting external call during origination, while lender consent (the
// terms hash) does not bind that calldata. Represents a cross-token predeposit
// origination shape. No protocol/token name is encoded.

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

interface IDepositTimelock {
    function withdraw(address lender, address token, uint256 amount, bytes calldata swapData) external returns (uint256);
}

interface ISwapAdapter {
    function swap(address tokenIn, address tokenOut, uint256 amountIn, bytes calldata route) external returns (uint256);
}

contract OriginationRouter {
    struct LoanTerms {
        address borrower;
        uint256 principal;
        address collateral;
    }
    struct LenderDepositInfo {
        address lender;
        address token;
        uint256 amount;
        bytes data; // borrower-supplied; NOT bound by the terms hash
    }

    mapping(bytes32 => bool) public originated;
    IDepositTimelock public timelock;
    ISwapAdapter public adapter;

    function borrow(LoanTerms calldata terms, LenderDepositInfo[] calldata infos) external {
        require(msg.sender == terms.borrower, "only borrower");
        // Lender consent is bound to the terms hash, which omits infos[].data.
        bytes32 termsHash = keccak256(abi.encode(terms.borrower, terms.principal, terms.collateral));
        require(!originated[termsHash], "already originated");
        originated[termsHash] = true;
        _borrowFunds(terms, infos);
    }

    function _borrowFunds(LoanTerms calldata terms, LenderDepositInfo[] calldata infos) internal {
        for (uint256 i = 0; i < infos.length; i++) {
            // swapData is borrower-controlled calldata and flows into a value path.
            bytes memory swapData = infos[i].data;
            timelock.withdraw(infos[i].lender, infos[i].token, infos[i].amount, swapData);
        }
    }
}
