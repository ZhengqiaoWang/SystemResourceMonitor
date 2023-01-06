# SystemResourceMonitor 系统进程监视器

## 简介

可以利用这个`Python3`程序做到：

1. 抓出有哪些进程在偷偷摸摸运行
2. 哪些进程在你不用的时候突然占用大量资源
3. 监听系统进程资源占用情况
4. 关注指定程序的资源变动情况

理论上该程序跨平台，我在编码的时候也尽力使用兼容性更强的代码，所以即便出现了兼容性问题也应该很容易定位和解决。

## 如何使用

### 环境准备

首先，你需要保证你可以运行`Python3`，如果没有安装`Python3`请移步[Python官方网站](https://www.python.org/)下载安装`Python3`和对应的`Pip`。

然后可以使用

```shell
pip install -r requirements.txt
```

安装程序所依赖的几个第三方动态库。

待安装完成，则一切就绪。

### 使用程序

我们可以使用

```shell
python start.py -h
```

来显示帮助：

```text
$ python start.py -h
usage: start.py [-h] [-o OUTPUT] [-i INTERVAL] [-f [FILTER ...]]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        输出位置
  -i INTERVAL, --interval INTERVAL
                        监听时间间隔(毫秒)
  -f [FILTER ...], --filter [FILTER ...]
                        限制监听范围，为进程名(如explorer.exe)
```

#### 监听所有的进程

一般默认情况下，程序会监听当前运行的所有进程，你只需要：

```shell
python start.py
```

即可运行程序。当你使用`Ctrl+c`退出程序时，程序会自动汇总监听到的数据，并输出在*当前目录*下的`output`文件夹下。

#### 监听指定的进程

如果你希望只监听*某些*进程，你完全可以使用`-f`或者`--filter`来指定进程名，就比如这样

```shell
python start.py -f notepad.exe Taskmgr.exe
```

它会只监听`记事本`和`任务管理器`两个进程，你不必担心它们此时有没有启动，当它们启动和退出时，程序会忠诚地记录最早启动时间和最晚退出时间。

#### 修改监听频率

默认程序按照5秒一次的频率刷新监听，如果你的统计跨度很长，那么有必要使用`-i`或者`--interval`来指定监听间隔，单位是milliseconds，即1/1000秒。

```shell
python start.py -f notepad.exe Taskmgr.exe -i 1000
```

如此你就可以从更高或更低频次的监听中找出更多细节。

#### 切换输出位置

你可以通过`-o`或`--output`来指定输出路径，需要注意的是，程序启动时会删除该路径下所有文件，等待程序结束后再生成新的记录文件。*因此请注意路径的正确性*。

### 查看结果

默认情况下会在当前目录的`output`目录下生成结果，里面主要有两项：`summury.txt`文件和`process`文件夹。前者主要记录了一些宏观统计信息。后者则包含了众多被监听的进程数据。数据以`html`的形式提供，每个文件名均为`进程名.html`格式，每个网页内包含了三张图表，可自行查看。

## 如何贡献

你可以提交`Issue`或者`Fork+PR`的方式提出你的想法和修改，我会不定期的查看并作出修改。当然，你也可以完全根据项目所属协议进行合法操作。
