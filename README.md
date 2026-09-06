# 145kHz 谐振传感器 PLL 追踪系统

## 项目目标

利用 **Red Pitaya STEMlab 125-14** 开发板实现 145kHz 谐振式传感器的**频率追踪 PLL 系统**（FPGA 混合方案）

---

## 📚 学习路线

### 第一阶段：基础知识（1-2周）
- [x] 信号处理基础（采样定理、I/Q采样、频域分析）
- [x] PLL 原理（NCO、相位检测、PI控制）

### 第二阶段：工具和硬件（1-2周）
- [ ] Vivado 基础
- [ ] Verilog RTL 设计
- [ ] Red Pitaya 硬件操作

### 第三阶段：核心模块设计（2-3周）
- [ ] NCO 数控振荡器
- [ ] 混频器和相位检测
- [ ] CIC 低通滤波器

### 第四阶段：系统集成（2-3周）
- [ ] FPGA 全系统设计
- [ ] ARM 软件集成
- [ ] 测试和验证

---

## 📁 项目结构

```
resonator-pll-learning-path/
├── 01_Fundamentals/           # 第一阶段：基础知识
│   ├── signal_processing_basics.py
│   ├── pll_simulation.py
│   └── notes.md
│
├── 02_Tools_Hardware/         # 第二阶段：工具和硬件
│   ├── vivado_setup.tcl
│   ├── verilog_tutorial.v
│   └── redpitaya_scpi_demo.py
│
├── 03_FPGA_Modules/           # 第三阶段：核心模块
│   ├── nco/
│   │   ├── nco.v
│   │   └── nco_tb.v
│   ├── mixer/
│   │   └── mixer.v
│   └── cic_filter/
│       └── cic_filter.v
│
├── 04_System_Integration/     # 第四阶段：系统集成
│   ├── resonator_tracker.v    # FPGA 顶层
│   ├── arm_controller.py      # ARM 控制程序
│   └── vivado_project.tcl     # 完整工程配置
│
├── docs/                      # 文档
│   ├── system_design.md
│   ├── pll_theory.md
│   ├── hardware_setup.md
│   └── testing_guide.md
│
├── resources/                 # 学习资源链接
│   ├── free_online_resources.md
│   ├── book_references.md
│   └── video_tutorials.md
│
└── README.md

```

---

## 🎯 系统架构

```
谐振传感器 (145kHz)
     ↓
 ┌─────────────────────────────────────┐
 │   Red Pitaya FPGA (实时处理)         │
 │  ┌─────────────────────────────────┤
 │  │ ADC → NCO → 混频 → CIC滤波      │
 │  │ ↓                              │
 │  │ I/Q 输出 (10 kSPS)             │
 │  └─────────────────────────────────┤
 │                                   │
 │   Red Pitaya ARM CPU (控制)        │
 │  ┌─────────────────────────────────┤
 │  │ 读取 I/Q → PLL PI控制 → 更新频率 │
 │  └─────────────────────────────────┤
 └─────────────────────────────────────┘
     ↓
 USB/Ethernet → 用户应用
```

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/liuw08061-wq/resonator-pll-learning-path.git
cd resonator-pll-learning-path
```

### 2. 安装依赖
```bash
pip install numpy matplotlib scipy
```

### 3. 运行第一个示例
```bash
cd 01_Fundamentals
python pll_simulation.py
```

### 4. 阅读文档
- 从 `docs/system_design.md` 开始
- 按顺序学习每个阶段

---

## 📋 学习时间表

| 阶段 | 内容 | 时间 | 预期完成日期 |
|------|------|------|------------|
| 第一阶段 | 基础知识 | 1-2周 | - |
| 第二阶段 | 工具和硬件 | 1-2周 | - |
| 第三阶段 | 核心模块 | 2-3周 | - |
| 第四阶段 | 系统集成 | 2-3周 | - |
| **总计** | **完整系统** | **8-12周** | - |

---

## 🔗 重要资源

### 官方文档
- [Red Pitaya 文档](https://redpitaya.readthedocs.io/)
- [Pavel Demin SDR 项目](https://pavel-demin.github.io/red-pitaya-notes/)
- [Xilinx Vivado](https://www.xilinx.com/support/documentation/sw_manuals/xilinx2022_1/ug910-vivado-getting-started.pdf)

### 在线教程
- [PySDR - 信号处理](https://pysdr.org/)
- [ChipVerify - Verilog 教程](https://www.chipverify.com/verilog)

### 硬件规格
- ADC 采样率：125 MS/s
- ADC 分辨率：14-bit
- 输入范围：±1V
- FPGA：Xilinx Zynq 7010

---

## 💡 核心技能清单

### 必须掌握
- [ ] 采样定理和 I/Q 采样原理
- [ ] PLL 工作原理和设计方法
- [ ] Verilog RTL 基础语法
- [ ] Vivado FPGA 设计流程
- [ ] Red Pitaya SCPI 命令

### 重要技能
- [ ] 信号处理算法（滤波、FFT）
- [ ] FPGA 时序设计
- [ ] ARM 嵌入式编程
- [ ] 硬件调试和验证

### 可选技能
- [ ] MATLAB/Simulink
- [ ] 模型仿真
- [ ] PCB 设计

---

## 📞 寻求帮助

遇到问题？
1. 检查 `docs/` 中的常见问题
2. 查看代码注释和示例
3. 参考官方文档
4. 提交 Issue 讨论

---

## 📄 许可证

MIT License - 自由使用和修改

---

**开始学习：** 
1. 进入 `01_Fundamentals/` 目录
2. 按顺序完成每个练习
3. 记录学习笔记
4. 持续迭代改进

祝学习愉快！🚀
