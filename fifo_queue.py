# Auxiliary class that implements a FIFO queue with a maximum size

class Fifo:
    def __init__(self, max_size=2):
        self.max_size = max_size
        self.queue = []

    def push(self, item):
        # insert at the beginning of the queue
        self.queue.insert(0, item)
        # ensure the queue does not exceed the max size
        if len(self.queue) > self.max_size:
            self.queue.pop()

    def pop(self):
        if len(self.queue) == 0:
            return
        else:
            self.queue.pop()
    
    def get_first(self):
        if len(self.queue) == 0:
            return None
        else:
            return self.queue[0]
    
    def get_last(self):
        if len(self.queue) == 0:
            return None
        else:
            return self.queue[-1]
    
    def get_last_in_max_size(self):
        if len(self.queue) == self.max_size:
            return self.queue[-1]
        else:
            return None
        
    def __len__(self):
        return len(self.queue)

    def __str__(self):
        return str(self.queue)
