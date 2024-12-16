import math as m
from core import *
from atmosphere import *
import copy
from utils import *

class AerodynamicCalculator:
    def __init__(self):
        self.DIVISIONS = 360.0
        self.calc_map = None
        self.cache_diameter = -1.0
        self.cache_length = -1.0
        self.stall_angle = 17.5 * m.pi / 180.0
        self.stall_margin = 0.0

    def get_stall_margin(self):
        return self.stall_margin

    def get_cp(self, configuration, conditions):
        force = self.calculate_non_axial_forces(configuration, conditions)
        return force.get_cp()

    def get_aerodynamic_forces(self, configuration, conditions):
        total = self.calculate_non_axial_forces(configuration, conditions)

        total.set_cd_friction(self.calculate_cd_friction(configuration, conditions))
        total.set_cd_pressure(self.calculate_cd_pressure(configuration, conditions))
        total.set_cd_base(self.calculate_cd_base(configuration, conditions))
        total.set_cd_override(self.calculate_cd_override(configuration, conditions))

        total.set_cd(total.get_cd_friction() + total.get_cd_pressure() +
                    total.get_cd_base() + total.get_cd_override())

        total.set_cd_axial(self.calculate_cd_axial(conditions, total.get_cd()))

        self.calculate_damping_moments(configuration, conditions, total)
        total.set_cm(total.get_cm() - total.get_pitch_damping_moment())
        total.set_c_yaw(total.get_c_yaw() - total.get_yaw_damping_moment())

        self.stall_margin = self.stall_angle - conditions.get_angle_of_attack()
        return total

    def get_force_analysis(self, configuration, conditions):
        pass

    def get_worst_cp(self, configuration, conditions):
        cond = conditions.clone()
        worst = Vector3()
        cp = Vector3()
        theta = 0.0

        for ii in range(self.DIVISIONS):
            cond.get_theta(2 * m.pi * ii / self.DIVISIONS)
            cp = self.get_cp(configuration, conditions)
            norm = m.sqrt(cp.x + cp.y + cp.z)
            if (norm > 0.00000001) and (cp.x < worst.x):
                worst = cp
                theta = cond.get_theta()

        conditions.get_theta(theta)
        return worst

    def calculate_non_axial_forces(self, configuration, conditions):
        assembly_forces = AerodynamicForces()

    def calculate_cd_friction(self, configuration, conditions):
        mach = conditions.get_mach()
        Re = self.calculate_reynolds_number(configuration, conditions)
        Cf = self.calculate_friction_coefficient(configuration, mach, Re)
        roughness_correction = self.calculate_roughness_correction(mach)

    def calculate_reynolds_number(self, configuration, conditions):
        return conditions.get_velocity() * configuration.get_length_aerodynamic() / conditions.get_atmospheric_conditions().get_kinematic_viscosity()

    def calculate_friction_coefficient(self, configuration, mach, Re):
        cf = 0.0
        c1 = 1.0
        c2 = 1.0
        if (configuration.get_rocket().is_perfect_finish()):
            if (Re < 1.0e4):
                cf = 1.33e-2
            elif (Re < 5.39e5):
                # Laminar
                cf = 1.328 / m.sqrt(Re)
            else:
                # Transitional
                cf = 1.0 / ((1.50 * m.log(Re) - 5.6)**2) - 1700.0 / Re
            # Compressibility correction
            if (mach < 1.1):
                if (Re > 1.0e6):
                    c1 = 1 - 0.1 * (mach ** 2) * (Re - 1.0e6) * 2.0e6
                else:
                    c1 = 1 - 0.1 * (mach ** 2)
            if (mach > 0.9):
                if (Re > 1.0e6):
                    if (Re < 3.0e6):
                        c2 = 1 + (1.0 / ((1 + 0.045 * (mach**2)) ** 0.25) - 1) * (Re - 1.0e6) / 2.0e6
                    else:
                        c2 = 1.0 / ((1 + 0.045 * (mach**2))** 0.25)
            if (mach < 0.9):
                cf *= c1
            elif(mach < 1.1):
                cf *= (c2 * (mach - 0.9) / 0.2 + c1 * (1.1 - mach) / 0.2)
            else:
                cf *= c2
        else:
            # Assume fully turbulent
            if (Re < 1.0e4):
                cf = 1.48e-2
            else:
                cf = 1.0 / ((1.50 * m.log(Re) - 5.6)**2)
            # Compressibility correction
            if (mach < 1.1):
                c1 = 1 - 0.1 * (mach**2)
            if (mach > 0.9):
                c2 = 1 / ((1 + 0.15 * (mach**2))** 0.58)
            if (mach < 0.9):
                cf *= c1
            elif (mach < 1.1):
                cf *= c2 * (mach - 0.9) / 0.2 + c1 * (1.1 - mach) / 0.2
            else:
                cf *= c2
        return cf

    def calculate_roughness_correction(self, mach):
        c1 = 0.0
        c2 = 0.0
        roughness_correction = 0.0
        if (mach < 0.9):
            roughness_correction = 1 - 0.1 * (mach**2)
        elif (mach > 1.1):
            roughness_correction = 1 / (1 + 0.18 * (mach ** 2))
        else:
            c1 = 1 - 0.1 * (0.9 **2)
            c2 = 1.0 / (1 + 0.18 * (1.1 ** 2))
            roughness_correction = c2 * (mach - 0.9) / 0.2 + c1 * (1.1 - mach) / 0.2
        return roughness_correction

    def calculate_cd_stagnation(self, mach):
        pressure = 0.0
        if (mach <= 1.0):
            pressure = 1 + (mach ** 2) / 4 + ((mach**2) **2) / 40.0
        else:
            pressure = 1.84 - 0.76 / (mach**2) + 0.166 / ((m**2)**2) + 0.035 / ((mach * mach * mach)**2)
        return 0.85 * pressure

    def calculate_cd_base(self, mach):
        if (mach <= 1.0):
            return 0.12 + 0.13 * mach * mach
        else:
            return 0.25 / mach


    # Function to calculate the axial drag coefficient from the total drag coefficient
    def calculate_cd_axial(conditions, cd,):
        # Initialize the PolyInterpolator and calculate the polynomials
        # This part simulates the initialization of the polynomials (equivalent to Java's static block)
        angle1 = 17 * np.pi / 180
        angle2 = np.pi / 2
        # First PolyInterpolator for axialDragPoly1
        interpolator1 = PolyInterpolator([0, angle1], [0, angle1])
        axial_drag_poly1 = interpolator1.interpolator(1, 1.3, 0, 0)
        # Second PolyInterpolator for axialDragPoly2
        interpolator2 = PolyInterpolator([angle1, angle2], [angle1, angle2], [angle2])
        axial_drag_poly2 = interpolator2.interpolator(1.3, 0, 0, 0, 0)
        aoa = PygameUtils.clamp(conditions.get_angle_of_attack(), 0, np.pi)  # Ensure AOA is within [0, pi]
        mul = 0
        # Adjust AOA if it is greater than π/2 (reflecting the angle to [0, π/2])
        if aoa > np.pi / 2:
            aoa = np.pi - aoa
        # Choose the correct polynomial for interpolation based on the AOA
        if aoa < angle1:  # angle1 is 17 * π / 180
            mul = PolyInterpolator.eval(aoa, axial_drag_poly1)
        else:
            mul = PolyInterpolator.eval(aoa, axial_drag_poly2)
        # If AOA is less than π/2, return positive mul * cd; else return negative mul * cd
        if conditions.get_angle_of_attack() < np.pi / 2:
            return mul * cd
        else:
            return -mul * cd

class AerodynamicForces:
    def __init__(self):
        self.component = None
        self.cp = None
        self.cna = float('nan')
        self.cn = float('nan')
        self.cm = float('nan')
        self.c_side = float('nan')
        self.c_yaw = float('nan')
        self.c_roll = float('nan')
        self.c_roll_damp = float('nan')
        self.c_roll_force = float('nan')
        self.cd_axial = float('nan')
        self.cd = float('nan')
        self.cd_pressure = float('nan')
        self.cd_base = float('nan')
        self.cd_friction = float('nan')
        self.cd_override = float('nan')
        self.pitch_damping_moment = float('nan')
        self.yaw_damping_moment = float('nan')
        self.axis_symmetric = True

    def is_axis_symmetric(self):
        return self.axis_symmetric

    def set_axis_symmetric(self, is_sym):
        if (self.axis_symmetric == is_sym):
            return
        self.axis_symmetric = is_sym

    def set_component(self, component):
        if (self.component == component):
            return
        self.component = component

    def get_component(self):
        return self.component

    def set_cp(self, cp):
        if (self.cp == cp):
            return
        self.cp = cp

    def get_cp(self):
        return self.cp

    def set_cn(self, cn):
        if (self.cn == cn):
            return
        self.cn = cn

    def get_cn(self):
        return self.cn

    def set_cna(self, cna):
        if (self.cna == cna):
            return
        self.cna = cna

    def get_cna(self):
        return self.cna

    def set_cm(self, cm):
        if (self.cm == cm):
            return
        self.cm = cm

    def get_cm(self):
        return self.cm

    def set_c_side(self, c_side):
        if (self.c_side == c_side):
            return
        self.c_side = c_side

    def get_c_side(self):
        return self.c_side

    def set_c_yaw(self, c_yaw):
        if (self.c_yaw == c_yaw):
            return
        self.c_yaw = c_yaw

    def get_c_yaw(self):
        return self.c_yaw

    def set_c_roll(self, c_roll):
        if(self.c_roll == c_roll):
            return
        self.c_roll = c_roll

    def get_c_roll(self):
        return self.c_roll

    def set_c_roll_damp(self, c_roll_damp):
        if(self.c_roll_damp == c_roll_damp):
            return
        self.c_roll_damp = c_roll_damp

    def get_c_roll_damp(self):
        return self.c_roll_damp

    def set_c_roll_force(self, c_roll_force):
        if(self.c_roll_force == c_roll_force):
            return
        self.c_roll_force = c_roll_force

    def get_c_roll_force(self):
        return self.c_roll_force

    def set_cd_axial(self, cd_axial):
        if (self.cd_axial == cd_axial):
            return
        self.cd_axial = cd_axial

    def get_cd_axial(self):
        return self.cd_axial

    def set_cd(self, cd):
        if (self.cd == cd):
            return
        self.cd = cd

    def get_cd(self):
        if (self.component == None):
            return self.cd
        elif (self.component.is_cd_overridden_by_ancestor()):
            return 0.0
        elif (self.component.is_cd_overridden()):
            return self.component.get_override_cd()
        return self.cd

    def get_cd_total(self):
        return self.get_cd() * self.component.get_instance_count()

    def set_cd_pressure(self, cd_pressure):
        if(self.cd_pressure == cd_pressure):
            return
        self.cd_pressure = cd_pressure

    def get_cd_pressure(self):
        if (self.component == None):
            return self.cd_pressure
        elif (self.component.is_cd_overridden() or
                self.component.is_cd_overridden_by_ancestor()):
            return 0.0
        return self.cd_pressure

    def set_cd_base(self, cd_base):
        if (self.cd_base == cd_base):
            return
        self.cd_base = cd_base

    def get_cd_base(self):
        if (self.component == None):
            return self.cd_base
        elif (self.component.is_cd_overridden() or
                self.component.is_cd_overridden_by_ancestor()):
            return 0.0
        return self.cd_base

    def set_cd_friction(self, cd_friction):
        if (self.cd_friction == cd_friction):
            return
        self.cd_friction = cd_friction

    def get_cd_friction(self):
        if (self.component == None):
            return self.cd_friction
        elif (self.component.is_cd_overridden() or
                self.component.is_cd_overridden_by_ancestor()):
            return 0.0
        return self.cd_friction

    def set_cd_override(self, cd_override):
        if (self.cd_override == cd_override):
            return
        self.cd_override = cd_override

    def get_cd_override(self):
        if (self.component == None):
            return self.cd_override
        elif (not isinstance(Rocket) and
            (self.component.is_cd_overridden() or
            self.component.is_cd_overridden_by_ancestor())):
            return 0.0
        return self.cd_override

    def set_pitch_damping_moment(self, pitch_damping_moment):
        if (self.pitch_damping_moment == pitch_damping_moment):
            return
        self.pitch_damping_moment = pitch_damping_moment

    def get_pitch_damping_moment(self):
        return self.pitch_damping_moment

    def set_yaw_damping_moment(self, yaw_damping_moment):
        if (self.yaw_damping_moment == yaw_damping_moment):
            return
        self.yaw_damping_moment = yaw_damping_moment

    def get_yaw_damping_moment(self):
        return self.yaw_damping_moment

    def reset(self):
        self.set_component(None)
        self.set_cp(None)
        self.set_cna(float('nan'))
        self.set_cn(float('nan'))
        self.set_cm(float('nan'))
        self.set_c_side(float('nan'))
        self.set_c_yaw(float('nan'))
        self.set_c_roll(float('nan'))
        self.set_c_roll_damp(float('nan'))
        self.set_c_roll_force(float('nan'))
        self.set_cd_axial(float('nan'))
        self.set_cd(float('nan'))
        self.set_pitch_damping_moment(float('nan'))
        self.set_yaw_damping_moment(float('nan'))

    def zero(self):
        self.axis_symmetric(True)
        self.set_cp(Vector3())
        self.set_cna(0.0)
        self.set_cn(0.0)
        self.set_cm(0.0)
        self.set_c_side(0.0)
        self.set_c_yaw(0.0)
        self.set_c_roll(0.0)
        self.set_c_roll_damp(0.0)
        self.set_c_roll_force(0.0)
        self.set_cd_axial(0.0)
        self.set_cd(0.0)
        self.set_pitch_damping_moment(0.0)
        self.set_yaw_damping_moment(0.0)
        return self

    def clone(self):
        try:
            return copy.deepcopy(self)
        except Exception as e:
            raise RuntimeError("Error occurred while cloning") from e

    def __eq__(self, other):
        if (self == other):
            return True
        if not isinstance(other, AerodynamicForces):
            return False
        return ((self.get_cna() == other.get_cna()) and
                (self.get_cn() == other.get_cn()) and
                (self.get_cm() == other.get_cm()) and
                (self.get_c_side() == other.get_c_side()) and
                (self.get_c_yaw() == other.get_c_yaw()) and
                (self.get_c_roll() == other.get_c_roll()) and
                (self.get_c_roll_damp() == other.get_c_roll_damp()) and
				(self.get_c_roll_force(), other.get_c_roll_force()) and
				(self.get_cd_axial(), other.get_cd_axial()) and
				(self.get_cd(), other.get_cd()) and
				(self.get_cd_pressure(), other.get_cd_pressure()) and
				(self.get_cd_base(), other.get_cd_base()) and
				(self.get_cd_friction(), other.get_cd_friction()) and
				(self.get_pitch_damping_moment(), other.get_pitch_damping_moment()) and
				(self.get_yaw_damping_moment(), other.get_yaw_damping_moment()) and
				(self.get_cp() == other.get_cp()))

    def __str__(self):
        text = "AerodynamicForces["
        if self.get_component() is not None:
            text += f"component:{self.get_component()},"
        if self.get_cp() is not None:
            text += f"cp:{self.get_cp()},"
        if not self.is_nan(self.get_cna()):
            text += f"CNa:{self.get_cna()},"
        if not self.is_nan(self.get_cn()):
            text += f"CN:{self.get_cn()},"
        if not self.is_nan(self.get_cm()):
            text += f"Cm:{self.get_cm()},"
        if not self.is_nan(self.get_c_side()):
            text += f"Cside:{self.get_c_side()},"
        if not self.is_nan(self.get_c_yaw()):
            text += f"Cyaw:{self.get_c_yaw()},"
        if not self.is_nan(self.get_c_roll()):
            text += f"Croll:{self.get_c_roll()},"
        if not self.is_nan(self.get_cd_axial()):
            text += f"CDaxial:{self.get_cd_axial()},"
        if not self.is_nan(self.get_cd()):
            text += f"CD:{self.get_cd()},"
        if text.endswith(','):
            text = text[:-1]
        text += "]"
        return text

    def is_nan(self, value):
        return value != value  # NaN is not equal to itself in Python

    def merge(self, other):
        if isinstance(other, AerodynamicForces):
            self.cp = PygameUtils.vector_average(self.cp, other.cp)
            self.cna = self.cna + other.get_cna()
            self.cn = self.cn + other.get_cn()
            self.cm = self.cm + other.get_cm()
            self.c_side = self.c_side + other.get_c_side()
            self.c_yaw = self.c_yaw + other.get_c_yaw()
            self.c_roll = self.c_roll + other.get_c_roll()
            self.c_roll_damp = self.c_roll_damp + other.get_c_roll_damp()
            self.c_roll_force = self.c_roll_force + other.get_c_roll_force()
        else:
            raise ValueError("Not an Aerodynamic Force")

class FlightCondition:
    def __init__(self, config=None):
        self.MIN_BETA = 0.25
        self.ref_length = 1.0
        self.ref_area = m.pi * 0.25
        if (config is not None) and (isinstance(config, FlightConfiguration)):
            self.set_ref_length(config.get_reference_length())
        self.angle_of_attack = 0.0
        self.sin_angle_of_attack = 0.0
        # sin(aoa) / aoa
        self.sinc_angle_of_attack = 1.0
        # lateral airflow
        self.theta = 0.0
        self.mach = 0.3
        self.beta = self.compute_beta(self.mach)
        self.roll_rate = 0.0
        self.pitch_rate = 0.0
        self.yaw_rate = 0.0
        self.pitch_center = Vector3()
        self.atmospheric_conditions = AtmosphericConditions(0.0, 0.0)

    def set_reference(self, config):
        self.set_ref_length(config.get_reference_length())

    def set_ref_length(self, length):
        if (self.ref_length == length):
            return
        self.ref_length = length
        self.ref_area = m.pi * (length / 2) ** 2

    def get_ref_length(self):
        return self.ref_length

    def set_ref_area(self, area):
        if (self.ref_area == area):
            return
        self.ref_area = area
        self.ref_length = m.sqrt(area / m.pi) * 2

    def get_ref_area(self):
        return self.ref_area

    def set_angle_of_attack(self, angle_of_attack):
        angle_of_attack = max(0.0, min(angle_of_attack, m.pi))
        if (self.angle_of_attack == angle_of_attack):
            return
        self.angle_of_attack = angle_of_attack
        if (angle_of_attack < 0.001):
            self.sin_angle_of_attack = angle_of_attack
            self.sinc_angle_of_attack = 1.0
        else:
            self.sin_angle_of_attack = m.sin(angle_of_attack)
            self.sinc_angle_of_attack = self.sin_angle_of_attack / angle_of_attack

    def get_angle_of_attack(self):
        return self.angle_of_attack

    def get_sin_angle_of_attack(self):
        return self.sin_angle_of_attack

    def get_sinc_angle_of_attack(self):
        return self.sinc_angle_of_attack

    def set_theta(self, theta):
        if (self.theta == theta):
            return
        self.theta = theta

    def get_theta(self):
        return self.theta

    def set_mach(self, mach):
        mach = max(mach, 0.0)
        if (self.mach == mach):
            return
        self.mach = mach
        self.beta = self.compute_beta(mach)

    def get_mach(self):
        return self.mach

    def get_velocity(self):
        return self.mach * self.atmospheric_conditions.get_mach_speed()

    def set_velocity(self, velocity):
        self.set_mach(velocity / self.atmospheric_conditions.get_mach_speed())

    def get_beta(self):
        return self.beta

    # Compute beta (compressibility factor/Prandtl-Glauert correction factor)
    def compute_beta(self, mach):
        if (mach < 1.0):
            return max(self.MIN_BETA, m.sqrt(1.0 - mach * mach))
        else:
            return max(self.MIN_BETA, m.sqrt(mach * mach - 1.0))

    def get_roll_rate(self):
        return self.roll_rate

    def set_roll_rate(self, rate):
        if (self.roll_rate == rate):
            return
        self.roll_rate = rate

    def get_pitch_rate(self):
        return self.pitch_rate

    def set_pitch_rate(self, rate):
        if (self.pitch_rate == rate):
            return
        self.pitch_rate = rate

    def get_yaw_rate(self):
        return self.yaw_rate

    def set_yaw_rate(self, rate):
        if (self.yaw_rate == rate):
            return
        self.yaw_rate = rate

    def get_pitch_center(self):
        return self.pitch_center

    def set_pitch_center(self, pitch_center):
        if (self.pitch_center == pitch_center):
            return
        self.pitch_center = pitch_center

    def set_atmospheric_conditions(self, conditions):
        if (self.atmospheric_conditions == conditions):
            return
        self.atmospheric_conditions = conditions

    def __str__(self):
        return (f"FlightConditions["
                f"aoa={self.angle_of_attack * 180 / m.pi:.2f}°,"
                f"theta={self.theta * 180 / m.pi:.2f}°,"
                f"mach={self.mach:.3f},"
                f"rollRate={self.roll_rate:.2f},"
                f"pitchRate={self.pitch_rate:.2f},"
                f"yawRate={self.yaw_rate:.2f},"
                f"refLength={self.ref_length:.3f},"
                f"pitchCenter={self.pitch_center},"
                f"atmosphericConditions={self.atmospheric_conditions}]")

    def clone(self):
        try:
            return copy.deepcopy(self)
        except Exception as e:
            raise RuntimeError("Error occurred while cloning") from e

    def __eq__(self, other):
        if (self == other):
            return True
        if not isinstance(other, FlightCondition):
            return False
        return ((self.ref_length == other.ref_length) and
                (self.angle_of_attack == other.angle_of_attack) and
                (self.theta == other.theta) and
                (self.mach == other.mach) and
                (self.roll_rate == other.roll_rate) and
                (self.pitch_rate == other.pitch_rate) and
                (self.yaw_rate == other.yaw_rate) and
                (self.pitch_center == other.pitch_center) and
                (self.atmospheric_conditions == other.atmospheric_conditions))