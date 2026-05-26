import torch
import torch.nn as nn
from py_interface import Ns3AIRLBase


# 1.  LAAVHA 神经网络架构
class LAAVHAPredictor(nn.Module):
    def __init__(self):
        super(LAAVHAPredictor, self).__init__()
        # 堆叠 LSTM 层：处理 15 维网络特征
        self.lstm1 = nn.LSTM(input_size=15, hidden_size=128, batch_first=True)
        self.lstm2 = nn.LSTM(input_size=128, hidden_size=64, batch_first=True)
        # 多头注意力机制：根据场景动态分配权重
        self.attention = nn.MultiheadAttention(embed_dim=64, num_heads=4, batch_first=True)
        # 融合层：整合速度与高度特征
        self.fc_mob = nn.Linear(2, 64)
        self.fc_pred = nn.Linear(64, 3)  # 输出 3 类：5G, LTE, WiFi

    def forward(self, x, mob):
        # x shape: (1, 10, 15) -> 10步历史，15维特征
        out, _ = self.lstm1(x)
        out, _ = self.lstm2(out)
        # 运行 Attention 提取核心特征
        attn_out, attn_weights = self.attention(out, out, out)
        context = attn_out[:, -1, :]  # 取序列最后一个状态
        # 融合无人机移动特征
        combined = context + torch.relu(self.fc_mob(mob))
        return self.fc_pred(combined), attn_weights


# 2. 核心交互类：实现 ns3-ai 的双向通信逻辑
class LAAVHAInferenceServer(Ns3AIRLBase):
    def __init__(self):
        # 绑定共享内存 ID 1234，与 C++ 端匹配
        super().__init__(1234)
        self.model = LAAVHAPredictor()
        self.model.load_state_dict(torch.load("laavha_model_final.pth"))
        #self.model.load_state_dict(torch.load("laavha_no_lstm_model.pth"))
        self.model.eval()
        self.history_window = []  # 用于存储历史 10 步的时序数据

    def do_action(self, obs):
        """
        【关键函数】： C++ 调用 m_aiInterface->Predict() 时，此函数被触发
        """
        # A. 接收逻辑：从 obs 字典中提取 C++ 传来的 15 维物理层指标
        raw_metrics = obs['metrics']  # 长度为 15 的数组[cite: 5]
        uav_state = [obs['velocity'], obs['altitude']]

        # B. 数据预处理：维护滑动窗口以满足 LSTM 的时序输入要求 (T=10)
        self.history_window.append(ra
        // --- LTE 网络状态采集 ---
        statw_metrics)
        if len(self.history_window) > 10:
            self.history_window.pop(0)

        if len(self.history_window) < 10:
            return  0  # 数据不足时保持当前网络

        # 转换为张量
        input_tensor = torch.FloatTensor(self.history_window).unsqueeze(0)  # (1, 10, 15)
        mob_tensor = torch.FloatTensor(uav_state).unsqueeze(0)

        # C. 推理逻辑：利用训练好的模型进行最优接入网络预测
        with torch.no_grad():
            prediction, weights = self.model(input_tensor, mob_tensor)
            decision = torch.argmax(prediction).item()

        # D. 回传逻辑：将决策结果 (0, 1, 2) 封装成字典写回共享内存
        # C++ 端的 m_aiInterface->Predict() 会立即收到此结果并继续运行
        return int(decision)


if __name__ == "__main__":
    print("=" * 60)
    print("LAAVHA 垂直切换推理服务端 - 已启动")
    print("正在通过共享内存接口监听 ns-3 仿真数据...")
    print("=" * 60)
    print("服务端已进入实时静默计算状态，仿真完成后关闭。")
    server = LAAVHAInferenceServer()
    server.run()  # 开始循环监听共享内存