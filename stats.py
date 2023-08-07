import abc
import math

from data_structures.referential_array import ArrayR
from data_structures.stack_adt import ArrayStack
from data_structures.array_sorted_list import ArraySortedListWithoutKeys
from data_structures.queue_adt import CircularQueue

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
        self.attack_formula = self.process_into_stack(attack_formula)
        self.defense_formula = self.process_into_stack(defense_formula)
        self.speed_formula = self.process_into_stack(speed_formula)
        self.max_hp_formula = self.process_into_stack(max_hp_formula)


    def get_attack(self, level: int):
        return self.calculate(self.attack_formula, level)
                 

    def get_defense(self, level: int):
        return self.calculate(self.defense_formula, level)

    def get_speed(self, level: int):
        return self.calculate(self.speed_formula, level)

    def get_max_hp(self, level: int):
        return self.calculate(self.max_hp_formula, level)
    
    def calculate(self, formula : ArrayR[str], level: int):
        stack = ArrayStack[str](len(formula))
        operations = ["+", "-", '*', '/', 'power', "sqrt", "middle"] #Cannot use Array like this 
        while not formula.is_empty():
            top = formula.serve()
            if top not in operations:
                if top == "level":
                    stack.push(level)
                else:
                    stack.push(top) 
            else:
                if top == "sqrt":
                    a = stack.pop()
                    stack.push(math.sqrt(float(a)))
                else:
                    a = stack.pop()
                    b= stack.pop()
                    if top == "middle":
                        c = stack.pop()
                        sorted_list = ArraySortedListWithoutKeys[int](3)
                        sorted_list.add(float(a))
                        sorted_list.add(float(b))
                        sorted_list.add(float(c))
                        stack.push(str(sorted_list[1]))
                    else:
                        if top == "power":
                            top = "**" 
                        expr = f"float({b}) {top} float({a})"
                        stack.push(str(eval(expr)))
        return int(float((stack.pop())))

    @classmethod
    def process_into_stack(cls, formula: ArrayR[str]) -> ArrayStack[str]:
        
        formula_stack = CircularQueue[str](len(formula))
        for i in formula:
            formula_stack.append(i)
        return formula_stack

def test_complex_stats():
    cs = ComplexStats(
        ArrayR.from_list([
            "5",
            "6",
            "+"
        ]),
        ArrayR.from_list([
            "9",
            "2",
            "8",
            "middle"
        ]),
        ArrayR.from_list([
            "level",
            "3",
            "power",
            "1",
            "2",
            "3",
            "middle",
            "*"
        ]),
        ArrayR.from_list([
            "level",
            "5",
            "-",
            "sqrt",
            "1",
            "10",
            "middle",
        ]),
    )
    cs.get_speed(5)

test_complex_stats()