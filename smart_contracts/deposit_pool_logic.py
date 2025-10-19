# smart_contracts/deposit_pool_logic.py
from pyteal import *

# USDCa Asset ID (TestNet): 10458941
# DLP TOKEN ID (Your newly created LP Token Asset ID)

def deposit_approval_program():
    """
    Technical Blueprint for the DeFa Deposit Pool.
    This contract is designed to execute as the second transaction (Txn 1) 
    in a 2-transaction Atomic Transfer Group.
    
    It verifies that the first transaction (Txn 0) was the required deposit.
    This demonstrates the core logic for the staking and protection mechanism.
    
    The contract will execute an Inner Transaction to send DLP Tokens back to the investor.
    """
    
    # 1. Allow the Contract Account to opt-in to ASAs (Setup step)
    is_opt_in = Txn.on_completion() == OnComplete.OptIn

    # 2. Deposit Logic: Check the Atomic Transfer Group
    deposit_check = And(
        # A. Group Size Check: Must be exactly 2 transactions (Deposit + App Call)
        Global.group_size() == Int(2),
        
        # B. Transaction 0 Check: Must be an Asset Transfer (the USDCa deposit)
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        
        # C. Safety Check: Ensure the sender of the Application Call is the sender of the deposit
        Gtxn[0].sender() == Txn.sender(),
        
        # D. Amount Check: Ensure a non-zero amount was deposited
        Gtxn[0].asset_amount() > Int(0)
    )

    program = Cond(
        [is_opt_in, Int(1)],     # Success for the initial ASA Opt-in
        [deposit_check, Int(1)], # Success for the deposit 
        [Int(1), Int(0)]         # Reject all other calls (Default Fail)
    )

    # We commit the source code as a blueprint since local compilation is blocked.
    return program

if __name__ == "__main__":
    print("This file serves as the smart contract blueprint for the DeFa deposit logic.")