
import pytest
import pyforth as forth

class TestStacks:
    def test_param_stack_push_and_pop(self):
        forth.PUSH(1)
        forth.PUSH(2)
        assert forth.POP() == 2
        assert forth.POP() == 1

    def test_return_stack_push_and_pop(self):
        forth.RPUSH(1)
        forth.RPUSH(2)
        assert forth.RPOP() == 2
        assert forth.RPOP() == 1

class TestStackManipulations:
    def setup(self):
        forth.stack = []
        forth.PUSH(1)
        forth.PUSH(2)
        forth.PUSH(3)

    def test_ROT(self):
        self.setup()
        forth.ROT()
        assert forth.POP() == 1
        assert forth.POP() == 3
        assert forth.POP() == 2

    def test_DROP(self):
        self.setup()
        forth.DROP()
        assert forth.POP() == 2
        assert forth.stack == [1]

    def test_NIP(self):
        self.setup()
        forth.NIP()
        assert forth.POP() == 3
        assert forth.POP() == 1

    def test_TUCK(self):
        self.setup()
        forth.TUCK()
        assert forth.POP() == 3
        assert forth.POP() == 2
        assert forth.POP() == 3
        assert forth.POP() == 1

    def test_TWODUP(self):
        self.setup()
        forth.TWODUP()
        assert forth.POP() == 3
        assert forth.POP() == 2
        assert forth.POP() == 3
        assert forth.POP() == 2

    def test_MOD(self):
        self.setup()
        forth.MOD()
        assert forth.POP() == 2
        assert forth.stack == [1]

class TestReturnStackManipulations:
    def setup(self):
        forth.stack = []
        forth.Rstack = []

    def test_toR(self):
        self.setup()
        forth.PUSH(1)
        forth.toR()
        assert forth.stack == []
        assert forth.Rstack == [1]

    def test_fromR(self):
        self.setup()
        forth.RPUSH(1)
        forth.fromR()
        assert forth.stack == [1]
        assert forth.Rstack == []

    def test_RCLEAR(self):
        self.setup()
        forth.RPUSH(1)
        forth.RPUSH(2)
        forth.RPUSH(3)
        forth.RCLEAR()
        assert forth.stack == []
        assert forth.Rstack == []

    def test_Rtop(self):
        self.setup()
        forth.RPUSH(8)
        forth.Rtop()
        assert forth.stack == [8]
        assert forth.Rstack == [8]

class TestThreading:
    def test_define_word(self):
        forth.input_stream = ": TWICE DUP + DUP ; 5 TWICE "
        forth.QUIT()
        assert forth.POP() == 10
        assert forth.POP() == 10

    def test_do_loop(self):
        forth.input_stream = ": TEST 5 1 DO I LOOP ; TEST"
        forth.stack = []
        forth.QUIT()
        assert forth.stack == [1, 2, 3, 4]

class TestBranching:
    def test_if_else(self):
        forth.input_stream = ": TEST DUP 7 < IF DUP 6 DUP ELSE 100 * THEN ; 5 TEST"
        forth.QUIT()
        assert forth.POP() == 6
        assert forth.POP() == 6
        assert forth.POP() == 5
        assert forth.POP() == 5

    def test_define_multiple_words(self):
        forth.input_stream = ": DOUBLE DUP + ; : TWICE DOUBLE DUP ; : SQUARED DUP * ; : CUBED DUP SQUARED * ; 2 CUBED 3 SQUARED 5 TWICE .S "
        forth.QUIT() #8 9 10 10
        assert forth.POP() == 10
        assert forth.POP() == 10
        assert forth.POP() == 9
        assert forth.POP() == 8

"""

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
