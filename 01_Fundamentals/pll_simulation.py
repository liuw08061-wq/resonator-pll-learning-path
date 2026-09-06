#!/usr/bin/env python3
"""
第一阶段：PLL 原理仿真

完整的数字锁相环（Phase-Locked Loop）实现
用于 145kHz 谐振传感器的频率追踪

PLL 组成：
1. NCO (数控振荡器) - 生成参考信号
2. 相位检测器 - 计算相位误差
3. 环路滤波器 - PI 控制器
4. 反馈路径 - 闭环控制
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sp_signal


# ============================================================================
# PLL 核心组件
# ============================================================================

class DigitalNCO:
    """数控振荡器 (Numerically Controlled Oscillator)"""
    
    def __init__(self, initial_freq, sample_rate):
        """
        参数:
            initial_freq: 初始频率 (Hz)
            sample_rate: 采样率 (Hz)
        """
        self.fs = sample_rate
        self.phase = 0
        self.freq = initial_freq
        self.freq_word = self._freq_to_word(initial_freq)
        self.freq_history = []
        self.phase_history = []
    
    def _freq_to_word(self, freq):
        """将频率转换为频率字 (32-bit)"""
        # freq_word = freq * (2^32 / fs)
        return int(freq * (2**32 / self.fs))
    
    def update_frequency(self, freq):
        """更新 NCO 频率"""
        self.freq = freq
        self.freq_word = self._freq_to_word(freq)
        self.freq_history.append(freq)
    
    def generate_samples(self, num_samples):
        """生成 NCO 输出"""
        sin_out = np.zeros(num_samples)
        cos_out = np.zeros(num_samples)
        
        for i in range(num_samples):
            # 获取 sin/cos
            sin_out[i] = np.sin(self.phase)
            cos_out[i] = np.cos(self.phase)
            self.phase_history.append(self.phase)
            
            # 相位累加
            self.phase += 2 * np.pi * self.freq / self.fs
            
            # 相位环绕 (-π 到 π)
            if self.phase > np.pi:
                self.phase -= 2 * np.pi
            elif self.phase < -np.pi:
                self.phase += 2 * np.pi
        
        return sin_out, cos_out


class PhaseDetector:
    """相位检测器"""
    
    @staticmethod
    def detect(input_signal, nco_sin, nco_cos):
        """
        相位检测：采用 atan2 方法
        计算输入信号与 NCO 参考信号的相位差
        """
        # I/Q 混频
        i_component = input_signal * nco_cos
        q_component = input_signal * nco_sin
        
        # 相位误差 = atan2(Q, I)
        phase_error = np.arctan2(q_component, i_component)
        
        return phase_error, i_component, q_component


class LoopFilter:
    """环路滤波器 (PI 控制器)"""
    
    def __init__(self, kp, ki):
        """
        参数:
            kp: 比例增益
            ki: 积分增益
        """
        self.kp = kp
        self.ki = ki
        self.integrator = 0
        self.freq_update_history = []
    
    def update(self, phase_error):
        """
        PI 控制器：
        freq_update = Kp * error + Ki * integral(error)
        """
        # 积分项更新
        self.integrator += phase_error
        
        # 限制积分值（防止积分饱和）
        self.integrator = np.clip(self.integrator, -10, 10)
        
        # 计算频率更新
        freq_update = self.kp * phase_error + self.ki * self.integrator
        self.freq_update_history.append(freq_update)
        
        return freq_update


class DigitalPLL:
    """完整的数字锁相环"""
    
    def __init__(self, target_freq, sample_rate, kp, ki):
        """
        参数:
            target_freq: 目标频率 (Hz)
            sample_rate: 采样率 (Hz)
            kp: 比例增益
            ki: 积分增益
        """
        self.target_freq = target_freq
        self.fs = sample_rate
        
        # 初始化各模块
        self.nco = DigitalNCO(target_freq, sample_rate)
        self.pd = PhaseDetector()
        self.loop_filter = LoopFilter(kp, ki)
        
        # 历史记录
        self.freq_estimate = [target_freq]
        self.phase_error_history = []
        self.i_component_history = []
        self.q_component_history = []
        self.locked = False
        self.lock_counter = 0
    
    def step(self, input_sample):
        """执行一个 PLL 步"""
        
        # 1. NCO 生成参考信号
        sin_ref = np.sin(self.nco.phase)
        cos_ref = np.cos(self.nco.phase)
        
        # 2. 相位检测
        phase_error, i_comp, q_comp = self.pd.detect(
            input_sample, sin_ref, cos_ref
        )
        
        # 3. 环路滤波
        freq_update = self.loop_filter.update(phase_error)
        
        # 4. 更新 NCO 频率
        new_freq = self.nco.freq + freq_update
        self.nco.update_frequency(new_freq)
        
        # 5. 更新相位累加器
        self.nco.phase += 2 * np.pi * self.nco.freq / self.fs
        
        # 相位环绕
        while self.nco.phase > np.pi:
            self.nco.phase -= 2 * np.pi
        while self.nco.phase < -np.pi:
            self.nco.phase += 2 * np.pi
        
        # 记录历史
        self.freq_estimate.append(self.nco.freq)
        self.phase_error_history.append(phase_error)
        self.i_component_history.append(i_comp)
        self.q_component_history.append(q_comp)
        
        # 6. 锁定检测
        if abs(phase_error) < 0.1:  # < 5.7°
            self.lock_counter += 1
            if self.lock_counter > 100:
                self.locked = True
        else:
            self.lock_counter = 0
            self.locked = False
        
        return {
            'phase_error': phase_error,
            'freq_estimate': self.nco.freq,
            'i_component': i_comp,
            'q_component': q_comp,
            'amplitude': np.sqrt(i_comp**2 + q_comp**2),
            'locked': self.locked
        }
    
    def run(self, input_signal):
        """运行 PLL"""
        results = []
        for sample in input_signal:
            result = self.step(sample)
            results.append(result)
        return results


# ============================================================================
# 仿真场景
# ============================================================================

def test_basic_tracking():
    """测试 1：基本频率追踪"""
    print("\n" + "="*70)
    print("测试 1: 基本频率追踪 (145 kHz)")
    print("="*70)
    
    # 参数
    fs = 125e6          # Red Pitaya 采样率
    f_target = 145e3    # 目标频率
    duration = 1e-3     # 1 ms
    
    # PLL 参数（需要调优）
    kp = 100
    ki = 10
    
    # 生成输入信号（无频率偏差）
    t = np.arange(0, duration, 1/fs)
    input_signal = np.sin(2*np.pi*f_target*t)
    
    # 创建 PLL
    pll = DigitalPLL(f_target, fs, kp, ki)
    
    # 运行 PLL
    results = pll.run(input_signal)
    
    # 统计
    freq_estimates = [r['freq_estimate'] for r in results]
    phase_errors = [r['phase_error'] for r in results]
    
    final_freq = freq_estimates[-1]
    freq_error = abs(final_freq - f_target)
    
    print(f"目标频率: {f_target/1e3:.1f} kHz")
    print(f"最终估计: {final_freq/1e3:.6f} kHz")
    print(f"频率误差: {freq_error:.2f} Hz")
    print(f"PLL 锁定: {pll.locked}")
    print(f"平均相位误差: {np.mean(np.abs(phase_errors)):.4f} rad")
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    
    samples = np.arange(len(results))
    
    # 频率追踪
    axes[0].plot(samples[::100], np.array(freq_estimates)[::100]/1e3, 'b-o', markersize=3)
    axes[0].axhline(y=f_target/1e3, color='r', linestyle='--', label='目标频率')
    axes[0].set_ylabel('频率 (kHz)')
    axes[0].set_title('测试 1: 频率追踪')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 相位误差
    axes[1].plot(samples[::100], np.array(phase_errors)[::100], 'g-o', markersize=3)
    axes[1].set_ylabel('相位误差 (rad)')
    axes[1].set_title('相位误差收敛')
    axes[1].grid(True, alpha=0.3)
    
    # I/Q 轨迹
    i_components = [r['i_component'] for r in results]
    q_components = [r['q_component'] for r in results]
    axes[2].plot(i_components[::100], q_components[::100], 'b.-')
    axes[2].set_xlabel('I 分量')
    axes[2].set_ylabel('Q 分量')
    axes[2].set_title('I/Q 轨迹（星座图）')
    axes[2].axis('equal')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test1_basic_tracking.png', dpi=100)
    print("图表已保存: test1_basic_tracking.png\n")
    plt.close()


def test_frequency_step():
    """测试 2：频率跳跃响应"""
    print("="*70)
    print("测试 2: 频率跳跃响应")
    print("="*70)
    
    # 参数
    fs = 125e6
    f_initial = 145e3
    f_target = 145.5e3  # 0.5 kHz 跳跃
    duration = 2e-3
    
    kp = 100
    ki = 10
    
    # 生成信号（前 1ms 是 145 kHz，后 1ms 是 145.5 kHz）
    t = np.arange(0, duration, 1/fs)
    jump_idx = int(duration/2 * fs)
    
    input_signal = np.zeros(len(t))
    input_signal[:jump_idx] = np.sin(2*np.pi*f_initial*t[:jump_idx])
    input_signal[jump_idx:] = np.sin(2*np.pi*f_target*t[jump_idx:])
    
    # 创建 PLL
    pll = DigitalPLL(f_initial, fs, kp, ki)
    results = pll.run(input_signal)
    
    # 统计
    freq_estimates = [r['freq_estimate'] for r in results]
    
    print(f"初始频率: {f_initial/1e3:.1f} kHz")
    print(f"跳跃至: {f_target/1e3:.1f} kHz (在样本 {jump_idx})")
    print(f"最终估计: {freq_estimates[-1]/1e3:.6f} kHz")
    
    # 计算锁定时间
    lock_time_idx = jump_idx
    for i in range(jump_idx, len(results)):
        if results[i]['locked']:
            lock_time_idx = i
            break
    lock_time = (lock_time_idx - jump_idx) / fs * 1e6
    
    print(f"锁定时间: {lock_time:.1f} μs")
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 6))
    
    samples = np.arange(len(results))
    axes[0].plot(samples[::1000]/fs*1e3, np.array(freq_estimates)[::1000]/1e3, 'b-o', markersize=3)
    axes[0].axvline(x=1, color='r', linestyle='--', alpha=0.5)
    axes[0].set_ylabel('频率 (kHz)')
    axes[0].set_title('测试 2: 频率跳跃响应')
    axes[0].grid(True, alpha=0.3)
    
    # 放大视图（跳跃前后）
    zoom_start = jump_idx - int(100e-6*fs)
    zoom_end = jump_idx + int(500e-6*fs)
    axes[1].plot(samples[zoom_start:zoom_end]/fs*1e6, 
                np.array(freq_estimates)[zoom_start:zoom_end]/1e3, 'b-o', markersize=2)
    axes[1].axvline(x=1000, color='r', linestyle='--', alpha=0.5, label='频率跳跃')
    axes[1].set_xlabel('时间 (μs, 相对跳跃点)')
    axes[1].set_ylabel('频率 (kHz)')
    axes[1].set_title('放大视图：锁定瞬间')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test2_frequency_step.png', dpi=100)
    print("图表已保存: test2_frequency_step.png\n")
    plt.close()


def test_noisy_signal():
    """测试 3：噪声抗扰"""
    print("="*70)
    print("测试 3: 噪声抗扰")
    print("="*70)
    
    # 参数
    fs = 125e6
    f_target = 145e3
    duration = 1e-3
    snr_db = 20  # 信噪比
    
    kp = 100
    ki = 10
    
    # 生成信号
    t = np.arange(0, duration, 1/fs)
    signal_clean = np.sin(2*np.pi*f_target*t)
    
    # 添加噪声
    noise_power = 10**(-snr_db/10)
    noise = np.sqrt(noise_power) * np.random.randn(len(t))
    input_signal = signal_clean + noise
    
    # 创建 PLL
    pll = DigitalPLL(f_target, fs, kp, ki)
    results = pll.run(input_signal)
    
    # 统计
    freq_estimates = [r['freq_estimate'] for r in results]
    freq_error = np.std(np.array(freq_estimates)[int(len(results)*0.5):] - f_target)
    
    print(f"目标频率: {f_target/1e3:.1f} kHz")
    print(f"信噪比: {snr_db} dB")
    print(f"频率估计标准差: {freq_error:.2f} Hz")
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 6))
    
    samples = np.arange(len(results))
    idx = int(duration * fs / 20)  # 显示 5%
    
    axes[0].plot(samples[:idx]/fs*1e6, input_signal[:idx], 'b-', linewidth=0.5, alpha=0.7, label='输入信号')
    axes[0].plot(samples[:idx]/fs*1e6, signal_clean[:idx], 'r-', linewidth=1, alpha=0.7, label='清洁信号')
    axes[0].set_ylabel('幅度')
    axes[0].set_title('测试 3: 噪声信号')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(samples[::1000]/fs*1e3, np.array(freq_estimates)[::1000]/1e3, 'g-o', markersize=3)
    axes[1].axhline(y=f_target/1e3, color='r', linestyle='--', label='目标频率')
    axes[1].set_xlabel('时间 (ms)')
    axes[1].set_ylabel('频率 (kHz)')
    axes[1].set_title(f'PLL 频率追踪 (SNR={snr_db}dB)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test3_noisy_signal.png', dpi=100)
    print("图表已保存: test3_noisy_signal.png\n")
    plt.close()


# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    print("\n" + "🎓 数字锁相环 (PLL) 仿真" + "\n")
    print("本程序演示 145kHz 谐振传感器所需的 PLL 原理\n")
    
    # 运行所有测试
    test_basic_tracking()
    test_frequency_step()
    test_noisy_signal()
    
    print("="*70)
    print("✓ 所有仿真测试完成！")
    print("="*70)
    print("\n生成的图表:")
    print("  test1_basic_tracking.png    - 基本频率追踪")
    print("  test2_frequency_step.png    - 频率跳跃响应")
    print("  test3_noisy_signal.png      - 噪声抗扰")
    print("\n关键参数调优:")
    print("  Kp (比例增益)   - 控制快速响应，值过大会振荡")
    print("  Ki (积分增益)   - 消除稳态误差，值过大会导致锁定困难")
    print("  推荐从小值开始：Kp=1, Ki=0.1，然后逐步增加")
    print("\n下一步学习:")
    print("  → 进入 02_Tools_Hardware 学习 Vivado 和 Verilog")
