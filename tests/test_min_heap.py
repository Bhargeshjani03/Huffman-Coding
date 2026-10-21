from src.min_heap import MinHeap
from src.node import HuffmanNode

heap = MinHeap()

print("Empty heap:", heap.is_empty())
print("Peek empty:", heap.peek())
print("Extract empty:", heap.extract_min())

heap.insert(HuffmanNode(symbol=65, frequency=7))
print("Single node peek:", heap.peek().frequency)
print("Single node extract:", heap.extract_min().frequency)
print("Empty after extract:", heap.is_empty())

for symbol, frequency in [(65, 4), (66, 2), (67, 2), (68, 8)]:
    heap.insert(HuffmanNode(symbol=symbol, frequency=frequency))

result = []
while not heap.is_empty():
    result.append(heap.extract_min().frequency)

print("Sorted extraction:", result)