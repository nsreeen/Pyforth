
import pytest
import pyforth as forth

class TestStacks:
    def test_param_stack_push_and_pop(self):
        forth.push(1)
        forth.push(2)
        forth.push(3)
        assert forth.pop() == 3
        assert forth.pop() == 2
        assert forth.pop() == 1

    def test_return_stack_push_and_pop(self):
        forth.push_RS(1)
        forth.push_RS(2)
        forth.push_RS(3)
        assert forth.pop_RS() == 3
        assert forth.pop_RS() == 2
        assert forth.pop_RS() == 1

"""class TestDictionary:
    def test_add_tracking_variables_start_of_dictionary(self):
        assert forth.HERE == len(forth.dictionary) - 1 #HERE
        assert forth.PC == -1 #PC

    def test_linked_list(self):
        current = forth.LATEST
        addresses = []
        while current != -1:
            current = forth.dictionary[current]
            addresses.append(current)
        assert min(addresses) == -1
        assert max(addresses) < len(forth.dictionary)
        print(addresses, '\n', sorted(addresses, reverse=True))
        assert addresses == sorted(addresses, reverse=True)"""


class TestThreading:
    def test_define_word(self):
        forth.input_stream = ": TWICE DUP + DUP ; 5 TWICE "
        forth.quit()
        assert forth.pop() == 10
        assert forth.pop() == 10

class TestBranching:
    def test_if_else(self):
        forth.input_stream = ": TEST DUP 7 < IF DUP 6 DUP ELSE 100 * THEN ; 5 TEST"
        forth.quit()
        assert forth.pop() == 6
        assert forth.pop() == 6
        assert forth.pop() == 5
        assert forth.pop() == 5

"""    def test_define_multiple_words(self):
        forth.input_stream = ": DOUBLE DUP + ; : TWICE DOUBLE DUP ; : SQUARED DUP * ; : CUBED DUP SQUARED * ; 2 CUBED 3 SQUARED 5 TWICE .S "
        forth.quit() #8 9 10 10
        assert forth.pop() == 10
        assert forth.pop() == 10
        assert forth.pop() == 9
        assert forth.pop() == 8


    def test_do_loop(self):
        forth.input_stream = ": TEST 5 1 DO I LOOP ; TEST"
        forth.stack = []
        forth.quit()
        assert forth.stack == [1, 2, 3, 4]

    def test_do_plus_loop(self):
        forth.input_stream = ": TEST 30 2 DO 2 I + DUP +LOOP ; TEST"
        forth.stack = []
        forth.quit()
        assert forth.stack == [4, 8, 16]

    def test_until(self):
        forth.input_stream = ": TEST 5 BEGIN DUP 1 + DUP 20 = UNTIL ; TEST"
        forth.stack = []
        forth.quit()
        assert forth.stack == [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]





"""
