<h1 align="center">DeFi-Exploit-PoCs</h1>

<p align="center">
  <img src="https://img.shields.io/badge/EVM_Tests-passing-brightgreen?style=flat-square" alt="EVM Tests">
  <img src="https://img.shields.io/badge/SVM_Tests-passing-brightgreen?style=flat-square" alt="SVM Tests">
</p>

<p align="center">
  <em>Deterministic Proof-of-Concept exploits for high-severity Web3 vulnerabilities across EVM, SVM, and MoveVM architectures. Maintained by Arkheionx (<a href="https://github.com/Yudis-bit">@Yudis-bit</a>).</em>
</p>

<hr>

<h2>☢️ Vulnerability Registry</h2>
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

<h2>🔒 Embargoed Research</h2>
<p><em>Vulnerabilities currently under responsible disclosure or active contest embargo. Proof of Concepts will be published post-patch.</em></p>
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

<h2>🧬 Attack Taxonomy</h2>
<ul>
  <li><strong>Logic &amp; State:</strong> Euler Finance</li>
  <li><strong>Denial of Service (DoS):</strong> Illuminate</li>
  <li><strong>Cryptography &amp; Signatures:</strong> <em>(Embargoed)</em></li>
</ul>

<hr>

<h2>🛠️ Repository Architecture &amp; Execution</h2>
<p>Environments are isolated by virtual machine. Dependencies, execution flows, and runtime assumptions are scoped per VM family.</p>

<h3>EVM (Foundry / Solidity)</h3>
<p><strong>Dependencies:</strong></p>
<pre><code>curl -L https://foundry.paradigm.xyz | bash</code></pre>
<p><strong>Execution:</strong></p>
<pre><code>forge test --fork-url $ETH_RPC_URL -vvvv</code></pre>
<p><em>(Forked block numbers are pinned in test file headers).</em></p>

<h3>SVM (Rust / Anchor / Solana)</h3>
<p><strong>Dependencies:</strong> Solana CLI, Anchor, Bankrun</p>
<p><strong>Execution:</strong></p>
<pre><code>anchor test --skip-local-validator</code></pre>

<h3>MoveVM (Aptos / Sui)</h3>
<p><strong>Execution:</strong></p>
<pre><code>aptos move test --dev</code></pre>

<hr>

<h2>📐 The Arkheionx Standard</h2>
<ul>
  <li><strong>Isolation:</strong> One exploit per file. Zero shared state across tests.</li>
  <li><strong>Deterministic Verification:</strong> Every exploit terminates with hard assertions against concrete post-exploit state.</li>
  <li><strong>Call Trace Transparency:</strong> Tests are designed for maximum trace visibility. Full call traces expose calldata manipulation and internal state transitions.</li>
  <li><strong>Real State Execution:</strong> No mocks. Exploits utilize mainnet forks at pinned block numbers or deterministic local validators with deployed bytecode.</li>
</ul>

<hr>

<h2>📁 File Naming Convention</h2>
<p><strong>Format:</strong> <code>[VM_Directory]/test/YYYY-MM-ProtocolName.[ext]</code></p>
<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>Definition</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>YYYY-MM</strong></td>
      <td>Disclosure date</td>
    </tr>
    <tr>
      <td><strong>ProtocolName</strong></td>
      <td>PascalCase</td>
    </tr>
    <tr>
      <td><strong>[ext]</strong></td>
      <td><code>.t.sol</code> for Foundry, <code>.rs</code> for Rust</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>🚨 Severity Classification</h2>
<table>
  <thead>
    <tr>
      <th>Level</th>
      <th>Definition</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🔴 <strong>Critical</strong></td>
      <td>Direct, unconditional loss of funds or protocol takeover.</td>
    </tr>
    <tr>
      <td>🔴 <strong>High</strong></td>
      <td>Loss of funds under specific conditions, or permanent DoS of core functionality.</td>
    </tr>
    <tr>
      <td>🟡 <strong>Medium</strong></td>
      <td>Conditional fund risk, governance manipulation, or reversible DoS.</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>⚖️ Disclaimer &amp; Contact</h2>
<p>This repository is provided exclusively for defensive security research, vulnerability analysis, and auditor training. Any unauthorized reproduction, deployment, or adaptation of these Proof of Concepts against live, unpatched contracts, protocols, or production systems is strictly prohibited and may violate applicable law, contractual restrictions, and responsible disclosure obligations.</p>
<p><strong>Contact:</strong> Arkheionx (<a href="https://github.com/Yudis-bit">@Yudis-bit</a>)</p>