"""
PRA Calculation with Dempster-Shafer Rule of Combination
======================================================

Usage:
    python3 pra_ds.py            # interactive mode
    python3 pra_ds.py --demo     # run a built-in example
"""

import sys


# ----------------------------------------------------------------------
# Core: Component class & DS combination
# ----------------------------------------------------------------------
class Component:
    def __init__(self, name="", m=None):
        self.name = name
        self.children = []
        self.m = m if m is not None else [0.0, 0.0, 1.0]  # default: total ignorance

    @property
    def count(self):
        return len(self.children)

    def add_child(self, child):
        self.children.append(child)

    def risk_estimation(self):
        """Recursive risk estimation per Algorithm 1."""
        if self.count == 0:               # Evidence (leaf) node
            return self.m

        # Combine all children via DS rule
        combined = self.children[0].risk_estimation()
        for child in self.children[1:]:
            combined = ds_combine(combined, child.risk_estimation())

        self.m = combined
        return self.m


def ds_combine(m1, m2):
    """
    Dempster-Shafer rule of combination.
    m1, m2 : [m(p), m(q), m({p,q})]
    Returns the combined m-vector.
    """
    m1_p, m1_q, m1_pq = m1
    m2_p, m2_q, m2_pq = m2

    # Conflict
    K = 1.0 - (m1_p * m2_q + m1_q * m2_p)
    if abs(K) < 1e-12:
        raise ValueError("Total conflict (K=0); evidence cannot be combined.")

    m_p  = (m1_p * m2_p + m1_p * m2_pq + m1_pq * m2_p)  / K
    m_q  = (m1_q * m2_q + m1_q * m2_pq + m1_pq * m2_q)  / K
    m_pq = (m1_pq * m2_pq) / K
    return [m_p, m_q, m_pq]


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def validate_m(m, tol=1e-3):
    if any(x < 0 for x in m):
        return False, "m-values must be non-negative."
    s = sum(m)
    if abs(s - 1.0) > tol:
        return False, f"m-values must sum to 1.0 (got {s:.4f})."
    return True, "OK"


def print_tree(node, depth=0):
    indent = "  " * depth
    tag = "[LEAF]" if node.count == 0 else "      "
    print(f"{indent}- {node.name} {tag}  "
          f"m(p)={node.m[0]:.4f}  m(q)={node.m[1]:.4f}  m(p,q)={node.m[2]:.4f}")
    for c in node.children:
        print_tree(c, depth + 1)


# ----------------------------------------------------------------------
# Interactive tree builder
# ----------------------------------------------------------------------
def get_m_values(node_name):
    print(f"\n  Enter m-values for leaf '{node_name}' (must sum to 1):")
    while True:
        try:
            mp  = float(input("    m(p)      = "))
            mq  = float(input("    m(q)      = "))
            mpq = float(input("    m({p,q})  = "))
            ok, msg = validate_m([mp, mq, mpq])
            if ok:
                return [mp, mq, mpq]
            print(f"    ! {msg}  Try again.")
        except ValueError:
            print("    ! Invalid number. Try again.")


def build_tree(name="Root", depth=0):
    indent = "  " * depth
    print(f"\n{indent}>>> Defining node: '{name}'")
    while True:
        try:
            n = int(input(f"{indent}    How many children does '{name}' have? "))
            if n >= 0:
                break
        except ValueError:
            pass
        print(f"{indent}    ! Enter a non-negative integer.")

    node = Component(name=name)
    if n == 0:
        node.m = get_m_values(name)
    else:
        for i in range(n):
            child_name = input(f"{indent}    Name of child {i+1} of '{name}': ").strip() \
                         or f"{name}.{i+1}"
            node.add_child(build_tree(child_name, depth + 1))
    return node


# ----------------------------------------------------------------------
# Demo (non-interactive sanity check)
# ----------------------------------------------------------------------
def demo():
    """Three-leaf example so you can verify the math by hand."""
    print("DEMO TREE")
    print("  Root")
    print("  ├── E1   m = [0.8, 0.2, 0.0]")
    print("  ├── E2   m = [0.8, 0.1, 0.1]")
    print("  ├── E3   m = [0.7, 0.1, 0.2]")
    print("  └── E4   m = [0.85, 0.05, 0.1]")

    root = Component("Root")
    root.add_child(Component("E1", [0.8, 0.2, 0.0]))
    root.add_child(Component("E2", [0.8, 0.1, 0.1]))
    root.add_child(Component("E3", [0.7, 0.1, 0.2]))
    root.add_child(Component("E4", [0.85, 0.05, 0.1]))

    final = root.risk_estimation()

    print("\nResult:")
    print_tree(root)
    print(f"\n  Combined  m(p)={final[0]:.6f}  "
          f"m(q)={final[1]:.6f}  m(p,q)={final[2]:.6f}  "
          f"sum={sum(final):.6f}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
        return

    print("=" * 62)
    print("  PRA Framework  |  Dempster-Shafer Risk Estimation")
    print("=" * 62)
    print("Build the risk tree node-by-node. Leaves require m-values.")

    root = build_tree("Root")

    print("\n" + "=" * 62)
    print("  Running Risk_Estimation()...")
    print("=" * 62)
    final = root.risk_estimation()

    print("\nTree with computed m-values:\n")
    print_tree(root)

    print("\n" + "=" * 62)
    print("  ROOT RISK ESTIMATE")
    print(f"    m(p)      = {final[0]:.6f}")
    print(f"    m(q)      = {final[1]:.6f}")
    print(f"    m({{p,q}})  = {final[2]:.6f}")
    print(f"    sum       = {sum(final):.6f}")
    print("=" * 62)


if __name__ == "__main__":
    main()
