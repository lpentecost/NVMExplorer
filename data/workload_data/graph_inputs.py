# This file includes memory access data for breadth-first search (BFS) and 
# single source shortest path (SSSP) on two 
# different social network graphs (Wikipedia and Facebook). These traffic patterns 
# come from throughput and access counts reported for the compute stream of a 
# domain-specific graph processing accelerator utilizing an 8MB eDRAM scratchpad

# References:
# J. Leskovec and A. Krevl, “SNAP Datasets: Stanford large network dataset collection,” 
# http://snap.stanford.edu/data, Jun. 2014.
#
# T. J. Ham, L. Wu, N. Sundaram, N. Satish, and M. Martonosi,“Graphicionado: A high-
# performance and energy-efficient accelerator for graph analytics,” in2016 49th Annual 
# IEEE/ACM International Symposium on Microarchitecture (MICRO), 2016, pp. 1–13.
#
# S. Beamer, K. Asanovic, and D. Patterson, “Locality exists in graph processing: 
# Workload characterization on an ivy bridge server,” in 2015 IEEE International 
# Symposium on Workload Characterization,2015, pp. 56–65.

graph8MB = {
  "names": ["Facebook--BFS8MB",
            "Facebook--SSSP8MB",
            "Wikipedia--BFS8MB",
  ],
  "raw_thruput": [1.6e9, #edges/s
                  1.4e9,
                  1e8
  ],
  "read_freq": [4.2e7,
                2.8e8,
                1.3e6
  ],
  "write_freq": [8.8e5,
                 1.9e5,
                 7.2e4
  ],
}

