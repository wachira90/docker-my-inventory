#!python
import GPUtil
from tabulate import tabulate

'''
pip3 install gputil
pip3 install tabulate
'''

print("="*40, "GPU Details", "="*40)
gpus = GPUtil.getGPUs()
list_gpus = []
for gpu in gpus:
    # get the GPU id
    gpu_id = gpu.id
    # name of GPU
    gpu_name = gpu.name
    # get % percentage of GPU usage of that GPU
    gpu_load = f"{gpu.load*100}%"
    # get free memory in MB format
    gpu_free_memory = f"{gpu.memoryFree}MB"
    # get used memory
    gpu_used_memory = f"{gpu.memoryUsed}MB"
    # get total memory
    gpu_total_memory = f"{gpu.memoryTotal}MB"
    # get GPU temperature in Celsius
    gpu_temperature = f"{gpu.temperature} °C"
    gpu_uuid = gpu.uuid
    list_gpus.append((
        gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
        gpu_total_memory, gpu_temperature, gpu_uuid
    ))

print(tabulate(list_gpus, headers=("id", "name", "load", "free memory", "used memory", "total memory", "temperature", "uuid")))

'''
======================================== GPU Details ========================================
  id  name              load    free memory    used memory    total memory    temperature    uuid
----  ----------------  ------  -------------  -------------  --------------  -------------  ----------------------------------------
   0  GeForce GTX 1050  2.0%    3976.0MB       120.0MB        4096.0MB        52.0 °C        GPU-c9b08d82-f1e2-40b6-fd20-543a4186d6ce
'''
