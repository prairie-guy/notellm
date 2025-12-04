# Coding Style Guide

## General Principles

### Layout

- Maximum line width: 160 characters
- One line of code should implement one complete idea
- If a 1-line function body fits comfortably on the same line as `def`/`function`, put them together
- No blank line between signature and first line of code
- No blank line between docstring and code
- Minimal blank lines within function bodies—use sparingly to indicate logical sections

Example:

```python
def double(x: int) -> int: return x * 2
```

### Alignment

Align conceptually similar statement parts so differences are immediately visible:

```python
if self.store.stretch_dir==0: x = stretch_cv(x, self.store.stretch, 0)
else:                         x = stretch_cv(x, 0, self.store.stretch)
```

### Naming

Follow the Huffman Coding principle: commonly used and generic concepts get shorter names.

Follow the life-cycle principle: shorter-lived symbols get shorter names.

- **Aggressive abbreviations**: list comprehensions, lambdas, temporary variables
- **Common abbreviations**: function arguments, function names, variables
- **Light/no abbreviations**: module names, class names, constructors

Common short names: `i` (index), `k`/`v` (key/value), `o` (object in comprehension), `x` (input), `n` (count), `fn` (function), `df` (dataframe), `sz` (size)

Use domain-appropriate abbreviations consistently.

### Comments

Avoid comments unless necessary to explain *why*. Use clear symbol names and expository code to show *how*.

### Code Generation Scope

Generate only what was requested. **Do not include test code, example usage, or demonstration calls unless explicitly asked.**

Let the user decide when and how to test or use the code.

### Formatting

- Do not use automatic linters or formatters
- Align conceptually similar statement parts so differences are immediately visible

-----

## Python

### Signatures

- Keep signatures on one line when under 160 characters
- Use type hints—they serve as documentation (not enforcement)

### Docstrings

- One-line docstrings for simple functions: `"""Return the sum of x and y."""`
- Parameters should be evident from type hints; don’t repeat them in docstrings

### Casing

- `CamelCase` for classes
- `snake_case` for functions, variables, modules

-----

## Julia

### Type Annotations

Omit type annotations unless needed for multiple dispatch. When annotations are required, prefer abstract types (`AbstractArray`, `Real`, `Number`) to preserve flexibility.

### Docstrings

Standard Julia docstrings (Markdown above the function with triple quotes). Use short one-line docstrings for simple functions.

-----

## Library Preferences

### Polars

Use method chaining. Surround with parentheses, one method per line, each line starting with `.`:

```python
(df.filter(pl.col("a") > 1)
    .select("a", "b")
    .sort("a"))
```

### Altair

Use method chaining, same pattern as Polars:

```python
(alt.Chart(df)
    .mark_bar()
    .encode(
        x="category",
        y="value"))
```
