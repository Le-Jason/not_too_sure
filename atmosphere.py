import math as m
import copy

class AtmosphericConditions:
    def __init__(self, temperature, pressure):
        # Specific Gas constant of dry air
        self.R = 287.053
        # Specific heat ratio of air
        self.gamma = 1.4
        self.STANDARD_PRESSURE = 101325.0
        self.STANDARD_TEMPERATURE = 293.15
        self.pressure = pressure
        self.temperature = temperature

    def get_pressure(self):
        return self.pressure

    def set_pressure(self, pressure):
        self.pressure = pressure

    def get_temperature(self):
        return self.temperature

    def set_temperature(self, temperature):
        self.temperature = temperature

    def get_density(self):
        return self.get_pressure() / (self.R * self.get_temperature())

    def get_mach_speed(self):
        # return 165.77 * 0.606 * self.get_temperature()
        return m.sqrt(self.gamma * self.R * self.get_temperature())

    # Can be computed using Sutherland's formula. In the region of -40 and
    # 40 deg Celsius the effects is highly linear so using this linear
    # approximation
    def get_kinematic_viscosity(self):
        v = 3.7291e-06 + 1.9944e-08 * self.get_temperature()
        return v / self.get_density()

    def clone(self):
        try:
            return copy.copy(self)  # Create a shallow copy
        except Exception as e:
            raise RuntimeError("Error occurred while cloning") from e

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, AtmosphericConditions):
            return False
        return (self.pressure == other.pressure) and (self.temperature == other.temperature)

    def __str__(self):
        return f"AtmosphericConditions[T={self.temperature:.2f},P={self.pressure:.2f}]"