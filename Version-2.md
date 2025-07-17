แนวทางออกแบบระบบเก็บข้อมูลสเปคคอมพิวเตอร์ด้วย Golang + PostgreSQL แบ่งเป็น 2 ส่วนหลักคือ **Server** และ **Agent** ดังนี้

---

## 1. สถาปัตยกรรมภาพรวม

* **Agent**: รันบนเครื่องลูกข่าย (PC, Laptop) ดึงข้อมูลสเปค (CPU, RAM, Disk, MAC address) ผ่านไลบรารีอย่าง [gopsutil](https://github.com/shirou/gopsutil) แล้วส่งไปยัง Server แบบ HTTP POST พร้อม Token
* **Server**: รับข้อมูลจาก Agent, เก็บลง PostgreSQL, ออก token ให้ Agent, มี Dashboard (UIkit) แสดงรายการอุปกรณ์และสเปคย้อนหลัง

```
┌──────────┐   HTTPS    ┌──────────┐
│  Agent   │──────────▶│  Server  │
│ (Go CLI) │◀──────────│ (Go/API) │
└──────────┘   HTTPS    └──────────┘
                     │
                     │  Dashboard (UIkit + Go html/template)
                     ▼
                 PostgreSQL
```

---

## 2. ฐานข้อมูล (PostgreSQL)

```sql
-- 2.1 ตารางผู้ใช้
CREATE TABLE users (
  id        SERIAL PRIMARY KEY,
  username  TEXT UNIQUE NOT NULL,
  full_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2.2 ตารางอุปกรณ์ (Device) ผูกกับผู้ใช้
CREATE TABLE devices (
  id         SERIAL PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name       TEXT NOT NULL,       -- ชื่อเครื่อง เช่น “office-pc01”
  token      TEXT UNIQUE NOT NULL,-- token สำหรับ Agent
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2.3 ตารางสเปค (Spec) เก็บเป็น snapshot แต่ละครั้ง
CREATE TABLE specs (
  id          SERIAL PRIMARY KEY,
  device_id   INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  cpu_model   TEXT,
  cpu_cores   INTEGER,
  ram_total   BIGINT,   -- byte
  disk_total  BIGINT,   -- byte (รวมทุก partition)
  disk_used   BIGINT,
  mac_address TEXT,
  collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

> **Tip**: ถ้าอยากเก็บข้อมูลละเอียดเพิ่มเติม (เช่นหลายดิสก์, หลาย NIC) ให้สร้างตาราง `disk_partitions` และ `network_interfaces` เชื่อม `specs.id` แทน

---

## 3. API Design (RESTful)

* **Authentication**: ใช้ HTTP Header `Authorization: Bearer <token>`
* **Endpoints**:

| Method | Path                    | คำอธิบาย                      |
| ------ | ----------------------- | ----------------------------- |
| POST   | /api/v1/register-device | ลงทะเบียนอุปกรณ์ (ต้อง Login) |
| POST   | /api/v1/specs           | รับ JSON สเปคจาก Agent        |
| GET    | /api/v1/devices         | คืนรายการอุปกรณ์ของผู้ใช้     |
| GET    | /api/v1/devices/{id}    | ข้อมูลอุปกรณ์ + สเปคย้อนหลัง  |

ตัวอย่าง request body `POST /api/v1/specs`:

```json
{
  "cpu_model": "Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz",
  "cpu_cores": 8,
  "ram_total": 17179869184,
  "disk_total": 512000000000,
  "disk_used": 128000000000,
  "mac_address": "00:1A:2B:3C:4D:5E"
}
```

---

## 4. ฝั่ง Server (Go)

### 4.1 โครงสร้างโฟลเดอร์

```
/server
  ├─ cmd/
  │   └─ server/
  │       └─ main.go
  ├─ internal/
  │   ├─ api/        — HTTP handlers
  │   ├─ auth/       — Token generation & middleware
  │   ├─ db/         — DB connection & model structs
  │   ├─ repository/ — CRUD กับ PostgreSQL (sqlx หรือ gorm)
  │   └─ web/        — html/templates + static (UIkit)
  ├─ config/         — อ่าน ENV vars (DB_URL, JWT_SECRET)
  └─ go.mod
```

### 4.2 ตัวอย่าง middleware สำหรับตรวจสอบ Token

```go
// auth/middleware.go
func TokenAuth(next http.Handler) http.Handler {
  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    auth := r.Header.Get("Authorization")
    parts := strings.Split(auth, " ")
    if len(parts) != 2 || parts[0] != "Bearer" {
      http.Error(w, "Unauthorized", http.StatusUnauthorized)
      return
    }
    token := parts[1]
    deviceID, err := validateToken(token)
    if err != nil {
      http.Error(w, "Invalid token", http.StatusUnauthorized)
      return
    }
    // ใส่ deviceID ลง context สำหรับ handler ถัดไป
    ctx := context.WithValue(r.Context(), "device_id", deviceID)
    next.ServeHTTP(w, r.WithContext(ctx))
  })
}
```

### 4.3 ตัวอย่าง handler รับ Specs

```go
// api/specs.go
func PostSpecs(w http.ResponseWriter, r *http.Request) {
  deviceID := r.Context().Value("device_id").(int)

  var spec SpecInput
  if err := json.NewDecoder(r.Body).Decode(&spec); err != nil {
    http.Error(w, "Bad Request", http.StatusBadRequest)
    return
  }

  // แปลงและบันทึกลง DB
  err := repository.SaveSpec(deviceID, spec)
  if err != nil {
    http.Error(w, "Internal Server Error", http.StatusInternalServerError)
    return
  }
  w.WriteHeader(http.StatusCreated)
}
```

### 4.4 Dashboard (UIkit + Go html/template)

* **static/**: เก็บไฟล์ CSS/JS UIkit
* **templates/**: ไฟล์ `.html` ใช้ syntax ของ Go `{{ .Devices }}`
* ตัวอย่าง snippet:

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="/static/css/uikit.min.css" />
</head>
<body>
  <div class="uk-container">
    <h1>Dashboard</h1>
    <table class="uk-table uk-table-divider">
      <thead>
        <tr><th>Device</th><th>Last Seen</th><th>CPU</th><th>RAM (GB)</th></tr>
      </tr></thead>
      <tbody>
        {{ range .Devices }}
        <tr>
          <td>{{ .Name }}</td>
          <td>{{ .LastSpec.CollectedAt }}</td>
          <td>{{ .LastSpec.CPUModel }}</td>
          <td>{{ printf "%.2f" (float64 .LastSpec.RAMTotal / (1<<30)) }}</td>
        </tr>
        {{ end }}
      </tbody>
    </table>
  </div>
  <script src="/static/js/uikit.min.js"></script>
  <script src="/static/js/uikit-icons.min.js"></script>
</body>
</html>
```

---

## 5. ฝั่ง Agent (Go CLI)

### 5.1 โครงสร้างโฟลเดอร์

```
/agent
  ├─ main.go
  └─ go.mod
```

### 5.2 ดึงสเปคด้วย gopsutil

```go
// main.go
package main

import (
  "bytes"
  "encoding/json"
  "flag"
  "fmt"
  "net/http"
  "os"
  "github.com/shirou/gopsutil/cpu"
  "github.com/shirou/gopsutil/disk"
  "github.com/shirou/gopsutil/mem"
  "github.com/shirou/gopsutil/net"
)

type Spec struct {
  CPUModel   string `json:"cpu_model"`
  CPUCores   int    `json:"cpu_cores"`
  RAMTotal   uint64 `json:"ram_total"`
  DiskTotal  uint64 `json:"disk_total"`
  DiskUsed   uint64 `json:"disk_used"`
  MACAddress string `json:"mac_address"`
}

func main() {
  flag.Usage = func() {
    fmt.Println("Usage: agent [serverURL] [token]")
  }
  flag.Parse()
  if len(flag.Args()) != 2 {
    flag.Usage()
    os.Exit(1)
  }
  serverURL, token := flag.Args()[0], flag.Args()[1]

  // ดึงข้อมูล
  cpuInfo, _ := cpu.Info()
  cores, _ := cpu.Counts(true)
  vm, _ := mem.VirtualMemory()
  parts, _ := disk.Partitions(false)
  var total, used uint64
  for _, p := range parts {
    du, _ := disk.Usage(p.Mountpoint)
    total += du.Total
    used += du.Used
  }
  ifcs, _ := net.Interfaces()
  mac := ifcs[0].HardwareAddr.String() // เลือกอันแรก

  spec := Spec{
    CPUModel:   cpuInfo[0].ModelName,
    CPUCores:   cores,
    RAMTotal:   vm.Total,
    DiskTotal:  total,
    DiskUsed:   used,
    MACAddress: mac,
  }
  body, _ := json.Marshal(spec)
  req, _ := http.NewRequest("POST", serverURL+"/api/v1/specs", bytes.NewBuffer(body))
  req.Header.Set("Content-Type", "application/json")
  req.Header.Set("Authorization", "Bearer "+token)

  resp, err := http.DefaultClient.Do(req)
  if err != nil {
    fmt.Println("Error sending:", err)
    os.Exit(1)
  }
  defer resp.Body.Close()
  if resp.StatusCode != http.StatusCreated {
    fmt.Println("Server returned:", resp.Status)
    os.Exit(1)
  }
  fmt.Println("Spec sent successfully.")
}
```

* คอมไพล์:

  ```bash
  cd agent
  go build -o agent
  ```
* รัน:

  ```bash
  ./agent https://your-server.example.com YOUR_TOKEN_HERE
  ```

---

## 6. สรุป

1. **Database**: ออกแบบตาราง `users` → `devices` → `specs`
2. **Server**:

   * ออก API รับ/ออก token, รับสเปค
   * ใช้ middleware ตรวจ auth
   * Dashboard ใช้ Go html/template + UIkit
3. **Agent**:

   * ดึงสเปคด้วย gopsutil
   * ส่ง POST พร้อม Bearer token
4. **Deployment**:

   * เซ็ต ENV: `DATABASE_URL`, `JWT_SECRET`
   * รัน Server และคอมไพล์ Agent กระจายไปตามเครื่อง

ด้วยโครงสร้างนี้จะขยายฟีเจอร์ (เช่น เก็บประวัติสเปค, กราฟย้อนหลัง, เพิ่มโมดูลทำ heartbeat) ได้ง่าย และแยกความรับผิดชอบระหว่าง Server กับ Agent อย่างชัดเจนครับ!
