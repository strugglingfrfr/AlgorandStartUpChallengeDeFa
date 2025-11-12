import { useState } from "react";
import algosdk from "algosdk";
import { PeraWalletConnect } from "@perawallet/connect";

const pera = new PeraWalletConnect();
const algod = new algosdk.Algodv2(
  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "http://localhost",
  4001
);

// Replace with your deployed values
const APP_ID = 1002;
const USDC_ASA = 10458941;
const DLP_ASA = 1001;

export default function App() {
  const [account, setAccount] = useState<string | null>(null);
  const [amount, setAmount] = useState<string>("");

  async function connectWallet() {
    try {
      const accounts = await pera.connect();
      setAccount(accounts[0]);
    } catch (err) {
      console.error("Wallet connect error:", err);
    }
  }

  async function handleDeposit() {
    if (!account || !amount) return alert("Connect wallet and enter amount");

    const sp = await algod.getTransactionParams().do();
    const txn = algosdk.makeApplicationNoOpTxnFromObject({
      sender: account,
      appIndex: APP_ID,
      appArgs: [new Uint8Array(Buffer.from("deposit"))],
      suggestedParams: sp,
    });

    console.log("Prepared TXN:", txn);
    alert(`Simulated deposit of ${amount} USDCa for ${account.slice(0, 10)}...`);
  }

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h2>DeFa Deposit Pool (Algorand LocalNet)</h2>
      <button onClick={connectWallet}>
        {account ? `Connected: ${account.slice(0, 8)}...` : "Connect Wallet"}
      </button>

      <div style={{ marginTop: "1rem" }}>
        <input
          type="number"
          placeholder="Amount in USDCa"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          style={{ marginRight: "1rem" }}
        />
        <button onClick={handleDeposit}>Deposit</button>
      </div>
    </div>
  );
}
