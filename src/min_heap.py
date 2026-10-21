class MinHeap:
    def __init__(self):
        self.heap = []

    def __len__(self):
        return len(self.heap)

    def is_empty(self):
        return len(self.heap) == 0
    
    def insert(self, node):
        self.heap.append(node)
        self.heapify_up(len(self.heap) - 1)

    def heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2

            if self.heap[index].frequency >= self.heap[parent].frequency:
                break

            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            index = parent
    
    def peek(self):
        if self.is_empty():
            return None
        return self.heap[0]

    def extract_min(self):
        if self.is_empty():
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        minimum = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.heapify_down(0)

        return minimum

    def heapify_down(self, index):
        size = len(self.heap)

        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if left < size and self.heap[left].frequency < self.heap[smallest].frequency:
                smallest = left

            if right < size and self.heap[right].frequency < self.heap[smallest].frequency:
                smallest = right

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            index = smallest