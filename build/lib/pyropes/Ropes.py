import collections.abc
import warnings


class _RopeNode(object):
    def __init__(self, weight, value=None):
        self.lc = None  # Left Child
        self.rc = None  # Right Child
        self.weight = weight  # String size on lc
        self.val = value  # 'sub-string' if leaf node else None
        self.height = 0  # for height balancing

    def __len__(self):
        return self.weight


class Rope(object):
    """
    - Value of all internal nodes will be None.
    - Value of all leaf nodes will be some sub-string of
            length not more than leafsize.
    - smaller leafsize will cause serious performance issues
        Use large leaf size like 8, 16, 24, 32.
    """

    def __init__(self, raw=None, leafsize=8):
        self.root = None
        self.__size = 0
        assert leafsize > 0, "leafsize must be positive integer"
        self.__leafsize = leafsize
        if raw is None:
            return
        if isinstance(raw, str):
            self.raw = raw
            self.root = self.__create_rope(0, len(raw) - 1)
            return
        if isinstance(raw, collections.abc.Collection):
            _append_ = self.__append
            _size_ = self.__size
            _root_ = self.root
            for sub in raw:
                rope = Rope(sub, leafsize)
                _size_ += rope.size
                _root_ = _append_(_root_, rope.root, update_thread=True)
            self.__size = _size_
            self.root = _root_
            return
        raise TypeError("Only string or string-container allowed")

    @property
    def size(self):
        return self.__size

    @size.getter
    def size(self):
        return self.__size

    @property
    def leafsize(self):
        return self.__leafsize

    @leafsize.getter
    def leafsize(self):
        return self.__leafsize

    @leafsize.setter
    def leafsize(self, value):
        if self.__leafsize == value:
            return
        if value <= 0 or not isinstance(value, int):
            raise ValueError("leafsize must be positive Integer")
        if value < 4:
            warnings.warn("Smaller leafsizes will cause serious performance"
                          + " issues. Use big integer like, 8, 16, 32, 64.\n")
        self.__leafsize = value
        self.root = self.__refresh(self.root)

    def __create_rope(self, lo, hi):
        """create rope from a string raw[lo:hi+1]"""
        if lo + self.leafsize > hi:
            self.__size += hi - lo + 1
            return _RopeNode(hi - lo + 1, self.raw[lo:hi + 1])
        mid = (lo + hi) // 2
        root = _RopeNode(mid - lo + 1)
        root.lc = self.__create_rope(lo, mid)
        root.rc = self.__create_rope(mid + 1, hi)
        root = self.__update_thread(root)
        return self.__balance(root)

    def __update_thread(self, root):
        if not root or root.val is not None:
            return root
        left_most, right_most = root.rc, root.lc
        while left_most and left_most.val is None:
            left_most = left_most.lc
        while right_most and right_most.val is None:
            right_most = right_most.rc

        if right_most:
            right_most.rc = left_most
        if left_most:
            left_most.lc = right_most
        return root

    def __find(self, root, index):
        """
        utility for find() function. Returns a
        rope with single character at self.root[i]
        """
        if index < root.weight:
            if root and root.val is None:
                return self.__find(root.lc, index)
            return Rope(root.val[index], self.leafsize)
        index -= root.weight
        return self.__find(root.rc, index)

    def __append(self, left_root, right_root, *, update_thread=False, root=None):
        """
        right_root and left_root are 'roots' of two
        Ropes to be merged.

                          new_root
                         /        \\
                left_root      right_root

         if any of the right_root or left_root is None,
         return the other else return new_root

         Counter of this is __append_left. Although
         working of both can be merged to single
         __append function but they are kept as it is
         to reduce complexity of code implementation
        """
        if right_root and left_root:
            count_left = self.__len__(left_root)
            if right_root.val is not None:
                # right_root must be a leaf
                count_right = self.__len__(right_root)
                total = count_left + count_right
                if total <= self.leafsize:
                    # left_root also must have been a LEAF.
                    # Shrink to single NODE since combined
                    # length is still less/equal to LEAFSIZE
                    left_thread = left_root.lc
                    right_root.val = left_root.val + right_root.val
                    right_root.weight = len(right_root.val)
                    right_root.lc = left_thread
                    if left_thread:
                        left_thread.rc = right_root
                    del left_root
                    return right_root
            if root is None:
                root = _RopeNode(count_left)
            else:
                root.weight = count_left
                root.val = None
            root.lc, root.rc = left_root, right_root
            if update_thread:
                root = self.__update_thread(root)
            return self.__balance(root)
        return left_root or right_root

    def __balance(self, root):
        """
        Uses AVLTree concept for balancing Ropes.
        Calling it will balance 'root' and decendents.
        """
        if root and root.val is None:
            lc, rc = root.lc, root.rc
            if self.height(lc) > self.height(rc) + 1:
                mid = root.lc
                if self.height(mid.lc) > self.height(mid.rc):
                    root = self.__ll_balance(root)
                else:
                    root = self.__lr_balance(root)
                lc, rc = root.lc, root.rc
            elif self.height(rc) > self.height(lc) + 1:
                mid = root.rc
                if self.height(mid.lc) > self.height(mid.rc):
                    root = self.__rl_balance(root)
                else:
                    root = self.__rr_balance(root)
                lc, rc = root.lc, root.rc
            root.height = 1 + max(self.height(lc), self.height(rc))
        return root

    def __ll_balance(self, root):
        parent, left = root, root.lc
        parent = self.__append(left.rc, parent.rc, root=parent)  # parent.lc=left.rc
        parent = self.__balance(parent)
        left = self.__append(left.lc, parent, root=left)  # left.rc=parent
        return self.__balance(left)

    def __lr_balance(self, root):
        parent, left = root, root.lc
        mid = left.rc
        left = self.__append(left.lc, mid.lc, root=left)  # left.rc=mid.lc
        left = self.__balance(left)
        parent = self.__append(mid.rc, parent.rc, root=parent)  # parent.lc=mid.rc
        parent = self.__balance(parent)
        mid = self.__append(left, parent, root=mid)
        return self.__balance(mid)

    def __rr_balance(self, root):
        parent, right = root, root.rc
        parent = self.__append(parent.lc, right.lc, root=parent)  # parent.rc=right.lc
        parent = self.__balance(parent)
        right = self.__append(parent, right.rc, root=right)  # right.lc=parent
        return self.__balance(right)

    def __rl_balance(self, root):
        parent, right = root, root.rc
        mid = right.lc
        right = self.__append(mid.rc, right.rc, root=right)  # right.lc=mid.rc
        right = self.__balance(right)
        parent = self.__append(parent.lc, mid.lc, root=parent)  # parent.rc=mid.lc
        parent = self.__balance(parent)
        mid = self.__append(parent, right, root=mid)
        return self.__balance(mid)

    def __splitleaf(self, root, key):
        """
        root is leafnode, with value 'STRING'
                STRING
              /        \\
            None       None

        modifies to: (key-dependent)
                STRING
              /        \\
            STRI        NG

        return refrences to (STRI, NG)
        """
        if root is None:
            return None, None
        s = root.val
        left_thread, right_thread = root.lc, root.rc
        leftleaf = _RopeNode(key, s[:key]) if key else None
        rightleaf = _RopeNode(root.weight - key, s[key:]) if \
            root.weight - key else None

        # modifying threads of left part
        if left_thread is not None:
            if leftleaf is None:
                left_thread.rc = None
            else:
                left_thread.rc = leftleaf
                leftleaf.lc = left_thread

        # modifying threads of right part
        if right_thread is not None:
            if rightleaf is None:
                right_thread.lc = None
            else:
                right_thread.lc = rightleaf
                rightleaf.rc = right_thread
        del root
        return leftleaf, rightleaf

    def __splitrope_util(self, root, key):
        """
        Utility for __splitrope() function.
        if a 'node' with weight==key encountered:
            return (node.lc, node.rc)
        if key overlaps on a leafnode:
            return spliteLeaf(node,key)
        """
        if root is None:
            return None, None
        if root.weight == key:
            if root.val is None:  # Node is not leaf
                # de-link threads of left and right parts
                left, right = root.lc, root.rc
                while left and left.val is None:
                    left = left.rc
                if left.rc:
                    left.rc.lc = None
                left.rc = None
                while right and right.val is None:
                    right = right.lc
                if right.lc:
                    right.lc.rc = None
                right.lc = None
                return root.lc, root.rc
            if root.rc:  # leaf have right thread
                root.rc.lc = None  # Remove left thread of right node
            root.rc = None  # Remove thread
            return root, None
        if root.weight > key:  # look in left child
            if root.val is not None:
                left, right = self.__splitleaf(root, key)
                return left, right
            left, right = self.__splitrope_util(root.lc, key)
            right = self.__append(right, root.rc)
            return left, right
        key -= root.weight  # look in right child
        left, right = self.__splitrope_util(root.rc, key)
        left = self.__append(root.lc, left)
        return left, right

    def __splitrope(self, root, key):
        """
        Split Rope in two parts at valid position 'key',
        'key' will be included in right part
        """
        length = self.__len__()
        if 0 <= key <= length:
            return self.__splitrope_util(root, key)
        if -1 * length <= key < 0:
            key = length + key
            return self.__splitrope_util(root, key)
        raise IndexError("Key out of range")

    def __delete(self, lo, hi):
        """
        Utility: remove Rope from index lo-hi (both inclusive)
        return the root node of extracted part
        """
        lo, hi = max(0, lo), min(hi, self.size - 1)
        if lo > hi:
            return Rope()
        left, right = self.__splitrope(self.root, lo)
        mid, right = self.__splitrope(right, hi - lo + 1)
        self.root = self.__append(left, right, update_thread=True)
        if self.root:
            self.__size = self.root.weight + self.__len__(self.root.rc)
        else:
            self.__size = 0
        return mid  # self.__update_thread(mid)

    def __copy_util(self, root):
        """
        Utility: Do postorder traversal and create
        a copy of whole tree rooted at 'root'.
        Returns the ROOT of new tree created.
        This new one is NOT a Rope object yet.
        """
        if root:
            new_node = _RopeNode(root.weight, root.val)
            new_node.height = root.height
            if root.val is not None:
                return new_node
            new_node.lc = self.__copy_util(root.lc)
            new_node.rc = self.__copy_util(root.rc)
            return self.__update_thread(new_node)
        return root

    def __reverse(self, root):
        """Utility for reverse"""
        if root:
            if root.val is None:
                self.__reverse(root.lc)
                self.__reverse(root.rc)
                root.weight = root.rc.weight if root.rc else 0
            else:
                root.val = root.val[::-1]
            root.lc, root.rc = root.rc, root.lc

    def __change_case(self, root, function):
        while root and root.val is None:
            root = root.lc
        while root:
            root.val = function(root.val)
            root = root.rc

    def __check_type(self, root, function):
        while root and root.val is None:
            root = root.lc
        while root and root.val is not None and function(root.val):
            root = root.rc
        return root is None

    def __modify_key(self, root, key, val):
        """
        utility: update value at index 'key' to 'val'
        """
        if key < root.weight:
            if root.val is None:
                return self.__modify_key(root.lc, key, val)
            s = root.val
            new_s = s[:key] + val + s[key + 1:]
            root.val = new_s
            return
        key -= root.weight
        return self.__modify_key(root.rc, key, val)

    def __refresh(self, root):
        """Utility for refresh"""
        if root:
            if root.val is None:
                root.lc = self.__refresh(root.lc)
                root.rc = self.__refresh(root.rc)
                root = self.__append(root.lc, root.rc, root=root)
            else:
                if root.weight > self.leafsize:
                    left_thread, right_thread = root.lc, root.rc
                    root = Rope(root.val, self.leafsize).root
                    left, right = root, root
                    while left and left.val is None:
                        left = left.lc
                    left.lc = left_thread
                    while right and right.val is None:
                        right = right.rc
                    right.rc = right_thread
                    if left_thread:
                        left_thread.rc = left
                    if right_thread:
                        right_thread.lc = right
                    return root
        return root

    def __inorder(self, root, lo=0, hi=None):
        """return inroder traversal generator of rope from str[lo:hi+1]"""

        def get_leaf(node):
            nonlocal lo
            if node is None or node.val is not None:
                return node
            if node.weight > lo:
                return get_leaf(node.lc)
            lo -= node.weight
            return get_leaf(node.rc)

        if hi is None:
            hi = self.size - 1
        total = hi - lo + 1
        root = get_leaf(root)
        if not root or lo > hi:
            return
        count = 0
        for val in root.val[lo:]:
            yield val
            count += 1
            if count >= total:
                return
        root = root.rc
        while root and count < total and root.val is not None:
            for val in root.val:
                yield val
                count += 1
                if count >= total:
                    return
            root = root.rc

    def split(self, index):
        """
        split Rope into two parts at 'index' and return
        'left' and 'right' Ropes.(index lies in right)
        Note that 'self' will Now points to 'left'
        rope
        """
        original_size = self.size
        self.root, right = self.__splitrope(self.root, index)
        self.__size = len(self)
        right_rope = Rope()
        right_rope.root = right
        right_rope._Rope__size = original_size - self.size
        return self, right_rope

    def find(self, index):
        """
        Return value of rope at index 'i'. Returned
        value is also a Rope object
        """
        length = self.__len__()
        if 0 <= index < length:
            pass
        elif -1 * length <= index < 0:
            index = length + index
        else:
            raise IndexError("Index out of range")
        return self.__find(self.root, index)

    def append(self, other_rope, inplace=True):
        """
                     new_root
                    /        \\
              self.root      other_rope

        if inplace is True:
            self.root=new_root
            return self
        else:
            CREATES A COPY of above rope
            return new Rope Object
        """
        if not isinstance(other_rope, Rope):
            other_rope = Rope(other_rope, self.leafsize)
        else:
            other_rope.leafsize = self.leafsize
        new_root = self.__append(self.root, other_rope.root, update_thread=True)
        if inplace:
            self.root = new_root
            self.__size += other_rope._Rope__size
            return self
        new_root = self.__copy_util(new_root)
        new_rope = Rope(leafsize=self.leafsize)
        new_rope.root = new_root
        new_rope._Rope__size = self.__size + other_rope._Rope__size
        return new_rope

    def height(self, node):
        """
        return the level of a node. Root is assumed
        at top level while leaves are at level 0
        """
        return node.height if node else 0

    def delete(self, lo, hi=None):
        """
        Delete Rope Part from lo-hi (both inclusive)
        using utility __delete(). Returns the extracted
        part as NEW ROPE
        """
        if hi is None:
            hi = lo
        lo, hi = max(0, lo), min(hi, self.size - 1)
        if lo > hi:
            return Rope()
        mid = self.__delete(lo, hi)
        extracted_rope = Rope(leafsize=self.leafsize)
        extracted_rope.root = mid
        extracted_rope._Rope__size = hi - lo + 1  # extracted_rope.__len__()
        return extracted_rope

    def insert(self, index, new_rope):
        """Insert new rope before index 'index'"""
        if not isinstance(new_rope, Rope):
            new_rope = Rope(new_rope, self.leafsize)
        if not new_rope:
            return
        left, right = self.__splitrope(self.root, index)
        left = self.__append(left, new_rope.root, update_thread=True)
        self.root = self.__append(left, right, update_thread=True)
        self.__size += new_rope.size

    def split_merge(self, split_start, split_end, merge_after):
        """
        split rope at (split_start,split_end) and merge it
        before 'merge_after'th character in the splitted node.
        """
        mid = self.delete(split_start, split_end)
        self.insert(merge_after, mid)

    def copy(self):
        """
        using utility __create_copy_util, duplicate the
        Rope and return the new copied Rope object
        """
        new_node = self.__copy_util(self.root)
        rope_object = Rope(leafsize=self.leafsize)
        rope_object.root = new_node
        rope_object._Rope__size = self.__size
        return rope_object

    def reverse(self):
        """reverse the Rope inplace in O(n)"""
        self.__reverse(self.root)

    def lower(self):
        self.__change_case(self.root, str.lower)
        return self

    def upper(self):
        self.__change_case(self.root, str.upper)
        return self

    def swapcase(self):
        self.__change_case(self.root, str.swapcase)
        return self

    def capitalize(self):
        self.__change_case(self.root, str.lower)
        self[0] = str(self[0]).upper()
        return self

    def islower(self):
        return self.__check_type(self.root, str.islower)

    def isupper(self):
        return self.__check_type(self.root, str.isupper)

    def isalnum(self):
        return self.__check_type(self.root, str.isalnum)

    def isalpha(self):
        return self.__check_type(self.root, str.isalpha)

    def isascii(self):
        return self.__check_type(self.root, str.isascii)

    def isdecimal(self):
        return self.__check_type(self.root, str.isdecimal)

    def isdigit(self):
        return self.__check_type(self.root, str.isdigit)

    def isidentifier(self):
        return self.__check_type(self.root, str.isidentifier)

    def isnumeric(self):
        return self.__check_type(self.root, str.isnumeric)

    def isprintable(self):
        return self.__check_type(self.root, str.isprintable)

    def refresh(self):
        """
        Using postorder traversal this will update
        any node according to self.leafsize,if found
        de-configured. Also re-balance the unbalanced
        nodes, if any.
        """
        self.root = self.__refresh(self.root)

    def __len__(self, root=None):
        """
        return length of rope in O(logn)
        Rope.size will also returns the same in
        O(1) but this function is used internally
        at several places where self.size can't be used.
        """
        if root is None:
            root = self.root
        head = root
        count = 0
        while head:
            count += head.weight
            if head.val is not None:
                break
            head = head.rc
        return count

    def __repr__(self, root=False):
        if root is False:
            root = self.root
        return f"Rope('{''.join(v for v in self.__inorder(root))}')"

    def __str__(self):
        return ''.join(v for v in self.__inorder(self.root))

    def __add__(self, other):
        """
        concatnate self.root and other.root to
        create a new root and return it as NEW
        ROPE. inplace=False to ensure new rope
        isn't shared wih self.root or other.root
        """
        return self.append(other, inplace=False)

    def __mul__(self, key):
        """
        return a copy of rope with size
        of self*key
        """
        assert key >= 0, "must be positive number"
        if not key:
            return Rope()
        new_rope = self.copy()
        for i in range(key - 1):
            new_rope.append(self.copy())
        # new_rope._Rope__size = self.__size * key
        return new_rope

    def __delitem__(self, index):
        """
        >> del rope[index] will delete value at 'index'
        """
        self.__delete(index, index)

    def __setitem__(self, index, val):
        """
        modify value at 'index' index in Rope
        Equivalent to del rope[index] followed by
        rope.insert(index,val) but more efficient.
        """

        if isinstance(index, int):
            if (not isinstance(val, str)) or len(val) != 1:
                raise ValueError("only character allowed, use slice instead")
            length = self.__len__()
            if 0 <= index < length:
                pass
            elif -1 * length <= index < 0:
                index = length + index
            else:
                raise IndexError("Index out of range")
            self.__modify_key(self.root, index, val)
        elif isinstance(index, slice):
            if not isinstance(val, Rope):
                val = Rope(val, self.leafsize)
            start, end, step = index.start, index.stop, index.step
            rope_length = self.size  # len(self)
            if start is None:
                start = 0
            elif start < 0:
                start += self.size
            if end is None or end > rope_length:
                end = rope_length
            elif end < 0:
                end += self.size
            if start > end:
                return
            if step is not None:
                class UnsupportedOperation(Exception):
                    pass

                raise UnsupportedOperation("slice-step is not supported")
            end -= 1  # excluding index.stop
            start = max(0, start)
            end = min(end, rope_length - 1)
            self.__delete(start, end)
            self.insert(start, val)
        else:
            raise ValueError("only integer or slice allowed")

    def __getitem__(self, index):
        """
        make rope subscriptable. i.e., similar
        to string, rope object can be queried for
        index 'index'.
        >> rope[index] will return value at 'index'
        >> rope[lo:hi:d] will return string equivalent
        to ropestring[lo:hi:d]
        In both cases, returned is a Rope Object.
        """
        if isinstance(index, int):
            return self.find(index)
        elif isinstance(index, slice):
            start, end, step = index.start, index.stop, index.step
            if step == 0:
                raise ValueError("Step cannot be 0")
            rope_length = self.__size  # len(self)
            if (start is None) and (end is None) and (step is None):
                return self
            if step is None:
                step = 1
            if step > 0:
                if start is None:
                    start = 0
                elif start < 0:
                    start += rope_length
                if (end is None) or (end >= rope_length):
                    end = rope_length
                elif end < 0:
                    end += rope_length
                end -= 1
                start = max(0, start)
                end = min(end, rope_length)
                if start > end:
                    return Rope(leafsize=self.leafsize)
            else:
                if (start is None) or (start > rope_length):
                    start = rope_length
                elif start < 0:
                    start += rope_length
                if end is None:
                    end = -1
                elif end < 0:
                    end += rope_length
                end += 1
                start = min(start, rope_length)
                end = max(0, end)
                if start < end:
                    return Rope(leafsize=self.leafsize)
                start, end = end, start
            sliced_str = ''.join(v for v in self.__inorder(self.root, start, end))
            if step > 0:
                temp = sliced_str[::step]
            else:
                temp = (sliced_str[::-1])[::-step]
            return Rope(temp, self.leafsize)
        raise ValueError("only integer or slice allowed")

    def __iter__(self):
        self.iterator = self.__inorder(self.root)
        return self.iterator

    def __next__(self):
        return next(self.iterator)

    def __eq__(self, other):
        if not isinstance(other, Rope):
            raise TypeError(f"Cannot compare Rope with {type(other)}")
        if self.size == other.size and str(self) == str(other):
            return True
        return False

    def __lt__(self, other):
        if not isinstance(other, Rope):
            raise TypeError(f"Cannot compare Rope with {type(other)}")
        return str(self) < str(other)

    def __bool__(self):
        return bool(self.size)

    def display(self, function=None):
        """
        return visual of Rope Tree.
        if function is None:
            All internal nodes will show weight; leaves will show 'substring';
        else:
            user-defined visual
        NOTE: function must use attributes from ('weight', 'height', 'val') as it is.
        Exmaple: the default function is:
         >> lambda root: f"({root.val if root.val else root.weight})"
        """

        def visualizer(root):
            return f"({root.val if root.val else root.weight})"

        if self.root is None:
            return ''
        if function is None:
            function = visualizer
        lines, _, _, _ = self.__display_aux(self.root, function)
        for line in lines:
            print(line)

    def __display_aux(self, root, func=None):
        """Returns list of strings, width, height, and
         horizontal coordinate of the root."""
        # No child.
        if root and root.val is not None:  # root.rc is None and root.lc is None:
            line = func(root)
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Ropes are always strict binary tree
        # Two children.
        left, n, p, x = self.__display_aux(root.lc, func)
        right, m, q, y = self.__display_aux(root.rc, func)
        s = func(root)
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2


def dis(root):
    """function to visualize threads in ropes. Just pass in rope.display(dis)"""
    if root.val is None:
        return f"({root.lc is None})({root.weight})({root.rc is None})"
    return f"({root.lc.val if root.lc else ''})[{root.val}]({root.rc.val if root.rc else ''})"

