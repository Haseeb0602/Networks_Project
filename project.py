#Muhammad Hamza 112246/34530  Haseeb Ali Bhatti 36160   BSCS-4A

import time #for sleep function
import pickle #serialization
import random
import sys
import socket #for udp
from collections import defaultdict #dictionary creation
from threading import Thread,Lock #multithreading




class Graph:
  def __init__(self):
    self.lock = Lock() #lock for selecting a single node within the graph (kind of like a semaphore)
    self.nodes = set() #the list of nodes within the graph
    self.edges = defaultdict(list) #list of edges connecting the nodes
    self.distances = {} #weights initially empty set
    
  def add_node(self, value): 
    self.lock.acquire() #lock critical section
    try:
      self.nodes.add(value)#append set
    finally:
      self.lock.release()
    
  def add_edge(self, from_node, to_node, distance):
    self.lock.acquire()#lock critical section
    try:
      self.edges[from_node].append(to_node)#key value pair created, where each neighbor node mapped to current node
      self.edges[to_node].append(from_node) #reverse pair, to create a dual relationship
      self.distances[(from_node, to_node)] = distance #as stated in the requirements, distance from A to B equal to distance from B to A
      self.distances[(to_node, from_node)] = distance
    finally:
      self.lock.release()
#remove locks after each addition

#*****acknowledgment*****
#this part of code was implemented using resource: code.activestate.com/recipes/119466-dijkstras-algorithm-for-shortest-paths/  
def dijkstra(graph, initial): #takes graph object and initial node
  visited = {initial: 0}#starting point set to 0, for example from node A to A , visited distance is 0
  path = {}#dictionary with key as node, value as distance
  
  nodes = set(graph.nodes) #set of nodes of dijkstra equal to set of nodes of graph

  while nodes: #loop until reaches max no. of nodes
    min_node = None #initialize minimum node as null
    for node in nodes: #for each node traversed
      if node in visited: #if node has been discovered
        if min_node is None: #if node does not have any min node (i.e also null)
          min_node = node #make this node the min node
        elif visited[node] < visited[min_node]: #if visited node has lesser value than min_node previously defined for this node
          min_node = node 
    
    if min_node is None: #if node not connected to any neighbours, exit
      break
    
    nodes.remove(min_node) #remove this node from the nodes unexplored
    current_weight = visited[min_node] 

    for edge in graph.edges[min_node]: #for each edge connecting min_node
      weight = current_weight + graph.distances[(min_node, edge)] #add the current weight to the weights of all the distances previously required to get to this node
      if edge not in visited or weight < visited[edge]: #if edge was never there in the visited list (i.e new path) or shorter path than previous visited edges 
        visited[edge] = weight #make this new weight for shortest path
        path[edge] = min_node #add node to path for short distance
        
  return visited, path #after all nodes traversed and path created, return path and visited nodes list
  

def shortestPath(self,P,target):
  path = [] 
  while True:
    path.append(target)
    if target == self:
      break
    target = P[target]
  
  path.reverse()
  return path


def broadcast(s, self, neighbours_cost, neighbours_port):
  while True:
    seq = random.randint(0,10000)
    # seq = 200
    for i, v in enumerate(neighbours_port):
        value = {'from':self,'neighbours':neighbours_cost,'seq':seq}
        packet = pickle.dumps(value)
        s.sendto(packet, ('127.0.0.1',neighbours_port[v]))#v is its neighbours
        # print value['neighbours'][v]
        # print 'sent to %d' %(neighbours_port[v])
    time.sleep(1)


def rebroadcast(s, self, graph, port, neighbours_port, received_lsp):
  #gotta checks for incoming packet, and will rebroadcast while also adding more to the topology
  time.sleep(40)
  while True:
    rereceived = False
    # print 'waiting for lsp'
    packet, client = s.recvfrom(1024) #lsp doesn't go over 300
    message = pickle.loads(packet)
    broadcasted_neighbour = message['neighbours']
    source = message['from']
    
    #checks whether this is a message previously received or not
    if message['seq'] in received_lsp:
      rereceived = True
    
    #checks if lsp is from source
    if source != self and rereceived == False:
      # print message
      received_lsp.add(message['seq'])
      for i, v in enumerate(broadcasted_neighbour):
        graph.add_node(v)
        graph.add_edge(message['from'],v,broadcasted_neighbour[v])
      
      for i, v in enumerate(neighbours_port):
        if v != source:
          s.sendto(packet, ('127.0.0.1',neighbours_port[v]))
          # print 'rebroadcasted packet from %s' %(source)


def countShortest(self,graph,received_lsp):
  while True:
    time.sleep(30)
    visited, path = dijkstra(graph, self)
    for node in graph.nodes:
      string = ''
      route = shortestPath(self, path, node)
      for track in route:
        string = string+track
      if string != node:
        print 'least-cost path to node %s: %s and the cost is %.1f' %(node,string,round(visited[node],1))
    print ''
    received_lsp = set()#clears the previous 30 seconds worth of seq nums

#--------------------------------main is here----------------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

self = sys.argv[1]
port = int(sys.argv[2])
f = open(sys.argv[3],'r')
neighbours_cost = {}
neighbours_port = {}
received_lsp = set()
threads = []
num_of_neighbour = f.readline()
num_of_neighbour = int(num_of_neighbour)

host=''
s.bind((host,port))


graph = Graph()
graph.add_node(self)

for i in range (0,num_of_neighbour):
  read = f.readline()
  read = read.split()
  neighbours_cost[read[0]] = float(read[1])
  neighbours_port[read[0]] = int(read[2])
  graph.add_node(read[0])
  graph.add_edge(self, read[0], float(read[1]))

try:
  #broadcast thread
  print 'starting broadcast thread'
  t1 = Thread(target=broadcast, kwargs={'s':s,'self':self,'neighbours_cost':neighbours_cost,'neighbours_port':neighbours_port})
  t1.daemon = True
  #rebroadcast thread
  print 'starting rebroadcast thread'
  t2 = Thread(target=rebroadcast, kwargs={'s':s,'self':self,'graph':graph,'port':port,'neighbours_port':neighbours_port,'received_lsp':received_lsp})
  t2.daemon = True
  #dijkstra thread
  print 'starting dijkstra thread'
  t3 = Thread(target=countShortest, kwargs={'self':self,'graph':graph, 'received_lsp':received_lsp})
  t3.daemon = True
  threads.append(t1)
  threads.append(t2)
  threads.append(t3)
  t1.start()
  t2.start()
  t3.start()
  while True:
      i = 1
except KeyboardInterrupt:
  print 'keyboard interrupt triggered'
  s.close()
  sys.exit(1)
