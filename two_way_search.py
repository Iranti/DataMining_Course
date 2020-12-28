import queue
#??from ..insta_spider import InstagramSpider

class Node:
  def __init__(self, val):
    self.val = val
    self.neighbors = None
    self.visited_right = False
    self.visited_left = False
    self.parent_right = None
    self.parent_left = None


def bidirectional_search(s, t):

  def extract_path(node):
    """return the path when both BFS's have met"""
    node_copy = node
    path = []

    while node:
      path.append(node.val)
      node = node.parent_right

    path.reverse()
    del path[-1]  # because the meeting node appears twice

    while node_copy:
      path.append(node_copy.val)
      node_copy = node_copy.parent_left
    return path


  q = queue.Queue()
  q.put(s)
  q.put(t)
  s.visited_right = True
  t.visited_left = True

  while not q.empty():
    n = q.get()

    if n.visited_left and n.visited_right:  # if the node visited by both BFS's
      return extract_path(n)

    for node in n.neighbors:
      if n.visited_left == True and not node.visited_left:
        node.parent_left = n
        node.visited_left = True
        q.put(node)
      if n.visited_right == True and not node.visited_right:
        node.parent_right = n
        node.visited_right = True
        q.put(node)

  return False

#??def new_node_generator()


n0 = Node(0)
n1 = Node(1)
n2 = Node(2)
n3 = Node(3)
n4 = Node(4)
n5 = Node(5)
n6 = Node(6)
n7 = Node(7)
n0.neighbors = [n1, n5]
n1.neighbors = [n0, n2, n6, n5]
n2.neighbors = [n1]
n3.neighbors = [n4, n6, n7]
n4.neighbors = [n3]
n5.neighbors = [n0, n6]
n6.neighbors = [n1, n3, n5, n7]
n7.neighbors = [n6]
print(bidirectional_search(n1, n2))
