# CODE-SIMPLICITY.md — Vigil

Binding constraints. Goal: a senior reads any module in 5 minutes and finds nothing to delete. Clean Code (Martin) where it fights complexity; YAGNI everywhere. When DRY and SIMPLE conflict, SIMPLE wins.

Python + ML flavor. The *principles* are portable across projects; the *examples* are Vigil's. Pairs with `CLAUDE.md` (hard rules, architecture principles) and `CONTEXT.md` (domain vocabulary).

## CS-1 — No layers for one consumer

One CSV load + split does not need Loader → Repository → Service. Newman: layers are for independent evolution; nothing here evolves independently.

```python
# BAD — layer cake for one load
class TransactionRepository: ...
class TransactionService:
    def __init__(self, repo: TransactionRepository): ...

# GOOD — one module, one function
def load_transactions() -> pd.DataFrame: ...
```

## CS-2 — No abstractions with a single implementation

No `ABC`/`Protocol` with one implementation. You have one Scorer today. Don't build `AbstractScorer`.

```python
# BAD
class Scorer(ABC):
    @abstractmethod
    def score(self, tx) -> Score: ...
class XGBoostScorer(Scorer): ...

# GOOD
def score(transaction) -> Score: ...
```

Extract a `Protocol` when the SECOND scorer exists — your System 2 plan may add one later, but wait until it's real, not planned.

## CS-3 — No `utils.py`, no `helpers.py`

Bag files collect orphans. Name every file for what it does: `features.py`, `split.py`, `scorer.py`, `reason_codes.py`, `label_factory.py`. If you can't name it specifically, the code doesn't know its job yet.

## CS-4 — Names reveal intent

Forbidden fragments: `data`, `info`, `result`, `item`, `obj`, `process`, `handle`, `manage`, `helper`, `util`. The ML conventions `X`, `y`, `df` are tolerated only in a short local scope; anything that outlives three lines gets a real name (`transactions`, `train_split`, `fraud_rate`). Domain words come from `CONTEXT.md` (`Transaction`, `Score`, `Reason Code`) — use them exactly.

```python
# BAD
def process_data(df): ...

# GOOD
def add_velocity_features(transactions: pd.DataFrame) -> pd.DataFrame: ...
```

## CS-5 — No premature configuration

No options objects, flags, or env vars for things with exactly one value. Hardcode the constant and NAME it.

```python
# BAD
split_transactions(cfg)  # 12 knobs, one caller

# GOOD
SACRED_TEST_FRACTION = 0.20
TIME_COLUMN = "TransactionDT"
RANDOM_SEED = 42
```

A real hyperparameter sweep gets a config when you actually sweep — not before.

## CS-6 — Fail loudly, never swallow

In fraud this is safety, not style: a swallowed error becomes a mis-scored Transaction with no Reason Code — an HR-5 defect.

```python
# BAD — silently "clean", hides the failure
try:
    return score(transaction)
except Exception:
    return 0.0

# GOOD — raise; let the Decision Engine decide what an error means
if expected_columns - set(frame.columns):
    raise ValueError(f"missing columns: {expected_columns - set(frame.columns)}")
```

Same for data: don't `fillna(0)` to paper over columns you didn't expect — surface it. A silent fill can hide leakage or a broken join.

## CS-7 — Functions: small, one job, ≤ ~20 lines

If a function needs a comment to explain WHAT it does, split or rename it. Comments are for WHY only.

```python
# time-based split: random shuffle leaks the future into the past for fraud (HR-4)
transactions = transactions.sort_values(TIME_COLUMN)
```

## CS-8 — No re-export indirection

`__init__.py` marks a package; it is not a re-export hub. Import from the real module (`from vigil.features import add_velocity_features`), not through a barrel. Indirection without value.

## CS-9 — Pure transforms, no hidden mutation

Feature and split functions take a frame and RETURN a new one. No function quietly mutates a DataFrame another function owns. Pure transforms are testable, reproducible, and don't leak state between steps.

```python
# BAD — mutates the caller's frame, action-at-a-distance
def add_features(df):
    df["amount_zscore"] = zscore(df["amount"])

# GOOD — returns a new frame
def add_features(transactions: pd.DataFrame) -> pd.DataFrame:
    return transactions.assign(amount_zscore=zscore(transactions["amount"]))
```

## CS-10 — No classes where a function does

Use library classes (`XGBClassifier`, `IsolationForest`) freely — that's their job. Don't wrap YOUR code in classes for nothing: no DI containers, no singletons-as-classes. Module-level state IS the state.

```python
# GOOD — the entire model-loading layer
_scorer = None
def get_scorer():
    global _scorer
    if _scorer is None:
        _scorer = load_scorer(MODEL_PATH)
    return _scorer
```

## CS-11 — Rule of two

Extract shared code only when a SECOND real consumer exists. Until then, small duplication beats indirection.

## CS-12 — Delete, don't comment out

No commented-out code, no `# TODO`. Deferred ideas and known limitations go in `docs/tech-debt.md`. Git remembers the deleted code; the file shouldn't.

## CS-13 — Dependency discipline

Every dependency is a liability you adopt. The approved list in `CLAUDE.md` is the entire budget. "It would be slightly more convenient" is not a reason. Two extra teeth in this project:

- A new **runtime / latency-path** dep also spends your HR-7 budget (200 ms) and needs an ADR.
- A new **dev / tooling** dep needs only Daniel's diff review.

The ML ecosystem will tempt you to add ten libraries for one helper. Don't.

## Self-check before reporting done

```
[ ] Could a senior delete any file/abstraction without losing behavior? → delete it now
[ ] Any name on the forbidden list? → rename (and use CONTEXT.md domain words)
[ ] Any except that hides a failure, or fillna that hides a data gap? → surface it
[ ] Any ABC / class / config with one impl / one value? → inline it
[ ] Anything in the scorer's latency path that doesn't belong (pandas, a fresh dep)? → move or drop it (AP-1, HR-7)
```
