import unittest
import string
# from pyropes.Ropes import dis as visualizer

from pyropes.Ropes import Rope


class Test(unittest.TestCase):

    def setUp(self):
        # TODO: targets
        pass

    def test_empty(self):
        rope = Rope()
        self.assertEqual(None, rope.root)
        self.assertEqual(0, rope.size)
        self.assertEqual(0, len(rope))
        self.assertEqual('', str(rope))
        self.assertEqual(rope.size, len(rope))

    def test_list(self):
        self.assertEqual(Rope(), Rope([]))
        self.assertEqual(Rope('abcdefghijklmno'), Rope(['abcdefghijklmno']))
        self.assertEqual(Rope('ab') + Rope('cd'), Rope(['ab', 'cd']))
        self.assertEqual(Rope('a') + Rope('b') + Rope('c'), Rope(['a', 'b', 'c']))
        self.assertEqual(((Rope('a') + Rope('b')) + Rope('cd')).size,
                         len(Rope(['ab', 'cd'])))

        s = 'These are some words'.split()
        r = (Rope('These') + Rope('are')) + (Rope('some') + Rope('words'))
        self.assertEqual(r, Rope(s))
        self.assertEqual(r.size, len(Rope(s)))

    def test_append(self):
        s = ['this_is a test', 'string', 'used for testing',
             'concatnation of ropes', 'of different leafsize']
        rope_array = []
        for sub in s:
            rope_array.append(Rope(sub, 4))

        for string, rope in zip(s, rope_array):
            self.assertEqual(string, str(rope))
            self.assertEqual(len(string), len(rope))
            self.assertEqual(len(string), rope.size)

        s = ''.join(s)

        rope = Rope()
        for sub in rope_array:
            rope.append(sub)
        self.assertEqual(s, str(rope))
        self.assertEqual(len(s), len(rope))
        self.assertEqual(len(s), rope.size)

    def test_add(self):
        s = ['this_is a test ', 'string', 'used for testing',
             'concatnation of ropes', 'of different leafsize']
        rope_array = []
        for sub in s:
            rope_array.append(Rope(sub, 4))

        for sub, rope in zip(s, rope_array):
            self.assertEqual(sub, str(rope))
            self.assertEqual(len(sub), len(rope))
            self.assertEqual(len(sub), rope.size)

        s = ''.join(s)

        rope = Rope()
        for sub in rope_array:
            rope += sub
        self.assertEqual(s, str(rope))
        self.assertEqual(len(s), len(rope))
        self.assertEqual(len(s), rope.size)

    def test_mul(self):
        s = "test string is this"
        r = Rope(s)
        for i in range(len(s) >> 1):
            self.assertEqual(s * i, str(r * i))

    def test_index_onenode(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_lowercase
            r = Rope(s, 4)
        for i in range(-len(s), len(s)):
            self.assertEqual(Rope(s[i]), r[i])
            self.assertEqual(Rope(s[i]).size, len(r[i]))
            self.assertEqual(len(Rope(s[i])), r[i].size)

        for i in range(len(s), 3 * len(s)):
            self.assertRaises(IndexError, r.__getitem__, i)
            self.assertRaises(IndexError, r.__getitem__, -(i + 1))

    def test_slice_onenode(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_lowercase
            r = Rope(s, 5)

        # Implicit start, step
        for i in range(-3 * len(s), 3 * len(s)):
            self.assertEqual(Rope(s[:i]), r[:i])
            self.assertEqual(Rope(s[:i]).size, len(r[:i]))
            self.assertEqual(len(Rope(s[:i])), r[:i].size)

        # Implicit stop, step
        for i in range(-3 * len(s), 3 * len(s)):
            self.assertEqual(Rope(s[i:]), r[i:])
            self.assertEqual(len(Rope(s[i:])), r[i:].size)
            self.assertEqual(Rope(s[i:]).size, len(r[i:]))

        # Explicit slices
        for i in range(-3 * len(s), 3 * len(s)):
            for j in range(-3 * len(s), 3 * len(s)):
                for k in range(-len(s), len(s)):
                    if not k:
                        self.assertRaises(ValueError, r.__getitem__,
                                          slice(i, j, k))
                        continue
                    self.assertEqual(s[i:j:k], str(r[i:j:k]))
                    self.assertEqual(len(s[i:j:k]), len(r[i:j:k]))
                    self.assertEqual(len(s[i:j:k]), (r[i:j:k]).size)

    def test_index_threenode(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_letters
            r = Rope(string.ascii_lowercase) + Rope(string.ascii_uppercase)

        for i in range(-len(s), len(s)):
            self.assertEqual(Rope(s[i]), r[i])
            self.assertEqual(len(Rope(s[i])), r[i].size)
            self.assertEqual(Rope(s[i]).size, len(r[i]))

        for i in range(len(s), 3 * len(s)):
            self.assertRaises(IndexError, r.__getitem__, i)
            self.assertRaises(IndexError, r.__getitem__, -(i + 1))

    def test_slice_threenode(self, s=None, r=None):
        if s is None or r is None:
            s = 'abc' + 'de'
            r = Rope('abc') + Rope('de')

        for i in range(-3 * len(s), 3 * len(s)):
            self.assertEqual(s[i:], str(r[i:]))

        for j in range(-3 * len(s), 3 * len(s)):
            self.assertEqual(s[:j], str(r[:j]))

        for i in range(-3 * len(s), 3 * len(s)):
            for j in range(-3 * len(s), 3 * len(s)):
                self.assertEqual(s[i:j], str(r[i:j]))

    def test_stride_threenode(self, s=None, r=None):
        if s is None or r is None:
            s = 'abcde' + 'fghijkl'
            lis = ['abcde', 'fghijkl']
            r = Rope(lis, leafsize=5)

        for i in range(-3 * len(s), 3 * len(s)):
            for k in range(-len(s), len(s) + 1):
                if k == 0:
                    self.assertRaises(ValueError, r.__getitem__,
                                      slice(i, None, k))
                else:
                    self.assertEqual(s[i::k], str(r[i::k]))
                    self.assertEqual(s[:i:k], str(r[:i:k]))

        for i in range(-3 * len(s), 3 * len(s)):
            for j in range(-3 * len(s), 3 * len(s)):
                for k in range(-3 * len(s), len(s) + 1):
                    if k == 0:
                        self.assertRaises(ValueError, r.__getitem__,
                                          slice(i, j, k))
                    else:
                        a, b = s[i:j:k], str(r[i:j:k])
                        self.assertEqual(a, b)

    def test_word_iteration(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_letters
            r = Rope(s)
        for i, w in enumerate(r):
            self.assertEqual(w, s[i])

    def test_find(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_letters
            r = Rope(s)
        for i in range(-len(s), len(s)):
            self.assertEqual(str(r.find(i)), s[i])

    def test_delete(self, s=None, r=None):
        if s is None or r is None:
            s = list(string.ascii_letters)
            r = Rope(s, 3)
        for i in range(len(s)):
            for j in range(len(s)):
                del_rope = r.delete(i, j)
                del_str = ''.join(s[i:j + 1])
                del s[i:j + 1]
                self.assertEqual(del_str, str(del_rope))
                self.assertEqual(''.join(s), str(r))
                r.insert(i, del_rope)
                s[i:i] = del_str

    def test_length(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_letters
            r = Rope(s, 4)
        for i in range(len(s)):
            for j in range(len(s)):
                temp = r[i:j]
                self.assertEqual(len(temp), len(s[i:j]))
                self.assertEqual(len(temp), temp.size)

    def test_reverse(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_letters
            r = Rope(s, 4)
        for i in range(len(s)):
            for j in range(i, len(s)):
                temp = r[i:j]
                temp.reverse()
                self.assertEqual(str(temp), s[i:j][::-1])

    def test_split(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_letters
            r = Rope(s, 3)
        for i in range(-len(s), len(s) + 1):
            left, right = r.split(i)
            self.assertEqual(str(left), s[:i])
            self.assertEqual(str(right), s[i:])
            r.append(right)

    def test_split_merge(self, s=None, r=None):
        if s is None or r is None:
            s = string.ascii_letters
            r = Rope(s, 3)
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                m = max(0, i - 5)
                r.split_merge(i, j, m)
                cut = s[i:j + 1]
                s = s[:i] + s[j + 1:]
                s = s[:m] + cut + s[m:]
                self.assertEqual(s, str(r))
                self.assertEqual(len(s), len(r))

    def test_equality(self):
        r = Rope('a') + Rope('b') + Rope('c')
        t = (Rope('a') + Rope('b')) + Rope('c')
        self.assertEqual(r, t)
        self.assertEqual(len(r), t.size)
        self.assertEqual(r.size, len(t))
        self.assertEqual(r.size, t.size)
        self.assertEqual(len(r), len(t))

    def test_isaplha(self):
        self.assertTrue(Rope("thisisALPhaBeT").isalpha())
        self.assertFalse(Rope("this1sALPha2eT").isalpha())
        self.assertFalse(Rope("this1sALP!@a2eT").isalpha())

    def test_isalnum(self):
        self.assertTrue(Rope("thisisALPhaBeT").isalnum())
        self.assertTrue(Rope("this1sALPha2eT").isalnum())
        self.assertFalse(Rope("this1sALP!@a2eT").isalnum())

    def test_islower(self):
        self.assertTrue(Rope("thisishasdjfnjksae").islower())
        self.assertFalse(Rope("this1sALPha2eT").islower())
        self.assertFalse(Rope("this1sALP!@a2eT").islower())

    def test_isupper(self):
        self.assertFalse(Rope("thisisALPhaBeT").isupper())
        self.assertTrue(Rope("THISISCAPITALCASE").isupper())
        self.assertFalse(Rope("this1sALP!@a2eT").isupper())

    def test_isdigit(self):
        self.assertFalse(Rope("thisisALPhaBeT").isdigit())
        self.assertTrue(Rope("2327482364520374").isdigit())
        self.assertFalse(Rope("this1sALP!@a2eT").isdigit())

    def test_universal(self):
        """
        testing all features on a single rope object at once
        Note: This is a time consuming testcase(6-8 min. depending on system).
        It uses bruteforce string operations and compares them with equivalent
        Rope operations. It's an exahustive testcase which checks all possible
        valid combinations of rope operations. You can track progress of test
        at file stored in "current_directory/test_universal.txt" file.

        Also note that this testcase tests only complex rope methods where there
        can be chances of missing corner cases.
        """
        s = string.ascii_lowercase
        r = Rope()
        for c in s:
            r.append(c)
        s += string.ascii_uppercase
        for c in string.ascii_uppercase:
            r += c

        output_file = open('test_universal.txt', 'w')

        # test_equality
        print("testing... equality", flush=True, file=output_file)
        self.assertEqual(s, str(r))
        self.assertEqual(len(s), len(r))
        self.assertEqual(len(r), r.size)

        print("testing... find", flush=True, file=output_file)
        self.test_find(s, r)

        print("testing... delete", flush=True, file=output_file)
        self.test_delete(list(s), r)
        # passed 'list' in delete because str don't support deletion

        print("testing... index_onenode", flush=True, file=output_file)
        self.test_index_onenode(s, r)

        print("testing... index_threenode", flush=True, file=output_file)
        self.test_index_threenode(s, r)

        print("testing... length", flush=True, file=output_file)
        self.test_length(s, r)

        print("testing... word_iteration", flush=True, file=output_file)
        self.test_word_iteration(s, r)

        print("testing... stride_threenode", flush=True, file=output_file)
        self.test_stride_threenode(s, r)

        print("testing... slice_threenode", flush=True, file=output_file)
        self.test_slice_threenode(s, r)

        print("testing... slice_onenode", flush=True, file=output_file)
        self.test_slice_onenode(s, r)

        print("testing... reverse", flush=True, file=output_file)
        self.test_reverse(s, r)

        output_file.close()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
