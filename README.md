# PRA Framework — Dempster–Shafer Rule of Combination

A Python implementation of a hierarchical **Privacy Risk Assessment (PRA)** framework that aggregates evidence using the **Dempster–Shafer (DS) rule of combination**. Risk is modeled as a tree of components; each leaf carries a mass distribution over a binary frame of discernment `{p, q}`, and internal nodes recursively combine their children's masses.

---

## Table of Contents

1. [Background](#background)
2. [Requirements](#requirements)
3. [Quick Start](#quick-start)
4. [Usage](#usage)
   - [Interactive Mode](#interactive-mode)
   - [Demo Mode](#demo-mode)
   - [Programmatic Use](#programmatic-use)
5. [Algorithm](#algorithm)
6. [Worked Example](#worked-example)
7. [Limitations & Notes](#limitations--notes)
8. [File Layout](#file-layout)

---

## Background

In Dempster–Shafer evidence theory, belief over a frame of discernment is expressed as a **mass function** `m`, where each subset of the frame receives a non-negative mass and all masses sum to 1. This implementation uses the binary frame `Θ = {p, q}`, so each node carries three masses:

| Mass        | Meaning                              |
| ----------- | ------------------------------------ |
| `m(p)`      | Belief committed exactly to `p`      |
| `m(q)`      | Belief committed exactly to `q`      |
| `m({p,q})`  | Uncertainty / ignorance (either one) |

The constraint `m(p) + m(q) + m({p,q}) = 1` must hold at every leaf.

The DS rule of combination fuses two independent mass functions `m₁` and `m₂`:

```
K        = 1 − [ m₁(p)·m₂(q) + m₁(q)·m₂(p) ]
m(p)     = [ m₁(p)·m₂(p) + m₁(p)·m₂({p,q}) + m₁({p,q})·m₂(p) ]   / K
m(q)     = [ m₁(q)·m₂(q) + m₁(q)·m₂({p,q}) + m₁({p,q})·m₂(q) ]   / K
m({p,q}) = [ m₁({p,q})·m₂({p,q}) ]                               / K
```

`K` is the normalization factor that redistributes the conflicting mass.

---

## Requirements

- Python 3.7+
- No external dependencies (standard library only)

---

## Quick Start

```bash
# Run the built-in example
python3 pra_ds.py --demo

# Build your own tree interactively
python3 pra_ds.py
```

---

## Usage

### Interactive Mode

```bash
python3 pra_ds.py
```

You'll be prompted, recursively, to define each node:

1. Give the node a number of children (`0` makes it a leaf).
2. For leaves, enter `m(p)`, `m(q)`, `m({p,q})` (must sum to 1).
3. For internal nodes, name and define each child in turn.

Once the tree is built, the program runs `Risk_Estimation()` from the root, prints the full tree with combined masses, and reports the root-level estimate.

### Demo Mode

```bash
python3 pra_ds.py --demo
```

Runs a non-interactive sanity check on a 4-leaf tree so you can verify the math against a hand calculation.

### Programmatic Use

You can build a tree directly in Python instead of typing values at a prompt:

```python
from pra_ds import Component

root = Component("Root")
root.add_child(Component("A", [0.6, 0.2, 0.2]))
root.add_child(Component("B", [0.5, 0.3, 0.2]))
root.add_child(Component("C", [0.7, 0.1, 0.2]))

m = root.risk_estimation()
print(m)   # [0.8921, 0.0935, 0.0144]
```

You can also nest internal nodes:

```python
subsystem = Component("Subsystem")
subsystem.add_child(Component("L1", [0.4, 0.4, 0.2]))
subsystem.add_child(Component("L2", [0.6, 0.2, 0.2]))

root = Component("Root")
root.add_child(subsystem)
root.add_child(Component("Direct_Evidence", [0.5, 0.3, 0.2]))

print(root.risk_estimation())
```

---

## Algorithm

Direct implementation of the pseudocode:

```
class Component:
    children : Array[] Component
    count    : int
    m        : Array[] float        # [m(p), m(q), m({p,q})]

    procedure Risk_Estimation():
        if count == 0:              # evidence node
            return m
        for each child in children:
            child.m  = child.Risk_Estimation()
            m        = m ⊕ child.m  # DS rule of combination
        return m
```

In the implementation, `count` is exposed as a `@property` derived from `len(self.children)` so it stays consistent as children are added.

---

## Worked Example

Demo input:

| Leaf |  `m(p)` |  `m(q)` |  `m({p,q})` |
| ---- | ------: | ------: | ----------: |
| E1   |    0.80 |    0.20 |        0.00 |
| E2   |    0.80 |    0.10 |        0.10 |
| E3   |    0.70 |    0.10 |        0.20 |
| E4   |    0.85 |    0.05 |        0.10 |


**Step 1 —  (E1 ⊕ E2):**
```
K        = 1 − (0.80·0.10 + 0.20·0.80) = 1 − 0.24 = 0.76
m(p)     = (0.80·0.80 + 0.80·0.10 + 0.00·0.80) / 0.76 = 0.7200 / 0.76 = 0.9474
m(q)     = (0.20·0.10 + 0.20·0.10 + 0.00·0.10) / 0.76 = 0.0400 / 0.76 = 0.0526
m({p,q}) = (0.00·0.10)                          / 0.76 = 0.0000
```

**Step 2 — (E1 ⊕ E2) ⊕ E3:**
```
K        = 1 − (0.9474·0.10 + 0.0526·0.70) = 1 − 0.1316 = 0.8684
m(p)     = (0.9474·0.70 + 0.9474·0.20 + 0.0000·0.70) / 0.8684 = 0.8526 / 0.8684 = 0.9818
m(q)     = (0.0526·0.10 + 0.0526·0.20 + 0.0000·0.10) / 0.8684 = 0.0158 / 0.8684 = 0.0182
m({p,q}) = (0.0000·0.20)                              / 0.8684 = 0.0000
```

**Step 3 — ((E1 ⊕ E2) ⊕ E3) ⊕ E4:**
```
K        = 1 − (0.9818·0.05 + 0.0182·0.85) = 1 − 0.0645 = 0.9355
m(p)     = (0.9818·0.85 + 0.9818·0.10 + 0.0000·0.85) / 0.9355 = 0.9327 / 0.9355 = 0.9971
m(q)     = (0.0182·0.05 + 0.0182·0.10 + 0.0000·0.05) / 0.9355 = 0.0027 / 0.9355 = 0.0029
m({p,q}) = (0.0000·0.10)                              / 0.9355 = 0.0000
```
Combining is associative under DS rule, so the order of folding doesn't matter.

---

## API Reference

### `Component(name="", m=None)`

A node in the risk tree.

| Field      | Type                | Description                                      |
| ---------- | ------------------- | ------------------------------------------------ |
| `name`     | `str`               | Display label.                                   |
| `children` | `list[Component]`   | Child nodes (empty for leaves).                  |
| `count`    | `int` (property)    | Number of children.                              |
| `m`        | `list[float]`       | `[m(p), m(q), m({p,q})]`. Defaults to `[0,0,1]`. |

Methods:

- `add_child(child)` — append a child node.
- `risk_estimation()` — recursively combine children via DS rule and return the resulting mass vector.

### `ds_combine(m1, m2) -> list[float]`

Standalone DS combination of two mass vectors. Raises `ValueError` if `K ≈ 0` (total conflict).

### `validate_m(m, tol=1e-3) -> (bool, str)`

Checks that masses are non-negative and sum to ~1 within tolerance.

### `print_tree(node, depth=0)`

Pretty-prints a tree with each node's current mass values.

---

## Limitations & Notes

- **Frame is fixed to `{p, q}`.** Generalizing to larger frames requires a power-set–indexed mass dictionary and a different combination kernel.
- **Total conflict (`K = 0`) raises an error.** This is the well-known degenerate case of Dempster's rule (Zadeh's counterexample).
- **Independence assumption.** The DS rule assumes evidence sources are independent. Combining correlated sources can over-concentrate mass.
- **Numerical guard.** A `1e-12` epsilon protects against floating-point near-zero `K`, but extreme inputs may still produce ill-conditioned results.
- **Validation tolerance.** `validate_m` accepts sums within `±0.001` of 1.0 to allow user typing with limited precision; tighten it for programmatic use if needed.

---

---

## File Layout

```
.
├── pra_ds.py     # Implementation + CLI
├── img           # Contains original figures from the research paper
└── README.md     # This file
```

---

## License

Provided as-is for academic and research use.
