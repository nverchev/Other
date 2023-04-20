# Allows a temporary change using the with statement
class UsuallyFalse:
    _value = False

    def __bool__(self):
        return self._value

    def __enter__(self):
        self._value = True

    def __exit__(self, *_):
        self._value = False


# Example use case
class HonestPerson:
    def __init__(self):
        self.lying = UsuallyFalse()
        self.age = 32

    @property
    def age(self):
        return self._age - 5 if self.lying else self._age

    @age.setter
    def age(self, value):
        self._age = value


me = HonestPerson()
print(f"Are you {me.age}?")
with me.lying:
    print(f"I am {me.age}. I swear, I am {me.age}.")
print(f"Just kidding, I am {me.age}.")

"""
Why using it instead of passing a flag parameter to the methods?
1) Some methods, like properties, do not accept flags
2) Highlight the change
3) Reuse the attribute instead of creating a new variable
4) Applies to all the methods in the context without repeating the flag
"""
