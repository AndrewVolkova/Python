import os
from psutil import Process

def mem_used()->float:
  proc: Process = Process(os.getpid())
  mb : float = proc.memory_info().rss / (1024 * 1024)
  
  return mb


mem_before_import = mem_used()

import numpy
# from numpy import PZERO

from math import sqrt

def sqrt():
  pass

print(sqrt(555))

mem_after_import = mem_used()
mem_diff = mem_after_import - mem_before_import

print(f"До импорта модуля: {mem_before_import:.2f} Mb")
print(f"После импорта модуля: {mem_after_import:.2f} Mb")
print(f"Разница : {mem_diff:.2f} Mb")