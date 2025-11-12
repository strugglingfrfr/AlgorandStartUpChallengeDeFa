# Algorand Standard Asset (ASA) Blueprint: DLP Tokens

**Core Feature 1:** This defines the LP Token that investors receive, which is essential for the pool's structure (as discussed in Phase B).

* **Token Name:** Decentralized Liquidity Pool Token
* **Unit Name:** DLP
* **Role:** Represents the user's fractional ownership of a specific risk-tiered loan pool.
* **Decimals:** 6 (Standard for stablecoin derivatives).
* **Compliance Features (Crucial for DeFa's Credit Insurance):**
    * **Freeze/Clawback Authority:** The contract would hold the authority to freeze or clawback tokens in specific, documented default scenarios, directly supporting the "90% credit insurance" model mentioned in the business plan.

**Associated Assets:**
* **Input Asset:** USDCa (TestNet ID: 10458941)
* **Core Logic:** `smart_contracts/deposit_pool_logic.py` handles the exchange.

## Challenge 2 – Deposit Pool Logic (Improved POC)
Successfully compiled smart contract implementing deposit and withdrawal flow.
- USDCa (ID: 10458941) deposits mint DLP tokens (ID: 1001)
- Withdrawals burn DLP and return USDCa.
- Verified compilation output in TEAL (Version 8)
