// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Generic synthetic fixture: per-tranche repayment rounding / under-distribution.
// Represents a credit-market pattern where debt is reduced in scaled units before
// per-lender distribution floors token units independently. No protocol/token name
// is encoded; this is a generic shape.

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

contract LoanRouter {
    struct Tranche {
        address lender;
        uint256 principal;
        uint256 credited;
    }
    struct Loan {
        address borrower;
        uint256 debt;
        uint8 status; // 0 = Active, 1 = Repaid
        bool collateralHeld;
    }

    mapping(uint256 => Loan) public loans;
    mapping(uint256 => Tranche[]) public tranches;
    IERC20 public asset;

    function repay(uint256 loanId, uint256 amount) external {
        Loan storage loan = loans[loanId];
        require(loan.status == 0, "not active");
        // Debt is reduced in scaled units up front, before per-tranche distribution.
        loan.debt -= amount;
        _distribute(loanId, amount);
        if (loan.debt == 0) {
            loan.status = 1; // Repaid — based on debt only, not lender settlement
            _releaseCollateral(loanId);
        }
    }

    function _distribute(uint256 loanId, uint256 amount) internal {
        Tranche[] storage trs = tranches[loanId];
        uint256 total = _totalPrincipal(loanId);
        for (uint256 i = 0; i < trs.length; i++) {
            // Per-tranche flooring: integer division rounds down independently,
            // so the sum of credited can be strictly less than `amount`.
            uint256 share = (amount * trs[i].principal) / total;
            trs[i].credited += share;
            asset.transfer(trs[i].lender, share);
        }
    }

    function _releaseCollateral(uint256 loanId) internal {
        loans[loanId].collateralHeld = false;
    }

    function _totalPrincipal(uint256 loanId) internal view returns (uint256 sum) {
        Tranche[] storage trs = tranches[loanId];
        for (uint256 i = 0; i < trs.length; i++) {
            sum += trs[i].principal;
        }
    }
}
