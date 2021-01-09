# _*_ coding:utf-8 _*_

# 将IP地址转换为十进制整数
def ip2int(ip):
    ip_list = ip.strip().split('.')
    SUM = 0
    for i in range(len(ip_list)):
        SUM += int(ip_list[i])*256**(3-i)
    return SUM