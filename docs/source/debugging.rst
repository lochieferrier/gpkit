Debugging
*********

Common Debugging Errors
=========================

Dual Feasible
-------------

A dual feasible error typically means that more than one unique solution meets the objective and satisfies the contraints and usually means that that one or more variables are not sufficiently constrained.  When solving with ``mosek``, the error message will tell you that the solution is dual-feasible.  When solving with ``cvxopt`` the error for a dual-feasible solution will usually display as a ``Rank`` error.  An example of a dual-feasible model is shown below. This model is dual-feasible because there are multiple values of ``x`` and ``y`` that meet the satisfy the constraint set even though the obvious value of the objective should be 1.

.. code-block:: python

    from gpkit import Variable, Model
    x = Variable("x")
    y = Variable("y")
    m = Model(x*y, [x*y >= 1])
    m.solve()

Note: When solving with ``mosek`` this model will actually solve because ``mosek`` is robust enough to handle some dual-feasible problems. The following example is a model that ``mosek`` labels as dual-feasible and will not solve. 

.. code-block:: python

    from gpkit import Variable, Model
    x = Variable("x")
    y = Variable("y")
    m = Model(x**0.01 * y, [x*y >= 1])
    m.solve()

While this model is very similar to the previous model, ``mosek`` is unable to solve this model and labels it as dual-feasible.  
