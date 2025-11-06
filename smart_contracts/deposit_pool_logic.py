# smart_contracts/deposit_pool_logic.py
from pyteal import *

# ==============================================================
# DeFa Deposit Pool Logic — Challenge 2 (Improved POC)
# ==============================================================

# TestNet ASA IDs
USDC_ASSET_ID = Int(10458941)      # Stablecoin deposit asset
DLP_ASSET_ID = Int(1001)  


def approval_program():
    """
    This contract demonstrates an enhanced deposit + withdraw flow:
    - Users deposit USDCa (Txn[0]) and receive DLP tokens proportionally.
    - Withdrawals burn DLP and return equivalent USDCa.
    """

    # ------------------------------------------------------------------
    # Global and local keys
    # ------------------------------------------------------------------
    global_total_deposits = Bytes("TOTAL_DEPOSITS")
    local_balance = Bytes("USER_BALANCE")

    # ------------------------------------------------------------------
    # On creation — initialize state
    # ------------------------------------------------------------------
    on_create = Seq(
        App.globalPut(global_total_deposits, Int(0)),
        Approve()
    )

    # ------------------------------------------------------------------
    # Opt-in — allows user to store local state
    # ------------------------------------------------------------------
    on_opt_in = Seq(
        App.localPut(Txn.sender(), local_balance, Int(0)),
        Approve()
    )

    # ------------------------------------------------------------------
    # Deposit logic
    # Grouped as: [0] Asset Transfer (USDCa) + [1] App Call
    # ------------------------------------------------------------------
    valid_deposit = And(
        Global.group_size() == Int(2),
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        Gtxn[0].xfer_asset() == USDC_ASSET_ID,
        Gtxn[0].asset_amount() > Int(0),
        Gtxn[0].sender() == Txn.sender()
    )

    on_deposit = Seq(
        Assert(valid_deposit),
        # Update totals
        App.globalPut(
            global_total_deposits,
            App.globalGet(global_total_deposits) + Gtxn[0].asset_amount()
        ),
        App.localPut(
            Txn.sender(),
            local_balance,
            App.localGet(Txn.sender(), local_balance) + Gtxn[0].asset_amount()
        ),
        # Inner transaction: send DLP tokens back to depositor
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.xfer_asset: DLP_ASSET_ID,
            TxnField.asset_amount: Gtxn[0].asset_amount(),
            TxnField.asset_receiver: Txn.sender(),
        }),
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # ------------------------------------------------------------------
    # Withdraw logic
    # User burns DLP tokens (Txn[0]) and gets back USDCa
    # ------------------------------------------------------------------
    valid_withdraw = And(
        Global.group_size() == Int(2),
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        Gtxn[0].xfer_asset() == DLP_ASSET_ID,
        Gtxn[0].asset_amount() > Int(0),
        Gtxn[0].sender() == Txn.sender()
    )

    on_withdraw = Seq(
        Assert(valid_withdraw),
        Assert(
            App.localGet(Txn.sender(), local_balance) >= Gtxn[0].asset_amount()
        ),
        # Update state
        App.localPut(
            Txn.sender(),
            local_balance,
            App.localGet(Txn.sender(), local_balance) - Gtxn[0].asset_amount()
        ),
        App.globalPut(
            global_total_deposits,
            App.globalGet(global_total_deposits) - Gtxn[0].asset_amount()
        ),
        # Send USDCa back to user
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.xfer_asset: USDC_ASSET_ID,
            TxnField.asset_amount: Gtxn[0].asset_amount(),
            TxnField.asset_receiver: Txn.sender(),
        }),
        InnerTxnBuilder.Submit(),
        Approve()
    )

    # ------------------------------------------------------------------
    # Router
    # ------------------------------------------------------------------
    program = Cond(
        [Txn.application_id() == Int(0), on_create],                   # Deploy
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],          # Opt-in
        [Txn.application_args[0] == Bytes("deposit"), on_deposit],     # Deposit call
        [Txn.application_args[0] == Bytes("withdraw"), on_withdraw],   # Withdraw call
    )

    return program


def clear_state_program():
    """Allow users to clear their local state."""
    return Approve()


# ----------------------------------------------------------------------
# Compile to TEAL
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print(compileTeal(approval_program(), mode=Mode.Application, version=6))

