from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass

    def describe(self):
        # Regular (non-abstract) method — subclasses inherit this as-is
        return f"This shape has area {self.area()} and perimeter {self.perimeter()}"


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


rect = Rectangle(4, 5)
print(rect.describe())  # This shape has area 20 and perimeter 18

# this is in main branch