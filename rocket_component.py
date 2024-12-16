import uuid
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Iterator
from utils import *
from axial_method import *
from core import *
from updated_rocket import *
from aerodynamics import *

class RocketComponent(ABC, ChangeSource):
    def __init__(self, axial_method=AxialMethod.AFTER, name=None):
        super().__init__()

        self.parent = None # Parent component of the current component
        self.children = [] # List of child components of this component
        self.length = 0.0 # Characteristic length of the component
        self.axial_method = axial_method # How this component is axially position
        self.axial_offset = 0.0 # Offset of the position of this component relative to the normal position
        self.position = Vector3() # Relative to it's parent

        self.override_mass = 0.0
        self.mass_overridden = False
        self.override_subcomponents_mass = False
        self.mass_overridden_by = None

        self.override_cg_x = 0.0
        self.cg_overridden = False
        self.override_subcomponents_cg = False
        self.cg_overridden_by = None

        self.override_cd = 0.0
        self.cd_overridden = False
        self.override_subcomponents_cd = False
        self.cd_overridden_by = None

        self.cd_overridden_by_ancestor = False

        self.name = name
        self.id = None
        self.config_listeners = []
        self.bypass_component_change_event = False

    def get_component_name(self):
        return self.name

    def get_component_mass(self):
        pass

    def get_component_cg(self):
        pass

    def get_longitudinal_unit_inertia(self):
        pass

    def get_rotational_unit_inertia(self):
        pass

    def allows_children(self):
        pass

    def is_compatible(self, component):
        return self.is_compatible_by_type(type(component))

    def is_compatible_by_type(self, component_type):
        raise NotImplementedError("Subclasses must implement this method")

    def get_component_bounds(self):
        pass

    def is_aerodynamic(self):
        pass

    def is_massive(self):
        pass

    def is_after(self):
        return (self.axial_method == AxialMethod.AFTER)

    def component_changed(self, event):
        self.check_state()
        self.update()

    def to_string(self):
        return self.name

    def clone(self):
        return deepcopy(self)

    @abstractmethod
    def __iter__(self) -> Iterator['RocketComponent']:
        pass

    def get_override_mass(self):
        if (not self.is_mass_overridden()):
            self.override_mass = self.get_component_mass()
        return self.override_mass

    def set_override_mass(self, mass):
        for listener in self.config_listeners:
            listener.set_override_mass(mass)
        if (mass == self.override_mass):
            return
        self.check_state()
        self.override_mass = max(mass, 0)
        if (self.mass_overridden):
            self.fire_component_change_event(ComponentChangeEvent.MASS_CHANGE)

    def is_mass_overridden(self):
        return self.mass_overridden

    def set_mass_overridden(self, overridden):
        for listener in self.config_listeners:
            listener.set_bypass_change_event(False)
            listener.set_mass_overridden(overridden)
            listener.set_bypass_change_event(True)
        if (self.mass_overridden == overridden):
            return
        self.check_state()
        self.mass_overridden = overridden
        if (not self.mass_overridden):
            self.override_mass = self.get_component_mass
        self.update_children_mass_overridden_by()
        self.fire_component_change_event(ComponentChangeEvent.MASS_CHANGE)

    def get_override_cg(self):
        if(not self.is_cg_overridden()):
            self.override_cg_x = self.get_component_cg().x
        return self.get_component_cg().set_x(self.override_cg_x)

    def get_override_cg_x(self):
        if (not self.is_cg_overridden()):
            self.override_cg_x = self.get_component_cg().x
        return self.override_cg_x

    def set_override_cg_x(self, x):
        for listener in self.config_listeners:
            listener.set_override_cg_x(x)
        if (self.override_cg_x == x):
            return
        self.check_state()
        self.override_cg_x = x
        if (self.is_cg_overridden()):
            self.fire_component_change_event(ComponentChangeEvent.MASS_CHANGE)
        else:
            self.fire_component_change_event(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    def is_cg_overridden(self):
        return self.cg_overridden

    def set_cg_overridden(self, overridden):
        for listener in self.config_listeners:
            listener.set_bypass_change_event(False)
            listener.set_cg_overridden(overridden)
            listener.set_bypass_change_event(True)
        if (self.cg_overridden == overridden):
            return
        self.check_state()
        self.cg_overridden = overridden
        if (not self.cg_overridden):
            self.override_cg_x = self.get_component_cg().x
        self.update_children_cg_overridden_by()
        self.fire_component_change_event(ComponentChangeEvent.MASS_CHANGE)

    def get_component_cd(self, angle_of_attack, theta, mach, roll_rate):
        rocket = Rocket()
        rocket = self.get_rocket()
        configuration = rocket.get_selected_configuration()
        conditions = FlightCondition(configuration)
        aerodynamic_calc = AerodynamicCalculator()
        conditions.set_angle_of_attack(angle_of_attack)
        conditions.set_theta(theta)
        conditions.set_mach(mach)
        conditions.set_roll_rate(roll_rate)
        aero_data = aerodynamic_calc.get_force_analysis(configuration, conditions)
        forces = aero_data.get(self)
        if (forces is not None):
            return forces.get_cd()
        return 0

    def get_override_cd(self):
        if (not self.is_cd_overridden()):
            # TODO make Preferences for mach
            self.override_cd = self.get_component_cd(0, 0, 0.3,0)
        return self.override_cd

    def set_override_cd(self, x):
        for listener in self.config_listeners:
            listener.get_override_cd(x)
        if (self.override_cd == x):
            return
        self.check_state()
        self.override_cd = x
        if (self.is_cd_overridden()):
            if (self.is_subcomponents_overridden_cd()):
                self.override_subcomponents_cd(True)
            self.fire_component_change_event(ComponentChangeEvent.AERODYNAMIC_CHANGE)
        else:
            self.fire_component_change_event(ComponentChangeEvent.NONFUNCTIONAL_CHANGE)

    def is_cd_overridden(self):
        return self.cd_overridden

    def set_cd_overridden(self, override):
        for listener in self.config_listeners:
            listener.set_cd_overridden(override)
        if (self.cd_overridden == override):
            return
        self.check_state()
        self.cd_overridden = override
        self.update_children_cd_overridden_by()
        if (self.is_subcomponents_overridden_cd()):
            self.override_subcomponents_cd(override)
        if (not self.cd_overridden):
            # TODO make Preferences for mach
            self.override_cd = self.get_component_cd(0, 0, 0.3, 0)
        self.fire_component_change_event(ComponentChangeEvent.AERODYNAMIC_CHANGE)

    def is_subcomponents_overridden_mass(self):
        return self.override_subcomponents_mass

    def set_subcomponents_overridden(self, override):
        self.set_subcomponents_overridden_mass(override)
        self.set_subcomponents_overridden_cg(override)
        self.set_subcomponents_overridden_cd(override)

    def set_subcomponents_overridden_mass(self, override):
        for listener in self.config_listeners:
            listener.set_subcompeonts_overridden_mass(override)
        if (self.override_subcomponents_mass == override):
            return
        self.check_state()
        self.override_subcomponents_mass = override
        self.update_children_mass_overridden_by()
        self.fire_component_change_event(ComponentChangeEvent.BOTH_CHANGE)
        self.fire_component_change_event(ComponentChangeEvent.TREE_CHANGE_CHILDREN)

    def is_subcomponents_overridden_cg(self):
        return self.override_subcomponents_cg

    def set_subcomponents_overridden_cg(self, override):
        for listener in self.config_listeners:
            listener.set_subcomponents_overridden_cg(override)
        if (self.override_subcomponents_cg == override):
            return
        self.check_state()
        self.override_subcomponents_cg = override
        self.update_children_cg_overridden_by()
        self.fire_component_change_event(ComponentChangeEvent.BOTH_CHANGE)
        self.fire_component_change_event(ComponentChangeEvent.TREE_CHANGE_CHILDREN)

    def set_subcomponents_overridden_cd(self, override):
        for listener in self.config_listeners:
            listener.set_subcomponents_overridden_cd(override)
        if (self.override_subcomponents_cd == override):
            return
        self.check_state()
        self.override_subcomponents_cd = override
        self.update_children_cd_overridden_by()
        self.override_subcomponents_cd(override)
        self.fire_component_change_event(ComponentChangeEvent.BOTH_CHANGE)
        self.fire_component_change_event(ComponentChangeEvent.TREE_CHANGE_CHILDREN)

    def override_subcomponents_cd(self, override):
        for child in self.children:
            if (child.is_cd_overridden_by_ancestor() != override):
                child.cd_overridden_by_ancestor = override
                if (not override and child.is_cd_overridden() and child.is_subcomponents_overridden_cd()):
                    child.override_subcomponents_cd(True)
                else:
                    child.override_subcomponents_cd(override)

    def is_override_subcomponents_enabled(self):
        return (self.is_cg_overridden() and self.is_mass_overridden() and self.is_cd_overridden)

    def get_mass_overridden_by(self):
        return self.mass_overridden_by

    def get_cg_overridden_by(self):
        return self.cg_overridden_by

    def get_cd_overridden_by(self):
        return self.cd_overridden_by

    def update_children_mass_overridden_by(self):
        overridden_by = None
        if (self.mass_overridden and self.override_subcomponents_mass):
            overridden_by = self
        for child in self.get_all_children():
            child.mass_overridden_by = self.overridden_by
            if (self.overridden_by is None):
                if (child.mass_overridden and child.override_subcomponents_mass):
                    self.overridden_by = child

    def update_children_cg_overridden_by(self):
        overridden_by = None
        if (self.mass_overridden and self.override_subcomponents_cg):
            overridden_by = self
        for child in self.get_all_children():
            child.mass_overridden_by = self.overridden_by
            if (self.overridden_by is None):
                if (child.cg_overridden and child.override_subcomponents_cg):
                    self.overridden_by = child

    def update_children_cd_overridden_by(self):
        overridden_by = None
        if (self.mass_overridden and self.override_subcomponents_cd):
            overridden_by = self
        for child in self.get_all_children():
            child.mass_overridden_by = self.overridden_by
            if (self.overridden_by is None):
                if (child.cd_overridden and child.override_subcomponents_cd):
                    self.overridden_by = child

    def get_instance_count(self):
        return 1

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def new_id(self):
        self.id = uuid.uuid4()

    def set_id(self, new_id):
        self.id = new_id

    def get_length(self):
        return self.length

    def get_axial_method(self):
        return self.axial_method

    def set_axial_method(self, new_axial_method):
        for listener in self.config_listeners:
            listener.set_axial_method(new_axial_method)
        if (new_axial_method == self.axial_method):
            return
        self.axial_method = new_axial_method
        self.axial_offset = self.get_axial_offset(new_axial_method)

    def get_axial_offset(self, as_method):
        parent_length = 0.0
        if (self.parent is not None) and (not isinstance(self.parent, Rocket)):
            parent_length = self.parent.get_length()
        if (AxialMethod.ABSOLUTE == as_method):
            return self.get_component_locations()[0].x
        else:
            return as_method.get_as_offset(self.position.x, self.get_length(), parent_length)

    def get_axial_offset(self):
        return self.axial_offset

    def get_axial_front(self):
        return self.position.x

    def is_ancestor(self, test_comp):
        cur_comp = test_comp.parent
        while (cur_comp is not None):
            if (self == cur_comp):
                return True
            cur_comp = cur_comp.parent
        return False

    def set_after(self):
        self.check_state()
        if (self.parent is None):
            return
        self.axial_method = AxialMethod.AFTER
        self.axial_offset = 0.0
        this_idx = self.parent.get_child_position(self)
        if (this_idx == 0):
            self.position.set_x(0.0)
        elif (0 < this_idx):
            idx = this_idx - 1
            reference_component = self.parent.get_child(idx)
            while ((not self.get_rocket().get_selected_configuration().is_component_active(reference_component)) and (idx > 0)):
                idx -= 1
                reference_component = self.parent.get_child(idx)
            if (not self.get_rocket().get_selected_configuration().is_component_active(reference_component)):
                self.position.set_x(0.0)
            ref_length = reference_component.get_length()
            ref_rel_x = reference_component.get_position().x
            self.position.set_x(ref_rel_x + ref_length)

    def set_axial_offset(self, requested_method, requested_offset):
        self.check_state()
        new_x = float('nan')
        if (self.parent is None):
            new_x = requested_offset
        elif (requested_method == AxialMethod.ABSOLUTE):
            new_x = requested_offset - self.parent.get_component_locations()[0].x
        elif (self.is_after()):
            self.set_after()
            return
        else:
            new_x = requested_method.get_as_position(requested_offset, self.get_length(), self.parent.get_length())
        EPSILON = 0.000001
        if (EPSILON > abs(new_x)):
            new_x = 0.0
        elif (new_x == float('nan')):
            raise ValueError("set_axial_offset is broken")
        self.axial_method = requested_method
        self.axial_offset = requested_offset
        self.position.set_x(new_x)

    def update(self):
        self.set_axial_offset(self.axial_method, self.axial_offset)

    def update_children(self):
        self.update()
        for child in self.children:
            child.update_children()

    def get_position(self):
        return self.position

    def get_instance_locations(self):
        self.check_state()
        center = self.position
        offsets = self.get_instance_offsets()
        locations = [center.add(offset) for offset in offsets]
        return locations

    def get_instance_offsets(self):
        return [Vector3()]

    def get_locations(self):
        return self.get_component_locations()

    def get_component_locations(self):
        if (self.parent is None):
            return self.get_instance_offsets()
        else:
            parent_position = self.parent.get_component_locations()
            parent_count = parent_position.length
            instance_locations = self.get_instance_locations()
            instance_count = instance_locations.length
            if ((parent_count == 1) and (instance_count == 1)):
                return parent_position[0] + instance_locations[0]
            this_count = instance_count * parent_count
            these_positions = Vector3()
            for i in range(parent_count):
                for j in range(instance_count):
                    these_positions[i + parent_count*j] = parent_position[i] + instance_locations[j]
            return these_positions

    def get_instance_angles(self):
        return self.get_instance_count()

    def get_component_angles(self):
        if (self.parent is None):
            return self.axial_rot_to_coord(self.get_instance_angles())
        else:
            parent_angles = self.parent.get_component_angles()
            parent_count = parent_angles.length
            instance_angles = self.axial_rot_to_coord(self.get_instance_angles())
            instance_count = instance_angles.length
            if ((parent_count == 1) and (instance_count == 1)):
                return parent_angles + instance_angles
            this_count = instance_count * parent_count
            these_angles = Vector3()
            for i in range(parent_count):
                for j in range(instance_count):
                    these_angles[i + parent_count*j] = these_angles[i] + these_angles[j]
            return these_angles

    def axial_rot_to_coord(self, angles):
        coords = Vector3()
        for i in range(angles.length):
            coords[i] = Vector3(angles[i], 0, 0)
        return coords

    def to_absolute(self, vec):
        self.check_state()
        these_position = self.get_component_locations()
        instance_count = these_position.length
        to_return = Vector3()
        for coord_idx in range(instance_count):
            to_return[coord_idx] = these_position[coord_idx] + vec
        return to_return

    def to_relative(self, vec, dest):
        if (dest is None):
            raise ValueError("toRelative dest is None")
        self.check_state()
        dest_locs = dest.get_locations()
        to_return = Vector3()
        for coord_idx in range(dest_locs.length):
            to_return[coord_idx] = self.get_locations()[0][coord_idx] + vec - dest_locs[coord_idx]
        return to_return

    def get_mass(self):
        if (self.mass_overridden):
            return self.override_mass
        return self.get_component_mass

    def get_section_mass(self):
        mass_sub_total = self.get_mass()
        if (self.mass_overridden and self.override_subcomponents_mass):
            return mass_sub_total
        for child in self.children:
            mass_sub_total += child.get_section_mass()
        return mass_sub_total

    def get_cg(self):
        self.check_state()
        if (self.cg_overridden):
            return self.get_override_cg().set_weight(self.get_mass())
        if (self.mass_overridden):
            return self.get_component_cg().set_weight(self.get_mass())
        return self.get_component_cg()

    def get_longitudinal_inertia(self):
        self.check_state()
        return self.get_longitudinal_unit_inertia() * self.get_mass()

    def get_rotational_inertia(self):
        self.check_state()
        return self.get_rotational_unit_inertia() * self.get_mass()

    def get_rocket(self):
        self.check_state()
        r = self.get_root()
        if (isinstance(r, Rocket)):
            return r
        else:
            raise ValueError("get_rocket() called with root component")

    def add_child(self, component, track_stage):
        self.check_state()
        self.add_child(component, len(self.children), track_stage)

    def add_child(self, component):
        self.add_child(component, True)

    def add_child(self, component, idx, track_stage):
        self.check_state()
        if (component.parent is not None):
            raise ValueError("already in the tree")
        if (self.get_root() == component):
            raise ValueError("attempting to create a cycle tree")
        if (not self.is_compatible(component)):
            raise ValueError("not compatible with component")
        self.children.insert(idx, component)
        component.parent = self
        if (self.mass_overridden and self.override_subcomponents_mass):
            component.mass_overridden_by = self
        else:
            component.mass_overridden_by = self.mass_overridden_by
        if (self.cg_overridden and self.override_subcomponents_cg):
            component.cg_overridden_by = self
        else:
            component.cg_overridden_by = self.cg_overridden_by
        if (self.cd_overridden and self.override_subcomponents_cg):
            component.cg_overridden_by = self
        else:
            component.cd_overridden_by = self.cd_overridden_by
        for child in component.iterator(False):
            if component.mass_overridden_by is not None:
                child.mass_overridden_by = component.mass_overridden_by
            if component.cg_overridden_by is not None:
                child.cg_overridden_by = component.cg_overridden_by
            if component.cd_overridden_by is not None:
                child.cd_overridden_by = component.cd_overridden_by
        if (track_stage and (isinstance(component, AxialStage))):
            n_stage = component
            self.get_rocket().track_stage(n_stage)
        self.check_component_structure()
        component.check_component_structure()
        self.fire_add_remove_event(component)

    def add_child(self, component, idx):
        self.add_child(component, idx, True)

    def remove_child(self, n, track_stage):
        self.check_state()
        component = self.get_child(n)
        self.remove_child_component(component, track_stage)

    def remove_child(self, n):
        self.remove_child(n, True)

    def remove_child_component(self, component, track_stage):
        self.check_state()
        component.check_component_structure()
        if (self.children.remove(component)):
            component.parent = None
            for child in component:
                if (child.mass_overridden_by == self) or (child.mass_overridden_by == self.mass_overridden_by):
                    child.mass_overridden_by = None
                if (child.cg_overridden_by == self) or (child.cg_overridden_by == self.cg_overridden_by):
                    child.cg_overridden_by = None
                if (child.cd_overridden_by == self) or (child.cd_overridden_by == self.cd_overridden_by):
                    child.cd_overridden_by = None
            if (track_stage):
                if (isinstance(component, AxialStage)):
                    stage = component
                    self.get_rocket().forget_stage(stage)
                for stage in component.get_sub_stages():
                    self.get_rocket().forget_stage(stage)
            self.check_component_structure()
            component.check_component_structure()
            self.fire_component_change_event(component)
            self.update_bounds()
            return True
        return False

    def remove_child_component(self, component):
        return self.remove_child_component(component, True)

    def fire_add_remove_event(self, component):
        iter = component.iterator(True)
        type = ComponentChangeEvent.TREE_CHANGE
        while (iter.has_next()):
            c = iter.next()
            if (c.is_aerodynamic()):
                self.fire_component_change_event(ComponentChangeEvent.AERODYNAMIC_CHANGE)
            if (c.is_massive()):
                self.fire_component_change_event(ComponentChangeEvent.MASS_CHANGE)
        self.fire_component_change_event(type)

    def get_child_count(self):
        self.check_state()
        self.check_component_structure()
        return self.children.size()

    def get_child(self, n):
        self.check_state()
        self.check_component_structure()
        return self.children.get(n)

    def update_children_mass_overridden_by(self):
        overridden_by = None
        if (self.mass_overridden and self.override_subcomponents_mass):
            overridden_by = self
        for child in self.get_all_children():
            child.mass_overridden_by = overridden_by
            if (overridden_by == None):
                if (child.mass_overridden and child.override_subcomponents_mass):
                    overridden_by = child

    def check_component_structure(self):
        if (self.parent is not None):
            if (self in self.parent.children):
                raise ValueError("Parent doesn't include this")
            for child in self.children:
                if (child.parent is not self):
                    raise ValueError("Child doesn't include this")

    def get_children(self):
        self.check_state()
        self.check_component_structure()
        return self.children

    def get_all_children(self):
        self.check_state()
        self.check_component_structure()
        children = []
        for child in self.get_children():
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def get_child_position(self, child):
        self.check_state()
        self.check_component_structure()
        return self.children.index(child)

    def get_parent(self):
        self.check_state()
        return self.parent

    def get_parents(self):
        self.check_state()
        results = []
        curr_comp = self
        while (curr_comp.parent is not None):
            curr_comp = curr_comp.parent
            results.append(curr_comp)
        return results

    def list_contains_parents(self, components, component):
        c = component
        while (c.get_parent() is not None):
            if (c.get_parent() in components):
                return True
            c = c.get_parent()
        return False

    def get_stage(self):
        self.check_state()
        cur_component = self
        while (cur_component is not None):
            if (isinstance(cur_component, AxialStage)):
                return cur_component
            cur_component = cur_component.parent
        raise ValueError("Error")

    def get_sub_stages(self):
        result = []
        it = self.iterator(False)
        while (it.has_next()):
            c = it.next()
            if (isinstance(c, AxialStage)):
                result.append(c)
        return result

    def get_assembly(self):
        pass

    def set_bypass_change_event(self, new_value):
        self.bypass_component_change_event = new_value

    def fire_component_change_event(self, event):
        self.check_state()
        if (self.parent == None) or (self.bypass_component_change_event):
            return
        self.get_root().fire_component_change_event(event)

    def get_root(self):
        self.check_state()
        root = self
        while(root.parent is not None):
            root = root.parent
        return root

    def add_component_change_listener(self, l):
        self.check_state()
        self.get_rocket().add_component_change_listener(l)

    def remove_component_change_listener(self, l):
        if (self.parent is not None):
            self.get_root().remove_component_change_listener(l)

    @abstractmethod
    def add_change_listener(self, listener):
        self.add_component_change_listener(listener)

    @abstractmethod
    def remove_change_listener(self, listener):
        self.remove_component_change_listener(listener)

    def fire_component_change_event(self, e):
        self.check_state()
        if (self.parent is None or self.bypass_component_change_event):
            return
        self.get_root().fire_component_change_event(e)

    def set_bypass_change_event(self, new_val):
        self.bypass_component_change_event = new_val

    def is_bypass_component_change_event(self):
        return self.bypass_component_change_event

    def add_config_listener(self, listener):
        if (self.is_bypass_component_change_event()):
            raise ValueError("")
        if (self.listeners is None):
            return False
        if (not self.listeners.get_config_listeners().is_empty()):
            raise ValueError("")
        if (self.config_listeners.contains(listener) or listener == self):
            return False
        self.config_listeners.append(listener)
        listener.set_bypass_change_event(True)
        return True

    def remove_config_listener(self, listener):
        self.config_listeners.remove(listener)
        self.listeners.set_bypass_change_event(False)

    def clear_config_listeners(self):
        for listener in self.config_listeners:
            listener.set_bypass_change_event(False)
        self.config_listeners.clear()

    def get_config_listeners(self):
        return self.config_listeners

    def check_state(self):
        pass

    def __eq__(self, other):
        if (self == other):
            return True
        if (other is None):
            return False
        if (self.get_class() is not other.get_class()):
            return False
        id_check = other.id
        return self.id == id_check

    def update_bounds(self):
        pass

class ComponentAssembly(RocketComponent):
    def __init__(self, axial_method=AxialMethod.AFTER):
        super().__init__(axial_method)

    def allows_children(self):
        return True

    def get_axial_offset(self):
        return super().get_axial_offset(self.axial_method)

    def get_component_bounds(self):
        return []

    def get_component_cg(self):
        return Vector3()

    def get_component_mass(self):
        return 0.0

    def get_longitudinal_unit_inertia(self):
        return 0.0

    def get_rotational_unit_inertia(self):
        return 0.0

    def is_aerodynamic(self):
        return False

    def is_massive(self):
        return False