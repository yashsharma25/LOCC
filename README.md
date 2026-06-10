# LOCC

**A research tool for studying entanglement structure and LOCC protocols in multipartite quantum systems.**

This project provides a computational framework for defining multipartite quantum states, applying local operations and classical communication, computing entanglement diagnostics, and visualizing how entanglement changes under protocol steps.

The current focus is on **LOCC protocols**: adaptive processes where separated parties act locally, exchange classical information, and condition later operations on earlier measurement outcomes.

The long-term goal is to study these protocols as **branch-resolved quantum-classical trees**, rather than only as input-output state transformations.

---

## Motivation

Entanglement in LOCC protocols is not fully captured by a single final density matrix.

After a measurement, the protocol produces a branch ensemble:

```math
\{p_i, \rho_i\}
```

where each branch has a probability, a post-measurement state, and a classical transcript.

If the transcript is retained, one studies the branch-conditioned structure:

```math
\sum_i p_i E(\rho_i)
```

If the transcript is forgotten, one studies the coarse-grained state:

```math
\bar{\rho} = \sum_i p_i \rho_i
```

and its entanglement:

```math
E(\bar{\rho})
```

The difference between these two views is central to the project. Classical information can determine which entanglement structure is operationally available.

---

## Current implementation

The repository currently contains the main ingredients of a LOCC and entanglement-analysis framework:

```text
locc/
  k_party.py                         multipartite quantum state abstraction
  n_party_states.py                  example multipartite entangled states
  locc_operation.py                  local operations, measurements, conditional operations
  locc_controller.py                 sequential LOCC protocol execution
  locc_teleportation.py              teleportation example
  entanglement_measures.py           entropy and localizable-entanglement diagnostics
  entanglement_structure_bipartite.py bipartition/entropy-structure experiments
  experiments/                       exploratory examples

visualization/
  visualization_server.py            browser visualization backend
  static/                            frontend visualization code

locc_app/
  model/, controller/, view/          application-style interface
```

At present, the project supports multipartite state construction, selected entanglement diagnostics, local/conditional operations, early LOCC protocol execution, teleportation examples, and browser-based visualization.

---

## Current limitation

The implementation is not yet a complete branch-resolved LOCC analysis engine.

The current protocol controller is closer to a sequential executor. The next major step is to make measurements generate the full protocol tree:

```text
LOCC protocol
  → branch-resolved protocol tree
  → analysis tables
  → saved results
  → visualization
```

In that representation, each node would store a quantum state, probability, and classical transcript; each edge would represent a local operation, measurement outcome, or classical message.

---

## Planned research direction

The main planned abstraction is a **branch-resolved LOCC protocol tree**.

This would allow the framework to answer questions such as:

* What are all possible final states?
* What is the probability of each transcript?
* Which branches succeed?
* How does entanglement change across branches and subsystem cuts?
* What differs between branch-conditioned and coarse-grained entanglement?
* How does a multipartite resource state generate selected EPR pairs under LOCC?

The intended flagship example is **generating (k) EPR pairs from (n)-party resource states**. This setting naturally tests multipartite entanglement, LOCC branching, classical transcripts, branch-dependent corrections, and target-pair fidelity.

---

## Intended outputs

The future paper-facing version should produce synchronized outputs from the same protocol analysis object:

```text
protocol tree
node table
edge table
leaf/final-branch table
entanglement landscape
protocol summary
visualization
```

The visualization layer should render computed analysis results, not hand-placed quantities.

Every displayed probability, transcript, fidelity, success label, or entanglement value should come from the protocol analysis engine.

---

## Long-term goal

The long-term goal is to make LOCC protocols inspectable as adaptive quantum-classical processes and to study how entanglement is transformed, concentrated, hidden, revealed, or routed through local operations and classical communication.

In short:

> Entanglement in adaptive LOCC protocols should be analyzed as a branch-resolved object, because the classical transcript determines which post-measurement state is operationally available.
