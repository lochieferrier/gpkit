"A module to facilitate testing GPkit against fmincon"
from gpkit import SignomialsEnabled
from simpleflight import simpleflight

def fmincon(m):
    """A method for preparing fmincon input files to run a GPkit program"""

    # Create a new dictionary mapping variables to x(i)'s for use w/ fmincon
    i = 1
    newdict = {}
    newlist = []
    for key in m.varkeys:
        if key not in m.substitutions:
            newdict[key] = 'x({0})'.format(i)
            newlist += ['x_{0}: '.format(i) + key.str_without()]
            i += 1

    cost = m.cost # needs to be before subinplace()
    constraints = m.program.constraints
    constraints.subinplace(constraints.substitutions)
    constraints.subinplace(newdict)

    # Make all constraints less than zero, return list of clean strings
    c = []
    ceq = []
    with SignomialsEnabled():
        for constraint in constraints:
            if constraint.oper == '<=':
                cc = constraint.left - constraint.right
                c += [cc.str_without("units")]
            elif constraint.oper == '>=':
                cc = constraint.right - constraint.left
                c += [cc.str_without("units")]
            elif constraint.oper == '=':
                cc = constraint.right - constraint.left
                ceq += [cc.str_without("units")]

    # Write the constraint function .m file
    with open('confun.m', 'w') as outfile:
        outfile.write("function [c, ceq] = confun(x)\n" +
                      "% Nonlinear inequality constraints\n" +
                      "c = [\n    " +
                      "\n    ".join(c).replace('**', '.^') +
                      "\n    ];\n\n" +
                      "ceq = [\n      " +
                      "\n      ".join(ceq).replace('**', '.^') + 
                      "\n      ];"
                     )

    # Differentiate the objective function w.r.t each variable
    objdiff = []
    for key in newdict:
        costdiff = cost.diff(key)
        costdiff.subinplace(newdict)
        objdiff += [costdiff.str_without("units").replace('**', '.^')]

    # Replace variables with x(i), make clean string using matlab power syntax
    cost.subinplace(newdict)
    obj = cost.str_without("units").replace('**', '.^')

    # Write the objective function .m file
    with open('objfun.m', 'w') as outfile:
        outfile.write("function [f, gradf] = objfun(x)\n" +
                      "f = " + obj + ";\n" +
                      "if nargout > 1\n" +
                      "    gradf  = [" +
                      "\n              ".join(objdiff) +
                      "];\n" +
                      "end"
                      )

    # Write a txt file for looking up original variable names
    with open('lookup.txt', 'w') as outfile:
        outfile.write("\n".join(newlist))

    # Write the main .m file for running fmincon
    with open('main.m', 'w') as outfile:
        outfile.write("x0 = ones({0},1);\n".format(i-1) +
                      "[x,fval] = ...\n" +
                      "fmincon(@objfun,x0,[],[],[],[],[],[],@confun);")

    return obj, c, ceq

if __name__ == '__main__':
    m = simpleflight()
    obj, c, ceq = fmincon(m)
