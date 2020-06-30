from collections.abc import Container as _CONTAINER_
from warnings import warn as _WARN_

class _RopeNode(object):
    def __init__(self,weight,value=None):
        self.lc=None #Left Child
        self.rc=None #Right Child
        self.weight=weight #String size on lc
        self.val=value #'sub-string' if leaf node else None
        self.height=0 # for height balancing
    
    def __len__(self):
        return self.weight

class Rope(object):
    """
    - Value of all internal nodes will be None.
    - Value of all leaf nodes will be some sub-string of
            length not more than leafsize.
    """
    def __init__(self,raw=None,leafsize=8):
        self.root=None
        self.__size=0
        self.__LEAFSIZE=leafsize
        if raw is None:
            return
        if isinstance(raw,str):
            self.raw=raw
            self.root=self.__create_rope(0,len(raw)-1)
            return
        if isinstance(raw,_CONTAINER_):
            for string in raw:
                rope=Rope(string,self.leafsize)
                self.__size+=rope.size
                self.root=self.__append_left(self.root,rope.root)
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
        return self.__LEAFSIZE
    
    @leafsize.getter
    def leafsize(self):
        return self.__LEAFSIZE
    
    @leafsize.setter
    def leafsize(self,value):
        if value<=0 or not isinstance(value,int):
            raise ValueError("leafsize must be positive Integer")
        if value<4:
            _WARN_("smaller leafsizes will consume larger memory."+
                   " Most Suitable numbers for leafsizes are"+
                   " 4,8,16,32")
        self.__LEAFSIZE=value
        self.root=self.__refresh(self.root)
    
    def __create_rope(self,l,r):
        """create rope from a string raw[l:r+1]"""
        if l+self.leafsize>r:
            self.__size+=r-l+1
            return _RopeNode(r-l+1,self.raw[l:r+1])
        mid=(l+r)//2
        root=_RopeNode(mid-l+1)
        root.lc=self.__create_rope(l,mid)
        root.rc=self.__create_rope(mid+1,r)
        return self.Balance(root)
    
    def __find(self,root,i):
        """
        utility for find() function. Returns a 
        rope with single character at self.root[i]
        """
        if i<root.weight:
            if root.lc:
                return self.__find(root.lc,i)
            return Rope(root.val[i],self.leafsize)
        i-=root.weight
        return self.__find(root.rc,i)
    
    def find(self,i):
        """
        Return value of rope at index 'i'. Returned
        value is also a Rope object
        """
        if 0<=i<self.__len__():
            pass
        elif -1*self.__len__()<=i<0:
            i=self.__len__()+i
        else:
            raise IndexError("Index out of range")
        return self.__find(self.root,i)
    
    def __append_left(self,ropeto,ropein):
        """
        ropeto and ropein are 'roots' of two
        Ropes to be merged. Merge ropto to 
        ropein
        
                    new_root
                   /        \
                ropeto      ropein
                
         if any of the ropeto or ropein is None, 
         return the other else return new_root
        """
        if ropeto and ropein:
            count_right=self.__len__(ropeto)
            if ropein.val:
                #ropein must be a leaf
                count_left=self.__len__(ropein)
                total=count_left+count_right
                if total<=self.leafsize:
                    # ropeto also must have been a LEAF.
                    # Shrink to single NODE since combined
                    # length is still less/equal to LEAFSIZE
                    s=ropeto.val+ropein.val
                    return _RopeNode(len(s),s)
            root=_RopeNode(count_right)
            root.lc,root.rc=ropeto,ropein
            return self.Balance(root)
        if ropeto:
            return ropeto
        return ropein
    
    def __append_right(self,ropein,ropeto):
        """
        ropeto and ropein are 'roots' of two
        Ropes to be merged. Merge ropeto to 
        ropein
        
                    new_root
                   /        \
                ropein      ropeto
                
         if any of the ropeto or ropein is None, 
         return the other else return new_root
         
         Counter of this is __append_left. Although
         working of both can be merged to single 
         __append function but they are kept as it is
         to reduce complexity of code implementation
        """
        if ropeto and ropein:
            count_left=self.__len__(ropein)
            if ropeto.val:
                # ropeto must be a leaf
                count_right=self.__len__(ropeto)
                total=count_left+count_right
                if total<=self.leafsize:
                    # ropein also must have been a LEAF.
                    # Shrink to single NODE since combined
                    # length is still less/equal to LEAFSIZE
                    s=ropein.val+ropeto.val
                    return _RopeNode(len(s),s)
            root=_RopeNode(count_left)
            root.lc,root.rc=ropein,ropeto
            return self.Balance(root)
        if ropeto:
            return ropeto
        return ropein
    
    def append(self,other_rope,inplace=True):
        """
                     new_root         
                    /        \         
              self.root     other_rope 
              
        if inplace is True:
            self.root=new_root
            return self
        else:
            CREATES A COPY of above rope
            return new Rope Object
        """
        if not isinstance(other_rope,Rope):
            other_rope=Rope(other_rope,self.leafsize)
        new_root=self.__append_left(self.root,other_rope.root)
        if inplace:
            self.root=new_root
            self.__size+=other_rope._Rope__size
            return self
        new_root=self.__copy_util(new_root)
        new_rope=Rope(leafsize=self.leafsize)
        new_rope.root=new_root
        new_rope._Rope__size=self.__size+other_rope._Rope__size
        return new_rope
    
    def Height(self,node):
        """
        return the level of a node. Root is assumed
        at top level while leaves are at level 0
        """
        return node.height if node else 0
    
    def Balance(self,root):
        """
        Uses AVLTree concept for balancing Ropes.
        Calling it will balance 'root' and decendents.
        Although this can be accessed from Rope object
        but user don't need to do manual balancing unless
        some rare situation. Ropes are already automated
        to balance themselves own their own.
        """
        if root and root.val is None:
            lc,rc=root.lc,root.rc
            if self.Height(lc)>self.Height(rc)+1:
                mid=root.lc
                if self.Height(mid.lc)>self.Height(mid.rc):
                    root=self.LLBalance(root)
                else:
                    root=self.LRBalance(root)
            elif self.Height(rc)>self.Height(lc)+1:
                mid=root.rc
                if self.Height(mid.lc)>self.Height(mid.rc):
                    root=self.RLBalance(root)
                else:
                    root=self.RRBalance(root)
            lc,rc=root.lc,root.rc
            root.height=1+max(self.Height(lc),self.Height(rc))
        return root
    
    def LLBalance(self,root):
        """
        Utility for Balance. Can be accesed from Rope
        object but user doesn't need this explicitly
        """
        parent,left=root,root.lc
        parent=self.__append_left(left.rc,parent.rc)#parent.lc=left.rc
        parent=self.Balance(parent)
        left=self.__append_right(left.lc,parent)#left.rc=parent
        return self.Balance(left)
    
    def LRBalance(self,root):
        """
        Utility for Balance. Can be accesed from Rope
        object but user doesn't need this explicitly
        """
        parent,left=root,root.lc
        mid=left.rc
        left=self.__append_right(left.lc,mid.lc)#left.rc=mid.lc
        left=self.Balance(left)
        parent=self.__append_left(mid.rc,parent.rc)#parent.lc=mid.rc
        parent=self.Balance(parent)
        mid=self.__append_left(left,parent)
        return self.Balance(mid)
    
    def RRBalance(self,root):
        """
        Utility for Balance. Can be accesed from Rope
        object but user doesn't need this explicitly
        """
        parent,right=root,root.rc
        parent=self.__append_right(parent.lc,right.lc)#parent.rc=right.lc
        parent=self.Balance(parent)
        right=self.__append_left(parent,right.rc)#right.lc=parent
        return self.Balance(right)
    
    def RLBalance(self,root):
        """
        Utility for Balance. Can be accesed from Rope
        object but user doesn't need this explicitly
        """
        parent,right=root,root.rc
        mid=right.lc
        right=self.__append_left(mid.rc,right.rc)#right.lc=mid.rc
        right=self.Balance(right)
        parent=self.__append_right(parent.lc,mid.lc)#parent.rc=mid.lc
        parent=self.Balance(parent)
        mid=self.__append_right(parent,right)
        return self.Balance(mid)
    
    def __splitleaf(self,root,key):
        """ 
        root is leafnode, with value 'STRING'
                STRING
              /        \
            None       None
        
        modifies to: (key-dependent)
                STRING
              /        \
            STRI        NG
            
        return refrences to (STR, ING)
        """
        if root is None: return None, None
        s=root.val
        root.lc=_RopeNode(key,s[:key]) if key else None
        root.rc=_RopeNode(root.weight-key,s[key:]) if \
                            root.weight-key else None
        return root.lc,root.rc
    
    def __splitrope_util(self,root,key):
        """
        Utility for __splitrope() function.
        if a 'node' with weight==key encountered:
            return (node.lc, node.rc)
        if key overlaps on a leafnode:
            return spliteLeaf(node,key)
        """
        if root is None: return None,None
        if root.weight==key:
            if root.val is None:
                return root.lc, root.rc
            return root,None
        if root.weight>key: #look in left child
            if root.lc is None:
                left,right=self.__splitleaf(root,key)
                return left,right
            left,right=self.__splitrope_util(root.lc,key)
            right=self.__append_left(right,root.rc)
            return left,right
        key-=root.weight #look in right child
        left,right=self.__splitrope_util(root.rc,key)
        left=self.__append_right(root.lc,left)
        return left,right
    
    def __splitrope(self,root,key):
        """
        Split Rope in two parts at valid index 'key',
        'key' will be included in right part
        """
        if 0<=key<=self.__len__():
            return self.__splitrope_util(root,key)
        if -1*self.__len__()<=key<0:
            key=self.__len__()+key
            return self.__splitrope_util(root,key)
        raise IndexError("Key out of range")
    
    def split(self,index):
        """
        split Rope into two parts at 'index' and
        return 'left' and 'right' Ropes.
        Note that 'self' will Now points to 'left'
        rope
        """
        original_size=self.size
        self.root,right=self.__splitrope(self.root,index)
        self.__size=len(self)
        right_rope=Rope()
        right_rope.root=right
        right_rope._Rope__size=original_size-self.size
        return self,right_rope
    
    def __delete(self,i,j):
        """
        Utility: remove Rope from index i-j (both inclusive)
        return the root node of extracted part
        """
        i,j=max(0,i),min(j,self.size-1)
        left,right=self.__splitrope(self.root,i)
        mid,right=self.__splitrope(right,j-i+1)
        self.root=self.__append_left(left,right)
        if self.root:
            self.__size=self.root.weight+self.__len__(self.root.rc)
        else:
            self.__size=0
        return mid
    
    def delete(self,i,j=None):
        """
        Delete Rope Part from i-j (both inclusive)
        using utility __delete(). Returns the extracted
        part as NEW ROPE
        """
        if j is None:
            j=i
        i,j=max(0,i),min(j,self.size-1)
        mid=self.__delete(i,j)
        extracted_rope=Rope(leafsize=self.leafsize)
        extracted_rope.root=mid
        extracted_rope._Rope__size=j-i+1#extracted_rope.__len__()
        return extracted_rope
    
    def insert(self,index,new_rope):
        """Insert new rope before index 'index'"""
        if not isinstance(new_rope,Rope):
            new_rope=Rope(new_rope,self.leafsize)
        left,right=self.__splitrope(self.root,index)
        left=self.__append_left(left,new_rope.root)
        self.root=self.__append_left(left,right)
        self.__size+=new_rope.size
    
    def split_merge(self,split_start,split_end,merge_after):
        """
        split rope at (split_start,split_end) and merge it
        before 'merge_after'th character in the splitted node.
        """
        mid=self.delete(split_start,split_end)
        self.insert(merge_after,mid)
    
    def __copy_util(self,root):
        """
        Utility: Do postorder traversal and create
        a copy of whole tree rooted at 'root'.
        Returns the ROOT of new tree created.
        This new one is NOT a Rope object yet.
        """
        if root:
            new_node=_RopeNode(root.weight,root.val)
            new_node.height=root.height
            new_node.lc=self.__copy_util(root.lc)
            new_node.rc=self.__copy_util(root.rc)
            return new_node
        return None
    
    def copy(self):
        """
        using utility __create_copy_util, duplicate the
        Rope and return the new copied Rope object
        """
        new_node=self.__copy_util(self.root)
        rope_object=Rope(leafsize=self.leafsize)
        rope_object.root=new_node
        rope_object._Rope__size=self.__size
        return rope_object
    
    def __reverse(self,root):
        """Utility for reverse"""
        if root:
            self.__reverse(root.lc)
            self.__reverse(root.rc)
            root.lc,root.rc=root.rc,root.lc
            if root.val:
                root.val=root.val[::-1]
    
    def reverse(self):
        """reverse the Rope inplace in O(n)"""
        self.__reverse(self.root)
    
    def __change_case(self,root,function):
        if root:
            self.__change_case(root.lc,function)
            if root.val:
                root.val=function(root.val)
            self.__change_case(root.lc,function)
    
    def lower(self):
        self.__change_case(self.root,str.lower)
        return self
    
    def upper(self):
        self.__change_case(self.root,str.upper)
        return self
        
    def swapcase(self):
        self.__change_case(self.root,str.swapcase)
        return self
    
    def capitalize(self):
        self.__change_case(self.root,str.lower)
        self[0]=str(self[0]).upper()
        return self
    
    def __check_type(self,root,function):
        if root:
            if not self.__check_type(root.lc,function):
                return False
            if root.val:
                return function(root.val)
            if not self.__check_type(root.rc,function):
                return False
        return True
    
    def islower(self):
        return self.__check_type(self.root,str.islower)
    
    def isupper(self):
        return self.__check_type(self.root,str.isupper)
    
    def isalnum(self):
        return self.__check_type(self.root,str.isalnum)
    
    def isalpha(self):
        return self.__check_type(self.root,str.isalpha)
    
    def isascii(self):
        return self.__check_type(self.root,str.isascii)
    
    def isdecimal(self):
        return self.__check_type(self.root,str.isdecimal)
    
    def isdigit(self):
        return self.__check_type(self.root,str.isdigit)
    
    def isidentifier(self):
        return self.__check_type(self.root,str.isidentifier)
    
    def isnumeric(self):
        return self.__check_type(self.root,str.isnumeric)
    
    def isprintable(self):
        return self.__check_type(self.root,str.isprintable)
    
    def __refresh(self,root):
        """Utility for refresh"""
        if root and root.val is None:
            root.lc=self.__refresh(root.lc)
            root.rc=self.__refresh(root.rc)
            root=self.__append_left(root.lc,root.rc)
        return root
    
    def refresh(self):
        """
        Using postorder traversal this will update
        any node according to self.leafsize,if found
        deconfigured. Also rebalance the unbalanced
        nodes, if any.
        """
        self.root=self.__refresh(self.root)
    
    def __len__(self,root=False):
        """
        return length of rope in O(logn)
        Rope.size will also returns the same in 
        O(1) but this function is also required 
        at several palces. Users should use
        Rope.size.
        """
        if root==False:
            root=self.root
        head=root
        count=0
        while head:
            count+=head.weight
            head=head.rc
        return count
    
    def __inorder(self,root,ans):
        """return inroder traversal of rope"""
        if root:
            self.__inorder(root.lc,ans)
            if root.lc is None:
                ans.append(root.val)
            self.__inorder(root.rc,ans)
        return ans

    def __repr__(self,root=False):
        ans=[]
        if root==False:
            root=self.root
        self.__inorder(root,ans)
        return f"Rope('{''.join(ans) if ans else ''}')"
    
    def __str__(self):
        ans=[]
        self.__inorder(self.root,ans)
        return ''.join(ans) if ans else ''
    
    def __add__(self,other):
        """
        concatnate self.root and other.root to
        create a new root and return it as NEW 
        ROPE. inplace=False to ensure new rope 
        isn't shared wih self.root or other.root
        """
        if not isinstance(other,Rope):
            other=Rope(other,self.leafsize)
        new_rope=self.append(other,inplace=False)
        return new_rope
    
    def __mul__(self,key):
        """
        return a copy of rope with size
        of self*key
        """
        new_rope=self.copy()
        for i in range(key-1):
            new_rope.append(self.copy())
        new_rope._Rope__size=self.__size*key
        return new_rope
    
    def __delitem__(self,i):
        """
        >> del rope[i] will delete value at index i
        """
        self.__delete(i,i)
    
    def __modify_key(self,root,key,val):
        """
        utility: update value at index 'key' to 'val'
        """
        if key<root.weight:
            if root.lc:
                return self.__modify_key(root.lc,key,val)
            s=root.val
            new_s=s[:key]+val+s[key+1:]
            root.val=new_s
            return
        key-=root.weight
        return self.__modify_key(root.rc,key,val)
    
    def __setitem__(self,index,val):
        """
        modify value at 'index' index in Rope
        Equivalent to del rope[index] followed by
        rope.insert(index,val) but more efficent.
        """
        
        if isinstance(index,int):
            if (not isinstance(val,str)) or len(val)!=1:
                raise ValueError("only character allowed,"+
                                    " use slice instead")
            if 0<=index<self.__len__():
                pass
            elif -1*self.__len__()<=index<0:
                index=self.__len__()+index
            else:
                raise IndexError("Index out of range")
            self.__modify_key(self.root,index,val)
        elif isinstance(index,slice):
            if not isinstance(val,Rope):
                val=Rope(val,self.leafsize)
            start,end,step=index.start,index.stop,index.step
            ROPE_LENGTH=len(self)
            if start is None: start=0
            elif start<0: start+=self.size
            if end is None or end>ROPE_LENGTH: end=ROPE_LENGTH
            elif end<0: end+=self.size
            if start>end: return
            if step is not None:
                class UnsupportedOperation(Exception):
                    pass
                raise UnsupportedOperation("slice-step is"+
                                            " not supported")
            end-=1 #excluding index.stop
            self.__delete(start,end)
            self.insert(start,val)
        else:
            raise ValueError("only integer or slice allowed")
    
    def __getitem__(self,index):
        """
        make rope subscriptable. i.e., similar
        to string, rope object can be queried for 
        index 'index'.
        >> rope[index] will return value at 'index'
        >> rope[l:r:d] will return string equivalent
        to ropestring[l:r:d]
        In both cases, returned is a Rope Object.
        Time: O(j+logn) for slice of size 'j'
        """
        if isinstance(index,int):
            return self.find(index)
        elif isinstance(index,slice):
            start,end,step=index.start,index.stop,index.step
            if step==0:
                raise ValueError("Step cannot be 0")
            ROPE_LENGTH=self.__size
            if start==end==step==None: return self
            if step is None: step=1
            if step>0:
                if start is None: start=0
                elif start<0: start+=ROPE_LENGTH
                if (end is None) or (end>=ROPE_LENGTH): end=ROPE_LENGTH
                elif end<0: end+=ROPE_LENGTH
                end-=1
                start=max(0,start)
                end=min(end,ROPE_LENGTH)
                if start>end:
                    return Rope(leafsize=self.leafsize)
            else:
                if (start is None) or (start>ROPE_LENGTH): start=ROPE_LENGTH
                elif start<0: start+=ROPE_LENGTH
                if end is None: end=-1
                elif end<0: end+=ROPE_LENGTH
                end+=1
                start=min(start,ROPE_LENGTH)
                end=max(0,end)
                if start<end:
                    return Rope(leafsize=self.leafsize)
                start,end=end,start
            sliced_part=self.delete(start,end)
            if step>0:
                temp=str(sliced_part)[::step]
            else:
                temp=(str(sliced_part)[::-1])[::-step]
            self.insert(start,sliced_part)
            return Rope(temp,self.leafsize)
        raise ValueError("only integer or slice allowed")
    
    def __iter__(self):
        for sub in self.__inorder(self.root,[]):
            yield from sub
    
    def __eq__(self,other):
        if not isinstance(other,Rope):
            raise TypeError(f"Cannot compare Rope with {type(other)}")
        if len(self)==len(other) and str(self)==str(other):
            return True
        return False
    
    def __lt__(self,other):
        if not isinstance(other,Rope):
            raise TypeError(f"Cannot compare Rope with {type(other)}")
        return str(self)<str(other)
    
    def __bool__(self):
        return self.size
        
    def display(self,function=None):
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
        if function is None:
            function=lambda root: f"({root.val if root.val else root.weight})"
        if self.root is None:
            return ''
        lines, _, _, _ = self._display_aux(self.root,function)
        for line in lines:
            print(line)
        
    def _display_aux(self,root,func=None):
        """Returns list of strings, width, height, and
         horizontal coordinate of the root."""
        # No child.
        if root.rc is None and root.lc is None:
            line = func(root)
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if root.rc is None:
            lines, n, p, x = self._display_aux(root.lc,func)
            s = func(root)
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return ([first_line, second_line] + shifted_lines,
                    n + u, p + 2, n + u // 2)

        # Only right child.
        if root.lc is None:
            lines, n, p, x = self._display_aux(root.rc,func)
            s = func(root)
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return ([first_line, second_line] + shifted_lines, 
                    n + u, p + 2, u // 2)

        # Two children.
        left, n, p, x = self._display_aux(root.lc,func)
        right, m, q, y = self._display_aux(root.rc,func)
        s = func(root)
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y \
                                        * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' '\
                                    + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for \
                                             a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2
    