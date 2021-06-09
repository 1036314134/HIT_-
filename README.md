# HIT_Compiling_System_2021 lab

哈工大2018级编译系统实验


lab2

利用加载好的action和goto表进行语法分析。
文件执行时action.txt、goto.txt和input.txt需要放到同一路径下。
输入文件为input.txt，内容为词法分析后的结果
输出语法树结果在result.txt中,错误信息在error.log中
可在test.txt中输入待编译程序，由词法分析.py进行词法分析后再进行语法分析。
词法分析输出结果为input.txt

lab3

根据lab2得到的语法树进行分析。
需要把result.txt与语义分析程序放在同一路径下。
输出的四元式存放在tetrads.txt中，符号表存放在symbols.txt中。
测试样例为test.txt，需要依次进行词法分析、语法分析，再进行语义分析。
