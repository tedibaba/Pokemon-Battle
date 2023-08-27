import abc
import math

from data_structures.referential_array import ArrayR
from data_structures.stack_adt import ArrayStack
from data_structures.array_sorted_list import ArraySortedList
from data_structures.sorted_list_adt import ListItem

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

    """Unless otherwise stated, the complexity of each of the methods in the class are O(n) 
    where n is the number of elements in the given formula.
    """

    def __init__(
        self,
        attack_formula: ArrayR[str],
        defense_formula: ArrayR[str],
        speed_formula: ArrayR[str],
        max_hp_formula: ArrayR[str],
    ) -> None:
        self.attack_formula = attack_formula
        self.defense_formula = defense_formula
        self.speed_formula = speed_formula
        self.max_hp_formula = max_hp_formula


    def get_attack(self, level: int):
        """
        Returns the attack of the monster using its complex stats

        :param level: The level of the monster
        """
        return self.calculate(self.attack_formula, level)

    def get_defense(self, level: int):
        """
        Returns the defense of the monster using its complex stats

        :param level: The level of the monster
        """
        return self.calculate(self.defense_formula, level)

    def get_speed(self, level: int):
        """
        Returns the speed of the monster using its complex stats

        :param level: The level of the monster
        """
        return self.calculate(self.speed_formula, level)

    def get_max_hp(self, level: int):
        """
        Returns the max hp of the monster using its complex stats

        :param level: The level of the monster
        """
        return self.calculate(self.max_hp_formula, level)
    
    def calculate(self, formula : ArrayR[str], level: int) -> int:
        """
        Calculates the formula given in reverse polish notation

        :implementation:
            We use a stack for reverse polish notation because this is the most appropriate data structure
            for traversing through the elements of the formula.

        :param formula: An array containing the reverse polish notation for the equation
        :param level: The level of the monster
        :return: An integer representing the final result of calculating the formula
        :complexity: O(n) both best/worst case where n is the number of elements in the formula
        """
        
        stack = ArrayStack[str](len(formula))
        for i in range (len(formula)):
            top = formula[i]
            try:
                if top == "level":
                    stack.push(level)
                elif self.is_float(top):
                    stack.push(float(top))  
                elif top == "sqrt":
                    a = stack.pop()
                    stack.push(math.sqrt(a))
                else:
                    a = stack.pop()
                    b= stack.pop()
                    if top == "middle":
                        c = stack.pop()
                        sorted_list = ArraySortedList[int](3)
                        sorted_list.add(ListItem(a, a))
                        sorted_list.add(ListItem(b, b))
                        sorted_list.add(ListItem(c, c))
                        stack.push(sorted_list[1].value) #the median will be the value in the middle of the sorted list so we can just grab that value and push it onto the stack
                    else:
                        if top == "power":
                            res = math.pow(b,a)
                        elif top == "+":
                            res = a + b
                        elif top == "-":
                            res = b - a
                        elif top == "*":
                            res = a * b
                        elif top == "/":
                            res = b/a
                
                        stack.push(res)
            except (ValueError, UnboundLocalError, Exception):
                raise Exception(f"{top} is either not a valid operator or number")
        
        if len(stack) == 1: #The stack must only have one item left in the stack
            return int(stack.pop()) 
        else:
            raise ValueError("Invalid expression, not enough operators")
        
    def is_float(self, x):
        try:
            float(x)
            return True
        except ValueError:
            return False


def test_complex_stats():
    cs = ComplexStats(
        ArrayR.from_list([
            "5",
            "2",
            "power"
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
    # print(cs.get_speed(5))
    # print(cs.get_defense(1))
    # print(cs.get_max_hp(41))
    print(cs.get_attack(1))

