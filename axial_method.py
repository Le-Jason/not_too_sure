from enum import Enum, IntEnum, auto
from typing import Union


class ComponentChangeEvent:
    """
    Represents an event that signifies a change in a rocket component.
    """

    class TYPE(IntEnum):
        """
        Enumeration of change types for rocket components.
        """
        ERROR = -1
        NON_FUNCTIONAL = 1
        MASS = 2
        AERODYNAMIC = 4
        TREE = 8
        UNDO = 16
        MOTOR = 32
        EVENT = 64
        TEXTURE = 128
        GRAPHIC = 256
        TREE_CHILDREN = 512

        def __new__(cls, value):
            obj = int.__new__(cls, value)
            obj._value_ = value
            return obj

        def __init__(self, value, description=""):
            self.description = description

        def matches(self, test_value: int) -> bool:
            """
            Check if this type matches a given value using a bitwise AND operation.
            """
            return (self.value & test_value) != 0

    NONFUNCTIONAL_CHANGE = TYPE.NON_FUNCTIONAL
    MASS_CHANGE = TYPE.MASS
    AERODYNAMIC_CHANGE = TYPE.AERODYNAMIC
    AEROMASS_CHANGE = TYPE.MASS | TYPE.AERODYNAMIC
    BOTH_CHANGE = AEROMASS_CHANGE  # Alias for backward compatibility
    TREE_CHANGE = TYPE.TREE
    TREE_CHANGE_CHILDREN = TYPE.TREE_CHILDREN
    UNDO_CHANGE = TYPE.UNDO
    MOTOR_CHANGE = TYPE.MOTOR
    EVENT_CHANGE = TYPE.EVENT
    TEXTURE_CHANGE = TYPE.TEXTURE
    GRAPHIC_CHANGE = TYPE.GRAPHIC

    def __init__(self, component: 'RocketComponent', event_type: Union[int, 'ComponentChangeEvent.TYPE']):
        """
        Initialize the ComponentChangeEvent with a source component and a type.

        :param component: The RocketComponent that is the source of the event.
        :param event_type: The type of change event.
        """
        if event_type == self.TYPE.ERROR or event_type is None:
            raise ValueError("No valid event type provided.")
        self.component = component
        self.type = event_type.value if isinstance(event_type, self.TYPE) else event_type

    @staticmethod
    def get_type_enum(type_number: int) -> 'ComponentChangeEvent.TYPE':
        """
        Retrieve the TYPE enum corresponding to a type number.

        :param type_number: Integer representation of the TYPE enum.
        :return: The TYPE enum.
        :raises ValueError: If the type number does not correspond to a valid TYPE.
        """
        for type_enum in ComponentChangeEvent.TYPE:
            if type_enum.value == type_number:
                return type_enum
        raise ValueError(f"Type number {type_number} is not a valid TYPE enum.")

    def is_aerodynamic_change(self) -> bool:
        return self.TYPE.AERODYNAMIC.matches(self.type)

    def is_event_change(self) -> bool:
        return self.TYPE.EVENT.matches(self.type)

    def is_functional_change(self) -> bool:
        return not self.is_non_functional_change()

    def is_non_functional_change(self) -> bool:
        return self.TYPE.NON_FUNCTIONAL.matches(self.type)

    def is_mass_change(self) -> bool:
        return self.TYPE.MASS.matches(self.type)

    def is_texture_change(self) -> bool:
        return self.TYPE.TEXTURE.matches(self.type)

    def is_tree_change(self) -> bool:
        return self.TYPE.TREE.matches(self.type)

    def is_tree_children_change(self) -> bool:
        return self.TYPE.TREE_CHILDREN.matches(self.type)

    def is_undo_change(self) -> bool:
        return self.TYPE.UNDO.matches(self.type)

    def is_motor_change(self) -> bool:
        return self.TYPE.MOTOR.matches(self.type)

    def get_type(self) -> int:
        """
        Get the type of this event as an integer.
        """
        return self.type

    def __str__(self) -> str:
        """
        Return a string representation of the event.
        """
        changes = []
        if self.is_non_functional_change():
            changes.append("nonfunc")
        if self.is_mass_change():
            changes.append("mass")
        if self.is_aerodynamic_change():
            changes.append("aero")
        if self.is_tree_change():
            changes.append("tree")
        if self.is_tree_children_change():
            changes.append("treechild")
        if self.is_undo_change():
            changes.append("undo")
        if self.is_motor_change():
            changes.append("motor")
        if self.is_event_change():
            changes.append("event")
        return f"ComponentChangeEvent[{','.join(changes)}]"

class AxialMethod(Enum):
    """
    Enum to represent axial positioning methods for rocket components.
    """
    ABSOLUTE = auto()
    AFTER = auto()
    TOP = auto()
    MIDDLE = auto()
    BOTTOM = auto()

    @property
    def description(self) -> str:
        """
        Returns a localized description for the enum value.
        """
        translations = {
            AxialMethod.ABSOLUTE: "RocketComponent.Position.Method.Axial.ABSOLUTE",
            AxialMethod.AFTER: "RocketComponent.Position.Method.Axial.AFTER",
            AxialMethod.TOP: "RocketComponent.Position.Method.Axial.TOP",
            AxialMethod.MIDDLE: "RocketComponent.Position.Method.Axial.MIDDLE",
            AxialMethod.BOTTOM: "RocketComponent.Position.Method.Axial.BOTTOM",
        }
        # Simulate fetching translations (replace with actual translator calls if available)
        return translations[self]

    def clamp_to_zero(self) -> bool:
        """
        Determines if the position should be clamped to zero.
        """
        return False

    def get_as_position(self, offset: float, inner_length: float, outer_length: float) -> float:
        """
        Calculates the position of the component.
        """
        if self == AxialMethod.ABSOLUTE:
            return offset
        elif self == AxialMethod.AFTER:
            return outer_length + offset
        elif self == AxialMethod.TOP:
            return offset
        elif self == AxialMethod.MIDDLE:
            return offset + (outer_length - inner_length) / 2
        elif self == AxialMethod.BOTTOM:
            return offset + (outer_length - inner_length)
        else:
            raise ValueError("Unknown AxialMethod")

    def get_as_offset(self, position: float, inner_length: float, outer_length: float) -> float:
        """
        Calculates the offset of the component.
        """
        if self == AxialMethod.ABSOLUTE:
            return position
        elif self == AxialMethod.AFTER:
            return position - outer_length
        elif self == AxialMethod.TOP:
            return position
        elif self == AxialMethod.MIDDLE:
            return position + (inner_length - outer_length) / 2
        elif self == AxialMethod.BOTTOM:
            return position + (inner_length - outer_length)
        else:
            raise ValueError("Unknown AxialMethod")

    def __str__(self) -> str:
        """
        String representation of the enum, returning its description.
        """
        return self.description