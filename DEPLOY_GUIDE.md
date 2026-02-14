# Streamlit Cloud 部署指南

## 第一步：注册 Streamlit Cloud

1. 访问：https://streamlit.io/cloud
2. 点击 "Sign up" 按钮
3. **强烈建议用GitHub账号登录**（因为部署时需要关联GitHub仓库）
4. 注册完成后会进入Dashboard

---

## 第二步：上传代码到 GitHub

### 方式A：已有GitHub账号
```bash
cd D:\ClaudeCode\skills\porter-strategist\math_diagnosis_tool
git init
git add .
git commit -m "Initial commit: DSE数学诊断工具"
# 在GitHub创建新仓库后执行
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

### 方式B：没有GitHub账号
1. 注册GitHub：https://github.com/signup
2. 创建新仓库，命名为 `dse-math-diagnosis`
3. 把本文件夹内容上传

---

## 第三步：在 Streamlit Cloud 部署

1. 在 Streamlit Cloud 点击 "New app"
2. 填写信息：
   - **Repository**: 选择你刚创建的GitHub仓库
   - **Branch**: main (或master)
   - **Main file path**: `app.py`
3. 点击 **"Deploy"**
4. 等待2-3分钟，部署完成后会获得一个网址：`https://你的app名.streamlit.app`

---

## 第四步：测试与验证

### 检查清单
- [ ] 打开生成的网址，能正常显示界面
- [ ] 填写表单提交，能看到"诊断结果（预览版）"
- [ ] 微信号 xiaobo20230512 正确显示

### 获取流量
- 将网址放到小红书/视频号简介
- 评论区引导："想诊断孩子提分潜力？点简介链接免费测"

---

## 后续优化

### V2版本计划
- [ ] 接入Claude API生成真实分析
- [ ] 数据自动存入飞书表格
- [ ] 添加PDF报告自动生成

### 当前版本说明
- 现在是**预览版**，结果基于简单规则
- 目的是**收集销售线索**（加微信）
- 完整版需要人工分析 + 发送PDF

---

## 常见问题

**Q: 部署失败怎么办？**
A: 检查requirements.txt是否存在，确保app.py在根目录

**Q: 免费额度够用吗？**
A: 免费版每月30天运行，足够小流量使用

**Q: 可以自定义域名吗？**
A: 可以，在Streamlit Cloud设置中添加自定义域名

---

**部署完成后，将网址告诉我，我来帮你测试引流效果。**
