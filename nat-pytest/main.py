import pytest
import sys

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('I am pytest and I will run your tests')
    sys.exit(pytest.main(["./tests/"]))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
