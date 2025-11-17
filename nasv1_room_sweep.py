# sweep_nn_fixed.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import time

# -------------------------------------------------
# 1. GROUND-TRUTH FUNCTION (MUST BE BEFORE DATA!)
# -------------------------------------------------
def sweep_time_gt(area, vis, p_halt, clutter, redundancy=False):
    r = 0.05 + 0.30 * vis
    base = area / r * clutter
    comm = 120 * p_halt
    overhead = 15 + 0.5 * (area**0.5) * (clutter - 1)
    t = base + comm + overhead
    if redundancy:
        t *= 1.30
    return t

# -------------------------------------------------
# 2. DEVICE
# -------------------------------------------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# -------------------------------------------------
# 3. SYNTHETIC DATA
# -------------------------------------------------
np.random.seed(42)
N = 12000

area    = np.random.uniform(5, 120, N).astype(np.float32)
vis     = np.random.uniform(0, 1, N).astype(np.float32)
p_halt  = np.random.uniform(0, 0.5, N).astype(np.float32)
clutter = np.random.uniform(1.0, 2.0, N).astype(np.float32)

redundancy = np.random.rand(N) < 0.3

time_gt = np.zeros(N, dtype=np.float32)
for i in range(N):
    time_gt[i] = sweep_time_gt(area[i], vis[i], p_halt[i], clutter[i],
                               redundancy=redundancy[i])

time_gt += np.random.normal(0, 4, N).astype(np.float32)   # noise

# -------------------------------------------------
# 4. MANUAL NORMALIZATION (no sklearn)
# -------------------------------------------------
def normalize(x):
    mean = x.mean(axis=0, keepdims=True)
    std  = x.std(axis=0, keepdims=True) + 1e-8
    return (x - mean) / std, mean, std

X = np.column_stack((area, vis, p_halt, clutter))
X_norm, X_mean, X_std = normalize(X)
y_norm, y_mean, y_std = normalize(time_gt.reshape(-1,1))

# -------------------------------------------------
# 5. TRAIN / VAL SPLIT
# -------------------------------------------------
idx = np.random.permutation(N)
train_idx = idx[:int(0.8*N)]
val_idx   = idx[int(0.8*N):]

X_train = torch.from_numpy(X_norm[train_idx]).to(device)
y_train = torch.from_numpy(y_norm[train_idx]).to(device)
X_val   = torch.from_numpy(X_norm[val_idx]).to(device)
y_val   = torch.from_numpy(y_norm[val_idx]).to(device)

# -------------------------------------------------
# 6. DATASET & DATALOADER
# -------------------------------------------------
class SweepDataset(torch.utils.data.Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y
    def __len__(self): return len(self.X)
    def __getitem__(self, i): return self.X[i], self.y[i]

BATCH = 256
train_loader = torch.utils.data.DataLoader(SweepDataset(X_train, y_train),
                                           batch_size=BATCH, shuffle=True)
val_loader   = torch.utils.data.DataLoader(SweepDataset(X_val,   y_val),
                                           batch_size=BATCH, shuffle=False)

# -------------------------------------------------
# 7. NEURAL NETWORK
# -------------------------------------------------
class SweepNet(nn.Module):
    def __init__(self, hidden_sizes):
        super().__init__()
        layers = []
        prev = 4
        for h in hidden_sizes:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.ReLU())
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)
    def forward(self, x): return self.net(x)

# -------------------------------------------------
# 8. TRAINING HELPERS
# -------------------------------------------------
def train_one_epoch(model, opt):
    model.train()
    total = 0.0
    for xb, yb in train_loader:
        opt.zero_grad()
        loss = nn.MSELoss()(model(xb), yb)
        loss.backward()
        opt.step()
        total += loss.item() * xb.size(0)
    return total / len(train_loader.dataset)

@torch.no_grad()
def validate(model):
    model.eval()
    total = 0.0
    for xb, yb in val_loader:
        loss = nn.MSELoss()(model(xb), yb)
        total += loss.item() * xb.size(0)
    return total / len(val_loader.dataset)

# -------------------------------------------------
# 9. NAS
# -------------------------------------------------
search = {'layers':[1,2,3], 'sizes':[32,64,128,256]}
best_mse, best_cfg, best_state = float('inf'), None, None

print("\n=== NAS START ===")
for nl in search['layers']:
    for sz in search['sizes']:
        cfg = [sz] * nl
        print(f"Testing {cfg}", end=' ')
        model = SweepNet(cfg).to(device)
        opt   = optim.Adam(model.parameters(), lr=3e-3)
        for _ in range(60):
            train_one_epoch(model, opt)
        mse = validate(model)
        print(f"→ {mse:.6f}")
        if mse < best_mse:
            best_mse, best_cfg, best_state = mse, cfg, model.state_dict()
            print(" **BEST**")

print(f"\nBEST: {best_cfg} | MSE: {best_mse:.6f}")

# -------------------------------------------------
# 10. PREDICTION FUNCTION
# -------------------------------------------------
def predict_sweep_time(area, vis, p_halt, clutter):
    model = SweepNet(best_cfg).to(device)
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        x = np.array([[area, vis, p_halt, clutter]], dtype=np.float32)
        x = (x - X_mean) / X_std
        x_t = torch.from_numpy(x).to(device)
        y_n = model(x_t).cpu().numpy()
        return float(y_n[0,0] * y_std + y_mean)

# -------------------------------------------------
# 11. DEMO
# -------------------------------------------------
print("\n--- Demo ---")
for a,v,p,c in [(345,0.0,0.1,1.0), (25,0.6,0.2,1.5), (80,0.0,0.4,1.8)]:
    print(f"{a:3} m², v={v:.1f}, p_h={p:.2f}, c={c:.1f} → {predict_sweep_time(a,v,p,c):.1f} s")