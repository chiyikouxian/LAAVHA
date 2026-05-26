import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import pandas as pd
import numpy as np


# 1. 数据集加载类 (保持与之前一致)
class HandoverDataset(Dataset):
    def __init__(self, csv_file):
        df = pd.read_csv(csv_file)
        self.X_status = df.iloc[:, :150].values.reshape(-1, 3, 10, 5).astype(np.float32)
        self.X_mobility = df[['Velocity', 'Altitude']].values.astype(np.float32)
        self.Y_target = df.iloc[:, 152:167].values.reshape(-1, 3, 5).astype(np.float32)

    def __len__(self): return len(self.X_status)

    def __getitem__(self, idx):
        return (torch.from_numpy(self.X_status[idx]),
                torch.from_numpy(self.X_mobility[idx]),
                torch.from_numpy(self.Y_target[idx]))


# 2. LAAVHA 模型定义 (对应论文第三章架构)
class LAAVHA_Net(nn.Module):
    def __init__(self):
        super(LAAVHA_Net, self).__init__()
        # 堆叠 LSTM 模块
        self.lstm1 = nn.LSTM(5, 128, batch_first=True)
        self.lstm2 = nn.LSTM(128, 64, batch_first=True)
        self.fc_pred = nn.Linear(64, 5)
        # 注意力机制模块
        self.attention = nn.MultiheadAttention(embed_dim=5, num_heads=1, batch_first=True)
        self.fc_mob = nn.Linear(2, 16)
        self.fc_weight = nn.Linear(5 + 16, 5)

    def forward(self, x_status, x_mob):
        # 预测分支
        preds = []
        for i in range(3):
            out, _ = self.lstm1(x_status[:, i, :, :])
            out, _ = self.lstm2(out)
            preds.append(self.fc_pred(out[:, -1, :]))
        S_pred = torch.stack(preds, dim=1)
        # 权重分支
        S_cur = x_status[:, :, -1, :]
        attn_out, _ = self.attention(S_cur, S_cur, S_cur)
        combined = torch.cat([torch.mean(attn_out, dim=1), torch.relu(self.fc_mob(x_mob))], dim=1)
        weights = torch.softmax(self.fc_weight(combined), dim=1)
        return S_pred, weights


# 3. 训练函数
def run_training():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 划分数据集：8000条训练，2000条验证
    dataset = HandoverDataset('LAAVHA_Training_Dataset.csv')
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False)

    model = LAAVHA_Net().to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()  # 均方误差损失

    for epoch in range(50):
        model.train()
        train_loss = 0
        for b_status, b_mob, b_target in train_loader:
            b_status, b_mob, b_target = b_status.to(device), b_mob.to(device), b_target.to(device)
            optimizer.zero_grad()
            S_pred, _ = model(b_status, b_mob)
            loss = criterion(S_pred, b_target)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # 每轮训练完，在验证集上测准确度
        model.eval()
        val_loss = 0
        mae_list = []  # 存储平均绝对误差
        with torch.no_grad():
            for b_status, b_mob, b_target in val_loader:
                b_status, b_mob, b_target = b_status.to(device), b_mob.to(device), b_target.to(device)
                S_pred, _ = model(b_status, b_mob)

                # 计算误差
                v_loss = criterion(S_pred, b_target)
                val_loss += v_loss.item()

                # 核心：计算预测精度 (1 - 平均相对误差)
                relative_error = torch.abs(S_pred - b_target) / (torch.abs(b_target) + 1e-6)
                mae_list.append(torch.mean(relative_error).item())

        # 精度展示：1 - 平均误差百分比
        final_accuracy = (1 - np.mean(mae_list)) * 100
        print(
            f"Epoch {epoch + 1:02d}/50 | Loss: {train_loss / len(train_loader):.6f} | Val Accuracy: {final_accuracy:.2f}%")

    torch.save(model.state_dict(), 'laavha_model_final.pth')
    print("训练结束，最优模型已保存。")


if __name__ == "__main__":
    run_training()