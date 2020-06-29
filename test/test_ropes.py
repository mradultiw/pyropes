import unittest

from pyropes import Rope

class Test(unittest.TestCase):

    def setUp(self):
        # TODO: targets
        pass

    def test_empty(self):
        rope = Rope()
        self.assertEqual(None, rope.root)
        self.assertEqual(0, rope.size)
        self.assertEqual(0, len(rope))
        self.assertEqual('',str(rope))
        self.assertEqual(rope.size,len(rope))

    def test_list(self):
        self.assertEqual(Rope(), Rope([]))
        self.assertEqual(Rope('abcdefghijklmno'), Rope(['abcdefghijklmno']))
        self.assertEqual(Rope('ab')+Rope('cd'), Rope(['ab', 'cd']))
        self.assertEqual(Rope('a')+Rope('b')+Rope('c'),Rope(['a', 'b', 'c']))
        self.assertEqual(((Rope('a')+Rope('b'))+Rope('cd')).size,
                                         len(Rope(['ab', 'cd'])))

        s = 'These are some words'.split()
        r = (Rope('These')+Rope('are'))+(Rope('some')+Rope('words'))
        self.assertEqual(r, Rope(s))
        self.assertEqual(r.size,len(Rope(s)))

    def test_index_onenode(self):
        s = 'abc'
        r = Rope(s)
        for i in range(-len(s), len(s)):
            self.assertEqual(Rope(s[i]), r[i])
            self.assertEqual(Rope(s[i]).size,len(r[i]))
            self.assertEqual(len(Rope(s[i])),r[i].size)

        for i in range(len(s), 3 * len(s)):
            self.assertRaises(IndexError, r.__getitem__, i)
            self.assertRaises(IndexError, r.__getitem__, -(i + 1))

    def test_slice_onenode(self):
        s = 'abcdefghi'
        r = Rope(s)

        # Implicit start, step
        for i in range(-3 * len(s), 3 * len(s)):
            self.assertEqual(Rope(s[:i]), r[:i])
            self.assertEqual(Rope(s[:i]).size,len(r[:i]))
            self.assertEqual(len(Rope(s[:i])),r[:i].size)

        # Implicit stop, step
        for i in range(-3 * len(s), 3 * len(s)):
            self.assertEqual(Rope(s[i:]), r[i:])
            self.assertEqual(len(Rope(s[i:])), r[i:].size)
            self.assertEqual(Rope(s[i:]).size, len(r[i:]))

        # Explicit slices
        for i in range(-3 * len(s), 3 * len(s)):
            for j in range(-3 * len(s), 3 * len(s)):
                for k in range(-len(s),len(s)):
                    if not k:
                        self.assertRaises(ValueError,r.__getitem__,
                                                  slice(i,j,k))
                        continue
                    self.assertEqual(s[i:j:k], str(r[i:j:k]))
                    self.assertEqual(len(s[i:j:k]), len(r[i:j:k]))
                    self.assertEqual(len(s[i:j:k]), (r[i:j:k]).size)

    def test_index_threenode(self):
        s = 'abcde'
        r = Rope('abc') + Rope('de')

        for i in range(-len(s), len(s)):
            self.assertEqual(Rope(s[i]), r[i])
            self.assertEqual(len(Rope(s[i])), r[i].size)
            self.assertEqual(Rope(s[i]).size, len(r[i]))

        for i in range(len(s), 3 * len(s)):
            self.assertRaises(IndexError, r.__getitem__, i)
            self.assertRaises(IndexError, r.__getitem__, -(i + 1))

    def test_slice_threenode(self):
        s = 'abc' + 'de'
        r = Rope('abc') + Rope('de')

        # TODO: Condense this
        self.assertEqual(Rope('abc') + Rope('de'), r[:])

        for i in range(-3 * len(s), 3 * len(s)):
            self.assertEqual(s[i:], str(r[i:]))

        for j in range(-3 * len(s), 3 * len(s)):
            self.assertEqual(s[:j], str(r[:j]))

        for i in range(-3 * len(s), 3 * len(s)):
            for j in range(-3 * len(s), 3 * len(s)):
                self.assertEqual(s[i:j], str(r[i:j]))

    def test_stride_threenode(self):
        s = 'abcde' + 'fghijkl'
        lis=['abcde', 'fghijkl']
        r = Rope(lis,leafsize=3)

        for i in range(-3 * len(s), 3 * len(s)):
            for k in range(-len(s), len(s) + 1):
                if k == 0:
                    self.assertRaises(ValueError, r.__getitem__,
                                      slice(i,None,k))
                else:
                    a,b=s[i::k], str(r[i::k])
                    self.assertEqual(a,b)
                    a,b=s[:i:k], str(r[:i:k])
                    self.assertEqual(a,b)

        for i in range(-3 * len(s), 3 * len(s)):
            for j in range(-3 * len(s), 3 * len(s)):
                for k in range(-3*len(s), len(s) + 1):
                    if k == 0:
                        self.assertRaises(ValueError, r.__getitem__,
                                          slice(i,j,k))
                    else:
                        a,b=s[i:j:k], str(r[i:j:k])
                        self.assertEqual(a,b)

    def test_word_iteration(self):
        words = ['a', 'b', 'c', 'd', 'e']
        rope = Rope(words)
        for i, w in enumerate(rope):
            self.assertEqual(w, words[i])

    def test_equality(self):
        r = Rope('a') + Rope('b') + Rope('c')
        t = (Rope('a') + Rope('b')) + Rope('c')
        self.assertEqual(r, t)
        self.assertEqual(len(r),t.size)
        self.assertEqual(r.size,len(t))
        self.assertEqual(r.size,t.size)
        self.assertEqual(len(r),len(t))
        
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
