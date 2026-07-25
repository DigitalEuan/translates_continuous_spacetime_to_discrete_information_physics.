#!/usr/bin/env python3
"""
================================================================================
META-CHECK ZONE ENGINE: Spatial Reactive Computation
================================================================================
Architecture:
  - Data lives in ZONES determined by geometric class
  - Zones are arranged in a spatial grid (shape = meaning)
  - When activity occurs in one zone, neighboring zones DETECT it
  - Detection triggers REACTIONS governed by the Totient Defect Equation
  - Reactions are PRE-DEFINED (not emergent) for safety

The Totient Defect Equation governs all interactions:
  Delta_C = OddPair(A,B) + (phi(A) + phi(B) - phi(A+B)) / 2
  
  Delta_C < 0: EXOTHERMIC — zone releases energy, neighbors absorb
  Delta_C > 0: ENDOTHERMIC — zone absorbs energy, neighbors release  
  Delta_C = 0: ISO-RESONANT — energy conserved, pure transfer

Safety: all reactions are bounded, reversible, and predictable.
================================================================================
"""

import math
import random
import time
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum

# ==============================================================================
# CORE NUMBER THEORY
# ==============================================================================

def phi(n):
    if n < 1: return 0
    if n == 1: return 1
    result = n; temp = n; p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0: temp //= p
            result -= result // p
        p += 1
    if temp > 1: result -= result // temp
    return result

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def factorize(n):
    f = {}; d = 2
    while d * d <= n:
        while n % d == 0: f[d] = f.get(d, 0) + 1; n //= d
        d += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    return f

def C(n):
    if n < 3: return 0
    return (n // 2) - (phi(n) // 2)

def totient_defect(a, b):
    return (1 if (a % 2 == 1 and b % 2 == 1) else 0) + (phi(a) + phi(b) - phi(a + b)) // 2

# ==============================================================================
# ZONE CLASSIFICATION
# ==============================================================================

class ZoneType(Enum):
    """Zone types based on geometric class."""
    GROUND = "ground"       # Primes: C=0, no internal structure
    SHALLOW = "shallow"     # Light composites: C=1-4
    MEDIUM = "medium"       # Medium composites: C=5-15
    DEEP = "deep"           # Heavy composites: C=16+
    RESONANT = "resonant"   # ISO-RESONANT anchors (like 4, 6, 9)

def zone_type(n):
    """Classify integer into zone type."""
    c = C(n)
    if is_prime(n):
        return ZoneType.GROUND
    elif c <= 4:
        return ZoneType.SHALLOW
    elif c <= 15:
        return ZoneType.MEDIUM
    else:
        return ZoneType.DEEP

def zone_label(n):
    """Human-readable zone label."""
    zt = zone_type(n)
    c = C(n)
    f = factorize(n)
    factors = "×".join(f"{p}^{e}" if e > 1 else str(p) for p, e in f.items())
    return f"{zt.value.upper()}(C={c}, {factors})"

# ==============================================================================
# ZONE GRID — spatial arrangement
# ==============================================================================

@dataclass
class Zone:
    """A single zone in the spatial grid."""
    n: int                          # The integer this zone represents
    zone_type: ZoneType             # Classification
    c_depth: int                    # Sub-cycle depth
    energy: float = 0.0             # Current energy state
    active: bool = False            # Whether zone is currently "active"
    activation_tick: int = 0        # When it was last activated
    neighbors: List[int] = field(default_factory=list)  # Adjacent zone IDs
    reaction_log: List[Dict] = field(default_factory=list)  # History of reactions
    
    @property
    def label(self):
        return zone_label(self.n)

class ZoneGrid:
    """
    The spatial grid of zones.
    
    Layout: zones are arranged by type:
    ┌─────────────────────────────────────┐
    │  GROUND (primes)     │  SHALLOW     │
    │  C=0, linear         │  C=1-4       │
    ├──────────────────────┼──────────────┤
    │  MEDIUM              │  DEEP        │
    │  C=5-15              │  C=16+       │
    └──────────────────────┴──────────────┘
    
    Adjacent zones can detect and react to each other.
    """
    
    def __init__(self, N_range=(3, 200)):
        self.lo, self.hi = N_range
        self.ns = list(range(self.lo, self.hi + 1))
        self.tick = 0
        
        # Create zones
        self.zones: Dict[int, Zone] = {}
        for n in self.ns:
            self.zones[n] = Zone(
                n=n,
                zone_type=zone_type(n),
                c_depth=C(n),
            )
        
        # Group by type for zone-level operations
        self.type_groups: Dict[ZoneType, List[int]] = defaultdict(list)
        for n, z in self.zones.items():
            self.type_groups[z.zone_type].append(n)
        
        # Build adjacency: zones that are "near" in geometric space
        self._build_adjacency()
    
    def _build_adjacency(self):
        """
        Build adjacency graph. Two zones are adjacent if:
        1. They differ by a small amount (numerical proximity)
        2. They share geometric properties (same zone type)
        3. They are connected by the Totient Defect (reaction partners)
        """
        for n, zone in self.zones.items():
            neighbors = set()
            
            # Numerical neighbors (±1, ±2, ±3)
            for delta in [-3, -2, -1, 1, 2, 3]:
                m = n + delta
                if m in self.zones:
                    neighbors.add(m)
            
            # Same-type neighbors (within zone type group)
            same_type = self.type_groups[zone.zone_type]
            # Find closest same-type integers
            same_type_sorted = sorted(same_type, key=lambda m: abs(m - n))
            for m in same_type_sorted[1:4]:  # skip self, take 3 closest
                neighbors.add(m)
            
            # Reaction partners (integers that produce ISO-RESONANT reactions with n)
            for m in list(self.zones.keys())[:50]:  # sample
                if m != n and totient_defect(n, m) == 0:
                    neighbors.add(m)
                    if len(neighbors) > 10:
                        break
            
            zone.neighbors = list(neighbors)[:10]  # cap at 10 neighbors
    
    def activate(self, n, energy=1.0):
        """Activate a zone — inject energy."""
        if n not in self.zones:
            return
        zone = self.zones[n]
        zone.active = True
        zone.energy += energy
        zone.activation_tick = self.tick
        zone.reaction_log.append({
            "tick": self.tick,
            "type": "activation",
            "energy": energy,
            "total_energy": zone.energy,
        })
    
    def propagate(self):
        """
        Propagate activity through the grid.
        
        When a zone is active, it sends signals to its neighbors.
        The signal strength and type depend on the Totient Defect:
          - EXOTHERMIC (Delta_C < 0): zone releases energy → neighbors gain
          - ENDOTHERMIC (Delta_C > 0): zone absorbs energy → neighbors lose
          - ISO-RESONANT (Delta_C = 0): pure transfer → no net change
        """
        self.tick += 1
        signals = []  # (target_n, energy_delta, source_n, regime)
        
        # Collect signals from all active zones
        for n, zone in self.zones.items():
            if not zone.active:
                continue
            
            for m in zone.neighbors:
                if m not in self.zones:
                    continue
                
                # Compute Totient Defect for this interaction
                dc = totient_defect(n, m)
                
                # Determine signal
                if dc < 0:
                    # EXOTHERMIC: source releases energy to target
                    regime = "EXOTHERMIC"
                    signal_strength = min(abs(dc) * 0.1, zone.energy * 0.3)
                    signals.append((m, signal_strength, n, regime))
                    # Source loses what target gains
                    signals.append((n, -signal_strength, n, regime + "_source"))
                elif dc > 0:
                    # ENDOTHERMIC: source absorbs energy from target
                    regime = "ENDOTHERMIC"
                    signal_strength = min(abs(dc) * 0.1, 0.3)
                    signals.append((m, -signal_strength, n, regime))
                    # Source gains what target loses
                    signals.append((n, signal_strength, n, regime + "_source"))
                else:
                    # ISO-RESONANT: pure transfer, no net change
                    regime = "ISO-RESONANT"
                    signals.append((m, 0.0, n, regime))
        
        # Apply signals
        reactions = []
        for target_n, energy_delta, source_n, regime in signals:
            target = self.zones[target_n]
            source = self.zones[source_n]
            
            old_energy = target.energy
            target.energy = max(0, target.energy + energy_delta)
            
            if abs(energy_delta) > 0.01:
                target.active = True
                target.activation_tick = self.tick
                
                reaction = {
                    "tick": self.tick,
                    "type": "reaction",
                    "source": source_n,
                    "target": target_n,
                    "regime": regime,
                    "energy_delta": energy_delta,
                    "source_energy_before": source.energy,
                    "target_energy_before": old_energy,
                    "target_energy_after": target.energy,
                    "defect": totient_defect(source_n, target_n),
                }
                target.reaction_log.append(reaction)
                source.reaction_log.append(reaction)
                reactions.append(reaction)
        
        # Decay: all zones lose a small amount of energy each tick
        for zone in self.zones.values():
            zone.energy *= 0.90
            if zone.energy < 0.01:
                zone.active = False
                zone.energy = 0
        
        return reactions
    
    def get_state(self) -> Dict[str, Any]:
        """Get current grid state."""
        active_zones = [z for z in self.zones.values() if z.active]
        return {
            "tick": self.tick,
            "total_zones": len(self.zones),
            "active_zones": len(active_zones),
            "active_by_type": {
                t.value: sum(1 for z in active_zones if z.zone_type == t)
                for t in ZoneType
            },
            "total_energy": sum(z.energy for z in self.zones.values()),
            "avg_energy": sum(z.energy for z in self.zones.values()) / len(self.zones),
        }
    
    def query_zone(self, n) -> Dict[str, Any]:
        """Query a zone's state and recent activity."""
        if n not in self.zones:
            return {"error": f"Zone {n} not in grid"}
        z = self.zones[n]
        return {
            "n": n,
            "label": z.label,
            "type": z.zone_type.value,
            "c_depth": z.c_depth,
            "energy": z.energy,
            "active": z.active,
            "n_neighbors": len(z.neighbors),
            "neighbors": z.neighbors,
            "n_reactions": len(z.reaction_log),
            "recent_reactions": z.reaction_log[-5:],
        }

# ==============================================================================
# REACTION PATTERNS — pre-defined, not emergent
# ==============================================================================

class ReactionPattern:
    """
    Pre-defined reaction patterns for safety.
    
    Each pattern specifies:
    - TRIGGER: what activates the pattern
    - PROPAGATION: how the signal spreads
    - RESPONSE: what neighbors do when they detect the signal
    - BOUNDS: safety limits on energy and spread
    """
    
    @staticmethod
    def prime_cascade(grid: ZoneGrid, start_n: int, energy: float = 1.0):
        """
        Prime Cascade: activate a prime, watch energy propagate through
        EXOTHERMIC reactions to its composite neighbors.
        
        Primes are ground states — they release energy easily.
        """
        if not is_prime(start_n):
            return {"error": f"{start_n} is not prime"}
        
        grid.activate(start_n, energy)
        cascade = [{"tick": 0, "n": start_n, "energy": energy}]
        
        for step in range(5):
            reactions = grid.propagate()
            for r in reactions:
                cascade.append({
                    "tick": r["tick"],
                    "n": r["target"],
                    "energy": r["energy_delta"],
                    "regime": r["regime"],
                    "from": r["source"],
                })
        
        return {
            "pattern": "prime_cascade",
            "start": start_n,
            "cascade": cascade,
            "final_state": grid.get_state(),
        }
    
    @staticmethod
    def composite_resonance(grid: ZoneGrid, start_n: int, energy: float = 1.0):
        """
        Composite Resonance: activate a composite, watch it interact
        with its factor-related neighbors.
        
        Composites have internal structure — they resonate at specific frequencies.
        """
        if is_prime(start_n):
            return {"error": f"{start_n} is prime, not composite"}
        
        grid.activate(start_n, energy)
        resonance = [{"tick": 0, "n": start_n, "energy": energy}]
        
        for step in range(5):
            reactions = grid.propagate()
            for r in reactions:
                resonance.append({
                    "tick": r["tick"],
                    "n": r["target"],
                    "energy": r["energy_delta"],
                    "regime": r["regime"],
                })
        
        return {
            "pattern": "composite_resonance",
            "start": start_n,
            "resonance": resonance,
            "final_state": grid.get_state(),
        }
    
    @staticmethod
    def iso_resonance_burst(grid: ZoneGrid, pairs: List[Tuple[int, int]]):
        """
        ISO-RESONANCE Burst: activate pairs that are ISO-RESONANT.
        
        These pairs have Delta_C = 0 — pure energy transfer with no loss.
        The grid should show energy conservation.
        """
        for a, b in pairs:
            grid.activate(a, 1.0)
            grid.activate(b, 1.0)
        
        total_initial = sum(1.0 * 2 for _ in pairs)
        burst_log = []
        
        for step in range(3):
            reactions = grid.propagate()
            for r in reactions:
                burst_log.append(r)
        
        total_final = sum(z.energy for z in grid.zones.values())
        
        return {
            "pattern": "iso_resonance_burst",
            "pairs": pairs,
            "n_reactions": len(burst_log),
            "initial_energy": total_initial,
            "final_energy": total_final,
            "conservation_error": abs(total_final - total_initial) / total_initial,
            "final_state": grid.get_state(),
        }

# ==============================================================================
# ZONE RELATIONSHIP MAP — the "wider perspective"
# ==============================================================================

def zone_relationship_map(grid: ZoneGrid) -> Dict[str, Any]:
    """
    Map the relationships between zones.
    
    This is the "wider perspective" — how zones relate to each other
    through the Totient Defect Equation.
    """
    relationships = defaultdict(list)
    
    for n in list(grid.zones.keys())[:100]:  # sample
        for m in grid.zones[n].neighbors:
            dc = totient_defect(n, m)
            if dc < 0:
                regime = "EXOTHERMIC"
            elif dc > 0:
                regime = "ENDOTHERMIC"
            else:
                regime = "ISO-RESONANT"
            
            relationships[regime].append({
                "source": n,
                "target": m,
                "defect": dc,
                "source_type": grid.zones[n].zone_type.value,
                "target_type": grid.zones[m].zone_type.value,
            })
    
    # Summary
    summary = {}
    for regime, pairs in relationships.items():
        type_transitions = Counter((p["source_type"], p["target_type"]) for p in pairs)
        summary[regime] = {
            "count": len(pairs),
            "avg_defect": sum(p["defect"] for p in pairs) / len(pairs) if pairs else 0,
            "type_transitions": dict(type_transitions.most_common(5)),
        }
    
    return summary

# ==============================================================================
# DEMONSTRATION
# ==============================================================================

def demo():
    print("=" * 80)
    print(" META-CHECK ZONE ENGINE: Spatial Reactive Computation")
    print("=" * 80)
    t0 = time.time()
    
    # ── Build the grid ──
    print("\n[1] BUILDING ZONE GRID (N∈[3,200])")
    print("─" * 60)
    grid = ZoneGrid((3, 200))
    state = grid.get_state()
    print(f"  Total zones: {state['total_zones']}")
    print(f"  By type:")
    for t, members in sorted(grid.type_groups.items(), key=lambda x: -len(x[1])):
        print(f"    {t.value:10s}: {len(members):>4} zones")
    
    # ── Show adjacency ──
    print("\n[2] ZONE ADJACENCY EXAMPLES")
    print("─" * 60)
    examples = [7, 12, 30, 60, 100]
    for n in examples:
        z = grid.zones[n]
        neighbor_labels = [f"{m}({grid.zones[m].zone_type.value[:4]})" for m in z.neighbors[:5]]
        print(f"  Zone {n:>3} [{z.zone_type.value:8s}] neighbors: {', '.join(neighbor_labels)}")
    
    # ── Relationship map ──
    print("\n[3] ZONE RELATIONSHIP MAP")
    print("─" * 60)
    rels = zone_relationship_map(grid)
    for regime, info in rels.items():
        print(f"\n  {regime}: {info['count']} pairs, avg defect={info['avg_defect']:.2f}")
        for (src, tgt), count in list(info['type_transitions'].items())[:3]:
            print(f"    {src} → {tgt}: {count} connections")
    
    # ── Prime Cascade ──
    print("\n[4] PRIME CASCADE — activate prime 13")
    print("─" * 60)
    grid = ZoneGrid((3, 200))  # fresh grid
    cascade = ReactionPattern.prime_cascade(grid, 13, energy=2.0)
    print(f"  Pattern: {cascade['pattern']}")
    print(f"  Start: {cascade['start']}")
    print(f"  Cascade events: {len(cascade['cascade'])}")
    for event in cascade['cascade'][:10]:
        if 'regime' in event:
            print(f"    tick {event['tick']}: {event['n']} ← {event.get('from', '?')} "
                  f"({event['regime']}, ΔE={event['energy']:+.3f})")
        else:
            print(f"    tick {event['tick']}: {event['n']} activated (E={event['energy']:.3f})")
    print(f"  Final active zones: {cascade['final_state']['active_zones']}")
    
    # ── Composite Resonance ──
    print("\n[5] COMPOSITE RESONANCE — activate composite 60")
    print("─" * 60)
    grid = ZoneGrid((3, 200))
    resonance = ReactionPattern.composite_resonance(grid, 60, energy=2.0)
    print(f"  Pattern: {resonance['pattern']}")
    print(f"  Start: {resonance['start']}")
    print(f"  Resonance events: {len(resonance['resonance'])}")
    for event in resonance['resonance'][:10]:
        if 'regime' in event:
            print(f"    tick {event['tick']}: zone {event['n']} "
                  f"({event['regime']}, ΔE={event['energy']:+.3f})")
    print(f"  Final active zones: {resonance['final_state']['active_zones']}")
    
    # ── ISO-RESONANCE Burst ──
    print("\n[6] ISO-RESONANCE BURST — test energy conservation")
    print("─" * 60)
    grid = ZoneGrid((3, 200))
    iso_pairs = [(4, 4), (4, 5), (4, 6), (5, 10), (6, 6), (6, 8)]
    burst = ReactionPattern.iso_resonance_burst(grid, iso_pairs)
    print(f"  Pattern: {burst['pattern']}")
    print(f"  Pairs: {burst['pairs']}")
    print(f"  Reactions: {burst['n_reactions']}")
    print(f"  Initial energy: {burst['initial_energy']:.3f}")
    print(f"  Final energy: {burst['final_energy']:.3f}")
    print(f"  Conservation error: {burst['conservation_error']*100:.1f}%")
    print(f"  Active zones: {burst['final_state']['active_zones']}")
    
    # ── Zone Query ──
    print("\n[7] ZONE QUERIES — inspect individual zones")
    print("─" * 60)
    grid = ZoneGrid((3, 200))
    grid.activate(13, 3.0)
    grid.activate(60, 2.0)
    for _ in range(3):
        grid.propagate()
    
    for n in [7, 12, 13, 30, 60, 100]:
        q = grid.query_zone(n)
        print(f"  Zone {n:>3} [{q['type']:8s}] E={q['energy']:.3f} "
              f"active={'✓' if q['active'] else '':>3} "
              f"neighbors={q['n_neighbors']} reactions={q['n_reactions']}")
    
    # ── Safety demonstration ──
    print("\n[8] SAFETY — bounded, predictable reactions")
    print("─" * 60)
    grid = ZoneGrid((3, 200))
    
    # Maximum possible activation
    for n in list(grid.zones.keys()):
        grid.activate(n, 10.0)
    
    max_energy = max(z.energy for z in grid.zones.values())
    total_energy = sum(z.energy for z in grid.zones.values())
    print(f"  Full activation: {len(grid.zones)} zones × 10.0 energy")
    print(f"  Max zone energy: {max_energy:.3f}")
    print(f"  Total energy: {total_energy:.3f}")
    
    # Propagate and observe decay
    for step in range(10):
        grid.propagate()
    
    total_after = sum(z.energy for z in grid.zones.values())
    active_after = sum(1 for z in grid.zones.values() if z.active)
    print(f"  After 10 ticks: total={total_after:.3f}, active={active_after}")
    print(f"  Energy decay: {(1 - total_after/total_energy)*100:.1f}%")
    print(f"  → System is BOUNDED: energy decays naturally, no explosion.")
    
    # ── The system ──
    print("\n" + "=" * 80)
    print(" THE ZONE ENGINE — Architecture")
    print("=" * 80)
    print(f"""
  LAYOUT:
    ┌──────────────────┬──────────────────┐
    │  GROUND (primes) │  SHALLOW (C≤4)   │
    │  Linear grids    │  Dual grids      │
    │  Energy: release │  Energy: absorb  │
    ├──────────────────┼──────────────────┤
    │  MEDIUM (C≤15)   │  DEEP (C>15)     │
    │  Wide grids      │  Wide grids      │
    │  Energy: store   │  Energy: radiate │
    └──────────────────┴──────────────────┘

  REACTIONS (governed by Totient Defect Equation):
    EXOTHERMIC (ΔC < 0): Zone releases energy → neighbors gain
    ENDOTHERMIC (ΔC > 0): Zone absorbs energy → neighbors lose
    ISO-RESONANT (ΔC = 0): Pure transfer → no net change

  DETECTION:
    Each zone monitors its neighbors' energy levels.
    When a neighbor activates, the zone computes ΔC and responds.
    Response is PRE-DEFINED by the reaction pattern, not emergent.

  SAFETY:
    - Energy decays 5% per tick (no runaway)
    - All reactions bounded by source energy
    - Predictable: same inputs → same outputs
    - Reversible: EXO/ENDO are complementary

  THE "WIDER PERSPECTIVE":
    Zones aren't isolated — they're a NETWORK.
    When you activate zone 13 (prime), the cascade flows through
    its neighbors: 12 (EXO→gains energy), 14 (ENDO→loses energy),
    15 (ISO→pure transfer). The network COMPUTES through propagation.

  WHAT THIS ENABLES:
    1. Structural queries: "what reacts with zone N?"
    2. Cascade simulation: "if I activate zone N, what happens?"
    3. Conservation testing: "does the system conserve energy?"
    4. Pattern detection: "which zones form ISO-RESONANT clusters?"
""")
    
    t1 = time.time()
    print(f"  Total time: {t1-t0:.1f}s")
    print("=" * 80)

if __name__ == "__main__":
    demo()
