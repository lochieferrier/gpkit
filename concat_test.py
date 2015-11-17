import gpkit
from gpkit.shortcuts import *

class Vehicle(Model):
    def setup(self):
        # Constants
        k = Var("k", 1.2, "-", "form factor")
        e = Var("e", 0.95, "-", "Oswald efficiency factor")
        mu = Var(r"\mu", 1.78e-5, "kg/m/s", "viscosity of air")
        pi = Var(r"\pi", np.pi, "-", "half of the circle constant")
        rho = Var(r"\rho", 1.23, "kg/m^3", "density of air")
        tau = Var(r"\tau", 0.12, "-", "airfoil thickness to chord ratio")
        N_ult = Var("N_{ult}", 3.8, "-", "ultimate load factor")
        V_min = Var("V_{min}", 22, "m/s", "takeoff speed")
        C_Lmax = Var("C_{L,max}", 1.5, "-", "max CL with flaps down")
        S_wetratio = Var(r"(\frac{S}{S_{wet}})", 2.05, "-", "wetted area ratio")
        W_W_coeff1 = Var("W_{W_{coeff1}}", 8.71e-5, "1/m",
                         "Wing Weight Coefficent 1")
        W_W_coeff2 = Var("W_{W_{coeff2}}", 45.24, "Pa",
                         "Wing Weight Coefficent 2")
        CDA0 = Var("(CDA0)", 0.031, "m^2", "fuselage drag area")
        W_0 = Var("W_0", 4940.0, "N", "aircraft weight excluding wing")

        # Free Variables
        D = Var("D", "N", "total drag force")
        A = Var("A", "-", "aspect ratio")
        S = Var("S", "m^2", "total wing area")
        V = Var("V", "m/s", "cruising speed")
        W = Var("W", "N", "total aircraft weight")
        Re = Var("Re", "-", "Reynold's number")
        C_D = Var("C_D", "-", "Drag coefficient of wing")
        C_L = Var("C_L", "-", "Lift coefficent of wing")
        C_f = Var("C_f", "-", "skin friction coefficient")
        W_w = Var("W_w", "N", "wing weight")

        constraints = []

        # Drag model
        C_D_fuse = CDA0/S
        C_D_wpar = k*C_f*S_wetratio
        C_D_ind = C_L**2/(pi*A*e)
        constraints += [C_D >= C_D_fuse + C_D_wpar + C_D_ind]

        # Wing weight model
        W_w_strc = W_W_coeff1*(N_ult*A**1.5*(W_0*W*S)**0.5)/tau
        W_w_surf = W_W_coeff2 * S
        constraints += [W_w >= W_w_surf + W_w_strc]

        # and the rest of the models
        constraints += [D >= 0.5*rho*S*C_D*V**2,
                        Re <= (rho/mu)*V*(S/A)**0.5,
                        C_f >= 0.074/Re**0.2,
                        W <= 0.5*rho*S*C_L*V**2,
                        W <= 0.5*rho*S*C_Lmax*V_min**2,
                        W >= W_0 + W_w]#,
                        #W <= 8000*gpkit.units("N")]
        return Model(D, constraints)

# a1, a2 = TonyAircraft(), TonyAircraft()
# planes = a1.concat(a2)
# planes.cost = a1["D"] + a2["D"]
# planes.constraints.extend([a1["S"] == 2*a2["S"]])
# sol = planes.solve()


class BlankModel(Model):
    def setup(self):
        return Model(gpkit.Monomial(1))

class Fleet(Model):
    def setup(self, mission_parameters=None, commonality=None):
        if commonality is None:
            # sweep commonalities
            pass
        if mission_parameters is None:
            # random / default missions
            mission_parameters = [{"V_{min}": 12}, {"V_{min}": 13}, {"V_{min}": 15}]

        vehicles = []
        for mp in mission_parameters:
            vehicle = Vehicle()
            mp = {vehicle[k]: v for k, v in mp.items()}
            vehicle.substitutions.update(mp)
            vehicles.append(vehicle)

        commonality_constraints = []
        commonality_vars = [gpkit.Variable("S_{common}", np.nan, "-", common_name="S")]
        tooling_params = {"S": gpkit.Variable("S", "ft^2")}
        cost = 1
        constraints = []
        substitutions = {}
        for vehicle in vehicles:
            cost *= vehicle.cost
            constraints.extend(vehicle.constraints)
            substitutions.update(vehicle.substitutions)
            for commonvar in commonality_vars:
                varname = commonvar.key.descr["common_name"]
                link = (vehicle[varname] == commonvar*tooling_params[varname])
                commonality_constraints.append(link)
        constraints.extend(commonality_constraints)
        return cost, constraints, substitutions


if __name__ == "__main__":
    Fleet().solve()
