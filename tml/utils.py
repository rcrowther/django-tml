from collections import deque


class Stack():
    
    # Python drains
    def __init__(self):
        self.stack = deque()

    @property
    def isEmpty(self):
        return (len(self.stack) == 0)

    @property
    def length(self):
        return len(self.stack)
                
    def push(self, e):
        self.stack.appendleft(e) 

    def pop(self):
        '''
        return
            top element from stack. If empty, None
        '''
        r = None
        if (self.stack):
            r = self.stack.popleft() 
        return r
        
    def head(self):
        '''
        return
            top element on stack, if empty, None
        '''
        r = None
        if (self.stack):
            r = self.stack[0]
        return r
        
    def reverse(self):
        return reversed(self.stack)
        
    def __repr__(self):
        xe = ', '.join((str(e) for e in self.stack))
        return "Stack({})".format(xe)
        
