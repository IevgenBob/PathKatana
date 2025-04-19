# Comparison of Bandwidth Estimation Methods

This table compares PathKatana with Pathload and PathChirp based on key algorithmic features and performance aspects, as outlined in Section 3.2 of the technical assignment.

| Feature                     | PathKatana | Pathload | PathChirp |
|-----------------------------|------------|----------|-----------|
| Uses Packet Trains         | ✅ Yes     | ✅ Yes   | ❌ No     |
| Delta Delay Analysis       | ✅ Yes     | ❌ No    | ❌ No     |
| Overhead                   | ✅ Low     | ⚠️ High  | ✅ Low    |
| Binary Search              | ✅ Yes     | ❌ No    | ❌ No     |
| Adaptive Rate Control      | ✅ Yes     | ⚠️ Manual| ✅ Yes    |
| Theoretical Curve Fitting  | ✅ Yes     | ❌ No    | ❌ No     |
| Kalman Filtering Support   | ✅ Optional| ❌ No    | ❌ No     |
| CLI Automation & Logging   | ✅ Full    | ⚠️ Partial| ⚠️ Partial|
| PDF Report Generation      | ✅ Yes     | ❌ No    | ❌ No     |

### Notes
- **PathKatana** provides a modern, lightweight method using delta delays and binary search to precisely identify the available bandwidth without overloading the path.
- **Pathload** uses longer trains and fixed thresholds, resulting in higher bandwidth consumption and less adaptability.
- **PathChirp** focuses on chirped packet spacing but does not track delta delay and lacks binary search.

### Summary
PathKatana offers a better trade-off between measurement accuracy and network impact, especially in high-speed or constrained environments.
