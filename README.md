# Docker MY Inventory

# **detailed hardware information** 

about your system. It uses the popular `github.com/shirou/gopsutil/v3` package, which gives access to CPU, memory, disk, host, and network information across platforms (Linux, macOS, Windows).

---

### ✅ Prerequisites

Install the dependency with:

```bash
go get github.com/shirou/gopsutil/v3
```

---

### 📄 Full Code: Get Detailed Hardware Specs

```go
package main

import (
	"fmt"
	"log"

	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/disk"
	"github.com/shirou/gopsutil/v3/host"
	"github.com/shirou/gopsutil/v3/mem"
	"github.com/shirou/gopsutil/v3/net"
)

func main() {
	printCPUInfo()
	printMemoryInfo()
	printDiskInfo()
	printHostInfo()
	printNetworkInfo()
}

func printCPUInfo() {
	cpuInfo, err := cpu.Info()
	if err != nil {
		log.Fatalf("Error getting CPU info: %v", err)
	}
	percent, _ := cpu.Percent(0, true)

	fmt.Println("=== CPU Info ===")
	for i, ci := range cpuInfo {
		fmt.Printf("CPU #%d: %s, %d MHz, Cores: %d, Model: %s\n", i, ci.VendorID, int(ci.Mhz), ci.Cores, ci.ModelName)
	}
	for i, p := range percent {
		fmt.Printf("CPU #%d Usage: %.2f%%\n", i, p)
	}
	fmt.Println()
}

func printMemoryInfo() {
	vm, err := mem.VirtualMemory()
	if err != nil {
		log.Fatalf("Error getting memory info: %v", err)
	}

	fmt.Println("=== Memory Info ===")
	fmt.Printf("Total: %v MB\n", vm.Total/1024/1024)
	fmt.Printf("Available: %v MB\n", vm.Available/1024/1024)
	fmt.Printf("Used: %v MB (%.2f%%)\n", vm.Used/1024/1024, vm.UsedPercent)
	fmt.Println()
}

func printDiskInfo() {
	partitions, err := disk.Partitions(true)
	if err != nil {
		log.Fatalf("Error getting disk partitions: %v", err)
	}

	fmt.Println("=== Disk Info ===")
	for _, p := range partitions {
		usage, err := disk.Usage(p.Mountpoint)
		if err != nil {
			continue
		}
		fmt.Printf("Mountpoint: %s, Filesystem: %s, Total: %v GB, Used: %v GB (%.2f%%)\n",
			p.Mountpoint, usage.Fstype,
			usage.Total/1024/1024/1024,
			usage.Used/1024/1024/1024,
			usage.UsedPercent)
	}
	fmt.Println()
}

func printHostInfo() {
	info, err := host.Info()
	if err != nil {
		log.Fatalf("Error getting host info: %v", err)
	}

	fmt.Println("=== Host Info ===")
	fmt.Printf("Hostname: %s\n", info.Hostname)
	fmt.Printf("OS: %s %s (%s)\n", info.Platform, info.PlatformVersion, info.KernelArch)
	fmt.Printf("Uptime: %d seconds\n", info.Uptime)
	fmt.Printf("Boot Time: %d\n", info.BootTime)
	fmt.Println()
}

func printNetworkInfo() {
	interfaces, err := net.Interfaces()
	if err != nil {
		log.Fatalf("Error getting network info: %v", err)
	}

	fmt.Println("=== Network Interfaces ===")
	for _, iface := range interfaces {
		fmt.Printf("Name: %s, MTU: %d, HardwareAddr: %s\n", iface.Name, iface.MTU, iface.HardwareAddr)
		for _, addr := range iface.Addrs {
			fmt.Printf("  Addr: %s\n", addr.Addr)
		}
	}
	fmt.Println()
}
```

---

### 🧪 What It Shows:

* CPU vendor, model, frequency, cores, and real-time usage.
* Total and used RAM.
* Disk partitions with usage percentage.
* Host OS, uptime, kernel arch.
* Network interface names, MAC addresses, IPs.

---

### 🔒 Note on Permissions

On Linux/macOS, some info (e.g., full disk or network details) may require elevated privileges. Run with `sudo` if needed.

Would you like me to help compile this into a binary or containerize it?
