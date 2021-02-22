# **三晋先锋**自动积分脚本

**仅供学习交流使用，严禁用于商业或其他用途，请于24小时内删除！**

## 使用

本脚本可使用腾讯云函数每日定时执行，也可直接在本地使用命令行运行。

本地运行需要先修改 `username` 和 `password` 字段，对应输入用户名和密码，然后在终端使用 `python3 index.py` 执行。

**现已知的问题是每天可保证 13 分，偶尔会 15 分，可能是点赞收藏接口不稳定。**

## 密码加密部分

加密后的密码受 [RuikaiWang/Study](https://github.com/RuikaiWang/Study) 启发（Copy）。

### 安装 pycrypto

1. pip uninstall crypto
2. pip uninstall pycrypto
3. pip install pycrypto

## 环境变量

用户名和密码建议通过环境变量获取。详情可查看[腾讯云函数环境变量文档](https://cloud.tencent.com/document/product/583/30228)。

Python 获取环境变量的方式：

```python
import os


value = os.environ.get('key')
print(value)
```

## 依赖安装

这一步相当于把第三方库保存到当前文件夹下。详情可查看[腾讯云函数依赖安装文档](https://cloud.tencent.com/document/product/583/39780)。

Python 可以通过 pip 包管理器进行依赖管理。由于环境配置不同，可自行将 pip 替换为 pip3 或 pip2。

使用方法：
1. 在 requirements.txt 中配置依赖信息。
2. 通过 `pip install -r requirements.txt -t .` 命令安装依赖包。
3. 上传代码库时请将依赖库一同打包上传。

这三步就是将第三方依赖安装到代码所在文件夹下。如下图：

![第三方库](https://i.loli.net/2020/12/28/92hpksd8n7Ie6F5.png)

## Server 酱微信通知

[Server 酱](http://sc.ftqq.com/3.version)使用 GitHub 一键登录，获取 SCKEY。

![SCKEY](https://i.loli.net/2020/12/28/XuO3eUF4yJ1Dt8P.jpg)

## 触发管理

![触发管理](https://i.loli.net/2020/12/28/nsdFNgaqDJX4uiI.jpg)

按上图设置好，每天中午的 11 点 10 分 16 秒开始执行任务。

## 微信通知

<div align=center><img src="https://i.loli.net/2021/02/22/5gr1cVsKzIYnmZT.jpg"></div>

## 赞赏

<div align=center><img width="260" height="260" src="https://i.loli.net/2021/01/12/ykHU2RSXoCZFfxr.jpg"></div>

![](https://i.loli.net/2020/06/17/ZpwDfJmCGEoKqnb.png)
