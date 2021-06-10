import numpy as np
import snap
import time

def gen_adj_mat(G):
  """ Generate an adjacency matrix (size NxN for N node graph) for an input snapPY graph

  :param G: snapPY input graph
  """
  nodes = G.GetNodes()
  print(nodes)
  mat = np.zeros((nodes, nodes))
  for edge in G.Edges():
    src = edge.GetSrcNId() #source node
    dst = edge.GetDstNId() #dest node
    if (src >= nodes):
      src = src % nodes
    if (dst >= nodes):
      dst = dst % nodes
    mat[src][dst] += 1
  print(mat)
  return mat


def gen_graph(M): #generate SNAP graph from adjacency matrix
  """ Generate a snapPY graph based on an adjacency matrix

  :param M: adjacency matrix representing stored graph
  """
  newG = snap.PNGraph.New()
  [ newG.AddNode(i) for i in range(len(M)) ]
  #for i in range(len(M)):
  #  newG.AddNode(i)
  for i in range(len(M)):
    for j in range(len(M[i])):
      if M[i][j] > 0:
        newG.AddEdge(i, j)
  return newG

def pack_bits(M, bpc=2): #pack multiple bits per entry according to storage density
  """ For MLC storage, pack adjacency matrix according to MLC settings

  :param M: adjacency matrix representing stored graph
  :param bpc: bits-per-cell for MLC storage format
  """
  entries = int(np.ceil(len(M)/bpc))
  M_pack = np.zeros((len(M), entries))
  for n in range(len(M)):
    for e in range(entries): #iterate over each entry of the packed M
      for b in range(bpc): #extract and append a bit according to cfg
        dst = e*(bpc)+b
        #print(n, e, M_pack[n][e], n, dst, M[n][dst])
        if (dst) >= len(M):
          continue #if out of range of number of nodes, don't add
        if M[n][dst] > 0:
          M_pack[n][e] += 2**(b)

  #print(M_pack)
  return M_pack

def unpack_bits(M_pack, bpc=2): #unpack multiple bits per matrix entry according to storage density
  """ For MLC storage, unpack adjacency matrix according to MLC settings

  :param M: adjacency matrix representing stored graph, packed according to MLC storage settings
  :param bpc: bits-per-cell for MLC storage format
  """
  nodes = len(M_pack) #this is still the number of nodes
  entries = int(np.ceil(nodes/bpc))
  M = np.zeros((nodes, nodes))
  for n in range(nodes):
    for e in range(entries):
      val = int(M_pack[n][e])
      for b in range(bpc):
        dst = e*(bpc)+b
        #print(n, e, val, n, dst, M[n][dst])
        if (dst) >= nodes:
          continue
        mask = 1 << b
        if (mask & val) > 0:
          M[n][dst] = 1

  #print(M)
  return M



