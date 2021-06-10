# placeholder definition for an access pattern object, can be passed as input

class PatternConfig:
  def __init__(self, 
		exp_name="default", #name or ID
                benchmark_name="test", #if this is a specific benchmark, include here
		read_freq=-1, #number of reads/s
                total_reads=-1, #total number of reads, can compute either way
		read_size=8, #size/read in bytes
		write_freq=-1, #number of writes/s
                total_writes=-1, #total number of reads, can compute either way
		write_size=8, #size/write in bytes
		workingset=1, #total working set size in MB
		total_ins=-1 #total number of ins in benchmark
		):
    #load all the parameters into the pattern class
    #everything that defines the access pattern should be in this class
    self.exp_name = exp_name
    self.benchmark_name = benchmark_name
    self.read_freq = read_freq
    self.total_reads = total_reads
    self.read_size = read_size
    self.write_freq = write_freq
    self.total_writes = total_writes
    self.write_size = write_size
    self.workingset = workingset  
    self.total_ins = total_ins


benchmarks = [ #collection of benchmarks from Tufts IISWC paper
  PatternConfig(benchmark_name="bzip2",
		total_reads=4.3e9,
		read_size=4,
		total_writes=1.47e9,
		write_size=4,
		workingset=(2505.38e3/1024./1024.),
		total_ins=1404973
		),
  PatternConfig(benchmark_name="GemsFDTD",
		total_reads=1.3e9,
		read_size=4,
		total_writes=0.7e9,
		write_size=4,
		workingset=(76576.59e3/1024./1024.),
		total_ins=475257
		),
  PatternConfig(benchmark_name="tonto",
		total_reads=1.1e9,
		read_size=4,
		total_writes=0.47e9,
		write_size=4,
		workingset=(5.59e3/1024./1024.),
		total_ins=490533
		),
  PatternConfig(benchmark_name="leela",
		total_reads=6.01e9,
		read_size=4,
		total_writes=2.35e9,
		write_size=4,
		workingset=(1.59e3/1024./1024.),
		total_ins=42211
		),
  PatternConfig(benchmark_name="exchange2",
		total_reads=62.28e9,
		read_size=4,
		total_writes=42.89e9,
		write_size=4,
		workingset=(0.64e3/1024./1024.),
		total_ins=417088
		),
  PatternConfig(benchmark_name="deepsjeng",
		total_reads=9.36e9,
		read_size=4,
		total_writes=4.43e9,
		write_size=4,
		workingset=(4.79e3/1024./1024.),
		total_ins=71720506
		),
  PatternConfig(benchmark_name="vips",
		total_reads=1.91e9,
		read_size=4,
		total_writes=0.68e9,
		write_size=4,
		workingset=(1107.19e3/1024./1024.),
		total_ins=3949419070
		),
  PatternConfig(benchmark_name="x264",
		total_reads=18.07e9,
		read_size=4,
		total_writes=2.84e9,
		write_size=4,
		workingset=(1585.49e3/1024./1024.),
		total_ins=229607
		),
  PatternConfig(benchmark_name="cg",
		total_reads=0.73e9,
		read_size=4,
		total_writes=0.04e9,
		write_size=4,
		workingset=(1015.43e3/1024./1024.),
		total_ins=1942892619
		),
  PatternConfig(benchmark_name="ep",
		total_reads=1.25e9,
		read_size=4,
		total_writes=0.54e9,
		write_size=4,
		workingset=(0.84e3/1024./1024.),
		total_ins=7051878902
		),
  PatternConfig(benchmark_name="ft",
		total_reads=0.28e9,
		read_size=4,
		total_writes=0.27e9,
		write_size=4,
		workingset=(342.64e3/1024./1024.),
		total_ins=1416746823
		),
  PatternConfig(benchmark_name="is",
		total_reads=0.12e9,
		read_size=4,
		total_writes=0.06e9,
		write_size=4,
		workingset=(1228.86e3/1024./1024.),
		total_ins=298507496
		),
  PatternConfig(benchmark_name="lu",
		total_reads=17.84e9,
		read_size=4,
		total_writes=3.99e9,
		write_size=4,
		workingset=(289.46e3/1024./1024.),
		total_ins=29482003362
		),
  PatternConfig(benchmark_name="mg",
		total_reads=0.76e9,
		read_size=4,
		total_writes=0.16e9,
		write_size=4,
		workingset=(4249.78e3/1024./1024.),
		total_ins=1308033184
		),
  PatternConfig(benchmark_name="sp",
		total_reads=9.23e9,
		read_size=4,
		total_writes=4.12e9,
		write_size=4,
		workingset=(556.75e3/1024./1024.),
		total_ins=30840210911
		),
  PatternConfig(benchmark_name="ua",
		total_reads=9.97e9,
		read_size=4,
		total_writes=5.85e9,
		write_size=4,
		workingset=(362.45e3/1024./1024.),
		total_ins=19361069980
		),
]
