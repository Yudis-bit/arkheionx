pragma solidity ^0.8.20;

interface GenericAsset {
    function transfer(address receiver, uint256 amount) external returns (bool);
}

contract GenericLoanRouter {
    struct Tranche {
        address lender;
        uint256 principal;
        uint256 credited;
    }

    struct Loan {
        uint256 debt;
        uint8 status;
    }

    mapping(uint256 => Loan) public loans;
    mapping(uint256 => Tranche[]) public tranches;
    GenericAsset public asset;

    function repay(uint256 loanId, uint256 amount) external {
        Loan storage loan = loans[loanId];
        loan.debt -= amount;
        _distribute(loanId, amount);
        if (loan.debt == 0) {
            loan.status = 1;
        }
    }

    function _distribute(uint256 loanId, uint256 amount) internal {
        Tranche[] storage items = tranches[loanId];
        uint256 total = _totalPrincipal(loanId);
        for (uint256 index; index < items.length; index++) {
            uint256 share = (amount * items[index].principal) / total;
            items[index].credited += share;
            asset.transfer(items[index].lender, share);
        }
    }

    function _totalPrincipal(uint256 loanId) internal view returns (uint256 total) {
        Tranche[] storage items = tranches[loanId];
        for (uint256 index; index < items.length; index++) {
            total += items[index].principal;
        }
    }
}
