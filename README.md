<h1>DeFi-Exploit-PoCs</h1>

<p>
  <img src="https://img.shields.io/badge/EVM%20Tests-pending-lightgrey" alt="EVM Tests" />
  <img src="https://img.shields.io/badge/SVM%20Tests-pending-lightgrey" alt="SVM Tests" />
</p>

<p>Deterministic Proof-of-Concept exploits for high-severity Web3 vulnerabilities across EVM, SVM, and MoveVM architectures. Maintained by Arkheionx (@Yudis-bit).</p>

<h2>Vulnerability Registry</h2>

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Date</th>
      <th>Protocol</th>
      <th>Vulnerability Vector</th>
      <th>Severity</th>
      <th>PoC Path</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>01</td>
      <td>2022-10</td>
      <td>Illuminate / APWine</td>
      <td>DoS via 1 wei Donation</td>
      <td>🔴 High</td>
      <td><code>EVM/test/2022-10-Illuminate.t.sol</code></td>
    </tr>
    <tr>
      <td>02</td>
      <td>2023-03</td>
      <td>Euler Finance</td>
      <td>Logic Error (Donation)</td>
      <td>🔴 Critical</td>
      <td><code>EVM/test/2023-03-EulerFinance.t.sol</code></td>
    </tr>
  </tbody>
</table>

<h2>Embargoed Research</h2>

<p>Vulnerabilities currently under responsible disclosure or active contest embargo.</p>

<table>
  <thead>
    <tr>
      <th>Target Environment</th>
      <th>Vulnerability Class</th>
      <th>Expected Release</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Soroban (Stellar)</td>
      <td>Cryptography / Signature Replay</td>
      <td>TBD</td>
      <td>🟡 Pending Fix Validation</td>
    </tr>
    <tr>
      <td>EVM (Arbitrum)</td>
      <td>Logic Error / DeFi Math</td>
      <td>Q3 2026</td>
      <td>🟢 Patched</td>
    </tr>
  </tbody>
</table>

<h2>Attack Taxonomy</h2>

<ul>
  <li><strong>Logic &amp; State:</strong> Euler Finance</li>
  <li><strong>Denial of Service (DoS):</strong> Illuminate</li>
  <li><strong>Cryptography &amp; Signatures:</strong> (Embargoed)</li>
</ul>

<h2>Repository Architecture &amp; Execution</h2>

<h3>EVM (Foundry / Solidity)</h3>
<p>Dependencies: <code>curl -L https://foundry.paradigm.xyz | bash</code></p>
<pre><code>forge test --fork-url $ETH_RPC_URL -vvvv</code></pre>

<h3>SVM (Rust / Anchor / Solana)</h3>
<p>Dependencies: Solana CLI, Anchor, Bankrun</p>
<pre><code>anchor test --skip-local-validator</code></pre>

<h3>MoveVM (Aptos / Sui)</h3>
<pre><code>aptos move test --dev</code></pre>

<h2>The Arkheionx Standard</h2>

<ul>
  <li><strong>Isolation:</strong> One exploit per file. Zero shared state.</li>
  <li><strong>Deterministic Verification:</strong> Hard assertions against concrete post-exploit state.</li>
  <li><strong>Call Trace Transparency:</strong> Maximum trace visibility.</li>
  <li><strong>Real State Execution:</strong> No mocks, only mainnet forks.</li>
</ul>

<h2>File Naming Convention</h2>

<p>Format: <code>[VM_Directory]/test/YYYY-MM-ProtocolName.[ext]</code></p>

<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>Definition</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>YYYY-MM</code></td>
      <td>Disclosure date</td>
    </tr>
    <tr>
      <td><code>ProtocolName</code></td>
      <td>PascalCase</td>
    </tr>
    <tr>
      <td><code>[ext]</code></td>
      <td><code>.t.sol</code> for Foundry, <code>.rs</code> for Rust</td>
    </tr>
  </tbody>
</table>

<h2>Severity Classification</h2>

<table>
  <thead>
    <tr>
      <th>Level</th>
      <th>Definition</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🔴 Critical</td>
      <td>Direct, unconditional loss of funds or protocol takeover.</td>
    </tr>
    <tr>
      <td>🔴 High</td>
      <td>Loss of funds under specific conditions, or permanent DoS.</td>
    </tr>
    <tr>
      <td>🟡 Medium</td>
      <td>Conditional fund risk or reversible DoS.</td>
    </tr>
  </tbody>
</table>

<h2>Disclaimer &amp; Contact</h2>

<p>Provided exclusively for defensive security research. Unauthorized reproduction against live contracts is strictly prohibited.</p>
<p>Contact: <a href="https://github.com/Yudis-bit">@Yudis-bit</a></p>