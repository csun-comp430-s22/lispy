[![main](https://github.com/csun-comp430-s22/lispy/actions/workflows/main.yaml/badge.svg)](https://github.com/csun-comp430-s22/lispy/actions/workflows/main.yaml) [![Coverage Status](https://coveralls.io/repos/github/csun-comp430-s22/lispy/badge.svg?branch=main)](https://coveralls.io/github/csun-comp430-s22/lispy?branch=main)

# lispyc

A compiler from a lisp-like language to Python, written in Python. _lispy_ is a compiled, statically typed, lexically scoped, and type-inferred LISP-like language. Rather than being based on the more modern and complex dialects of LISP, _lispy_ is based on LISP 1.5. However, it has significant adjustments and deviations from LISP 1.5. This helps the language stay small and manageable, but a lot of the differences also stem from the need to make the language statically typed rather than dynamically typed.


## Features

* Higher-order functions
* Generic lists
* Type inference

Full documentation can be found in the [manual](docs/manual.pdf).

## Examples

#### Example 1

```lisp
(let
  ((a 1) (b nil))
  (set b
    (cond
      ((greaterp a 1) (list 1 2))
      (list 3 4)
    )
  )
  (car b)
)
```
`b` is reassigned based on whether `a` is greater than 1. The entire form evaluates to `(car b)`, which retrieves the first value of the list.


#### Example 2
```lisp
(let
  (
    (add_10
      (lambda
        ((sum_floats (func (float float) float)) (x float))
        (progn
          (set x (sum_floats x 5.0))
          (sum_floats x 5.0)
        )
      )
    )
    (wrapped_sum
      (lambda
        ((a float) (b float))
        (sum a b)
      )
    )
  )
  (add_10 wrapped_sum 2.1)
)
```

A function `add_10` is defined by using a `lambda` form in the binding of a `let`. This function expects two arguments: a function which sums two floats, and a float to add 10 to. It adds 10 by adding 5 twice, the first time saving the value by reassigning the variable `x` in the scope of the function. `add_10` is called with `wrapped_sum` as the sum function and 2.1 as the value to add 10 to. `wrapped_sum` needs to wrap the special form `sum` because special forms are not higher-order functions.
