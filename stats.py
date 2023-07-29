import abc

from data_structures.referential_array import ArrayR
from data_structures.stack_adt import ArrayStack


class Stats(abc.ABC):

    @abc.abstractmethod
    def get_attack(self):
        pass

    @abc.abstractmethod
    def get_defense(self):
        pass

    @abc.abstractmethod
    def get_speed(self):
        pass

    @abc.abstractmethod
    def get_max_hp(self):
        pass


class SimpleStats(Stats):
     

    def __init__(self, attack, defense, speed, max_hp) -> None:
        # TODO: Implement
        pass
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.max_hp = max_hp

    def get_attack(self):
        return self.attack

    def get_defense(self):
        return self.defense

    def get_speed(self):
        return self.speed

    def get_max_hp(self):
        return self.max_hp

class ComplexStats(Stats):

    def __init__(
        self,
        attack_formula: ArrayR[str],
        defense_formula: ArrayR[str],
        speed_formula: ArrayR[str],
        max_hp_formula: ArrayR[str],
    ) -> None:
        self.attack_formula = process_into_stack(attack_formula)
        self.defense_formula = process_into_stack(defense_formula)
        self.speed_formula = process_into_stack(speed_formula)
        self.max_hp_formula = process_into_stack(max_hp_formula)


    def get_attack(self, level: int):
        number_stack = ArrayStack[str](len(self.attack_formula))
        operation_stack = ArrayStack[str](len(self.attack_formula))
        operations = ["+", "-", '*', '/', 'power', "sqrt", "middle"]
        while not self.attack_formula.is_empty():
            top = self.attack_formula.pop()
            if top in operations:
                operation_stack.push(top)
            else:
                operation = operation_stack.pop()
                if operation == "sqrt":
                    
                other_num = self.attack_formula.pop()
                
                


        

    def get_defense(self, level: int):
        raise NotImplementedError

    def get_speed(self, level: int):
        raise NotImplementedError

    def get_max_hp(self, level: int):
        raise NotImplementedError
    
    @classmethod
    def process_into_stack(cls, formula: ArrayR[str]) -> ArrayStack[str]:
        
        formula_stack = ArrayStack[str](len(formula))
        for i in formula:
            formula_stack.push(i)
        return formula_stack
