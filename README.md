# mpython_conn
A transfer protocol between mPython board and Python 3.X

掌控板上可以运行 micropython 程序，尽管 micropython 有着和 Python 3.x 一样的语法，但在 micropython 中无法使用原生 Python 强大的第三方资源支持。mpython_conn 是一个用于在 Python 3.x 中控制掌控板的连接库，上位机运行 Python 程序，而掌控板作为下位机完成输入输出任务。

### Attention
This program depends on the micropython firmware on the mPython board.

本程序依赖于掌控板板载的micropython固件。

### Pypi
https://pypi.org/project/mpython-conn/

### Wiki
http://wiki.labplus.cn/index.php?title=Mpython_conn

### Installation

##### Linux & Mac OS
```shell
sudo pip3 install mpython_conn
```
###### Upgrade
```shell
sudo pip3 install mpython_conn --upgrade
```

##### Windows
Open command prompt window as administrator mode
```shell
pip3 install mpython_conn
```
###### Upgrade
```shell
pip3 install mpython_conn --upgrade
```

## License

[MIT License](http://en.wikipedia.org/wiki/MIT_License)
