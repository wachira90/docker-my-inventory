#!python
import psutil
import platform
from datetime import datetime

'''
pip3 install psutil
'''

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

'''
System Information
'''

print("="*40, "System Information", "="*40)
uname = platform.uname()
print(f"System: {uname.system}")
print(f"Node Name: {uname.node}")
print(f"Release: {uname.release}")
print(f"Version: {uname.version}")
print(f"Machine: {uname.machine}")
print(f"Processor: {uname.processor}")

'''
Boot Time
'''

print("="*40, "Boot Time", "="*40)
boot_time_timestamp = psutil.boot_time()
bt = datetime.fromtimestamp(boot_time_timestamp)
print(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")


'''
CPU Information
'''

# let's print CPU information
print("="*40, "CPU Info", "="*40)
# number of cores
print("Physical cores:", psutil.cpu_count(logical=False))
print("Total cores:", psutil.cpu_count(logical=True))
# CPU frequencies
cpufreq = psutil.cpu_freq()
print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
# CPU usage
print("CPU Usage Per Core:")
for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
    print(f"Core {i}: {percentage}%")
print(f"Total CPU Usage: {psutil.cpu_percent()}%")

'''
Memory Usage
'''

# Memory Information
print("="*40, "Memory Information", "="*40)
# get the memory details
svmem = psutil.virtual_memory()
print(f"Total: {get_size(svmem.total)}")
print(f"Available: {get_size(svmem.available)}")
print(f"Used: {get_size(svmem.used)}")
print(f"Percentage: {svmem.percent}%")
print("="*20, "SWAP", "="*20)
# get the swap memory details (if exists)
swap = psutil.swap_memory()
print(f"Total: {get_size(swap.total)}")
print(f"Free: {get_size(swap.free)}")
print(f"Used: {get_size(swap.used)}")
print(f"Percentage: {swap.percent}%")


'''
Disk Usage
'''

# Disk Information
print("="*40, "Disk Information", "="*40)
print("Partitions and Usage:")
# get all disk partitions
partitions = psutil.disk_partitions()
for partition in partitions:
    print(f"=== Device: {partition.device} ===")
    print(f"  Mountpoint: {partition.mountpoint}")
    print(f"  File system type: {partition.fstype}")
    try:
        partition_usage = psutil.disk_usage(partition.mountpoint)
    except PermissionError:
        # this can be catched due to the disk that
        # isn't ready
        continue
    print(f"  Total Size: {get_size(partition_usage.total)}")
    print(f"  Used: {get_size(partition_usage.used)}")
    print(f"  Free: {get_size(partition_usage.free)}")
    print(f"  Percentage: {partition_usage.percent}%")
# get IO statistics since boot
disk_io = psutil.disk_io_counters()
print(f"Total read: {get_size(disk_io.read_bytes)}")
print(f"Total write: {get_size(disk_io.write_bytes)}")


'''
Network Information
'''

# Network information
print("="*40, "Network Information", "="*40)
# get all network interfaces (virtual and physical)
if_addrs = psutil.net_if_addrs()
for interface_name, interface_addresses in if_addrs.items():
    for address in interface_addresses:
        print(f"=== Interface: {interface_name} ===")
        if str(address.family) == 'AddressFamily.AF_INET':
            print(f"  IP Address: {address.address}")
            print(f"  Netmask: {address.netmask}")
            print(f"  Broadcast IP: {address.broadcast}")
        elif str(address.family) == 'AddressFamily.AF_PACKET':
            print(f"  MAC Address: {address.address}")
            print(f"  Netmask: {address.netmask}")
            print(f"  Broadcast MAC: {address.broadcast}")
# get IO statistics since boot
net_io = psutil.net_io_counters()
print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")


'''
======================================== System Information ========================================
System: Linux
Node Name: rockikz
Release: 4.17.0-kali1-amd64
Version: #1 SMP Debian 4.17.8-1kali1 (2018-07-24)
Machine: x86_64
Processor:
======================================== Boot Time ========================================
Boot Time: 2019/8/21 9:37:26
======================================== CPU Info ========================================
Physical cores: 4
Total cores: 4
Max Frequency: 3500.00Mhz
Min Frequency: 1600.00Mhz
Current Frequency: 1661.76Mhz
CPU Usage Per Core:
Core 0: 0.0%
Core 1: 0.0%
Core 2: 11.1%
Core 3: 0.0%
Total CPU Usage: 3.0%
======================================== Memory Information ========================================
Total: 3.82GB
Available: 2.98GB
Used: 564.29MB
Percentage: 21.9%
==================== SWAP ====================
Total: 0.00B
Free: 0.00B
Used: 0.00B
Percentage: 0%
======================================== Disk Information ========================================
Partitions and Usage:
=== Device: /dev/sda1 ===
  Mountpoint: /
  File system type: ext4
  Total Size: 451.57GB
  Used: 384.29GB
  Free: 44.28GB
  Percentage: 89.7%
Total read: 2.38GB
Total write: 2.45GB
======================================== Network Information ========================================
=== Interface: lo ===
  IP Address: 127.0.0.1
  Netmask: 255.0.0.0
  Broadcast IP: None
=== Interface: lo ===
=== Interface: lo ===
  MAC Address: 00:00:00:00:00:00
  Netmask: None
  Broadcast MAC: None
=== Interface: wlan0 ===
  IP Address: 192.168.1.101
  Netmask: 255.255.255.0
  Broadcast IP: 192.168.1.255
=== Interface: wlan0 ===
=== Interface: wlan0 ===
  MAC Address: 64:70:02:07:40:50
  Netmask: None
  Broadcast MAC: ff:ff:ff:ff:ff:ff
=== Interface: eth0 ===
  MAC Address: d0:27:88:c6:06:47
  Netmask: None
  Broadcast MAC: ff:ff:ff:ff:ff:ff
Total Bytes Sent: 123.68MB
Total Bytes Received: 577.94MB
'''
