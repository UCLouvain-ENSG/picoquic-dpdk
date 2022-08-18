from ast import keyword
from sqlite3 import converters
import matplotlib.pyplot as plt
import re
import numpy as np

throughput_index = 6
time_index = 4
request_index = 5
goodput_index = 2
nb_pkt_index = 7
perf_tp_index = 6


class ItemToPlot:
    def __init__(self, label,getDataFunction,args):
        self.label = label
        self.getDataFunction = getDataFunction
        self.args = args
        
    def getData(self):
        return self.getDataFunction(*self.args)
        
        
def take_average(file,index):
    file1 = open(file, 'r')
    throughput = 0
    counter = 0
    while True:
        line = file1.readline()
        if not line:
            break
        tab = line.split(" ")
        throughput += float(tab[index])
        counter +=1
    return(throughput/counter)

def identityFunction(x):
    return x

def get_full_data(file,index,keyword = ".*?",functionToApply = identityFunction):
    print(file)
    file1 = open(file, 'r')
    data = []
    for line in file1:
        if re.search(keyword,line):
                tab = line.split(" ")
                data.append(float(functionToApply(tab[index])))

            
        
    return data

def get_full_data_perf(file,index):
    file1 = open(file, 'r')
    data = []
    for line in file1:
        if re.search("sender",line):
            tab = line.split()
            unit = (tab[index + 1].split('/'))[0]
            if unit == "Gbits":
                data.append(float(tab[index])*1000.0)
            elif unit == "Mbits":
                data.append(float(tab[index]))
            else:
                print("wrong unit : " + unit)
    return data

def get_full_data_UDP(file,index):
    file1 = open(file, 'r')
    data = []
    my_max = 0
    for line in file1:
        
        if re.search("decreased", line):
            data.append(my_max)
            my_max = 0
            
        elif re.search("goodput", line):
            tokens = line.split()
            gp  = float(tokens[index])
            my_max = max(my_max,gp)
            
        
    return data
    

def comparison_plot_bar(items,title,yLabel,outputFileName):
    data = [i.getData() for i in items]
    labels = [i.label for i in items]
    plt.title(title)
    plt.ylabel(yLabel)
    plt.bar(labels,data)
    plt.grid(True)
    plt.savefig(outputFileName)
    
def comparison_plot_box(items,title,yLabel,outputFileName, xLabel = None, yTicks = None):
    print(xLabel)
    data = [i.getData() for i in items]
    labels = [i.label for i in items]
    fig, ax = plt.subplots()
    ax.boxplot(data,showfliers=False)
    ax.set_xticklabels(labels)
    ax.set_title(title)
    ax.set_ylabel(yLabel)
    ax.set_ylim(bottom=0)
    if xLabel != None:
        ax.set_xlabel(xLabel)
    if yTicks != None:
        plt.yticks(yTicks)
    plt.grid(True)
    plt.savefig(outputFileName,format = 'pdf')
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()
    
    
    
def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)
    
def comparison_plot_box_superpossed(items1,items2, title,yLabel,outputFileName, label1, label2, xLabel = None, yTicks = None):
    
    
    data1 = [i.getData() for i in items1]
    data2 = [i.getData() for i in items2]
    
    ticks = [str(i) for i in range(100,1300,100)]
    
    #starting here
    plt.figure()
    plt.grid(True)
    if xLabel != None:
        plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    

    bpl = plt.boxplot(data1, positions=np.array(range(len(data1)))*2.0-0.4, sym='', widths=0.6)
    bpr = plt.boxplot(data2, positions=np.array(range(len(data2)))*2.0+0.4, sym='', widths=0.6)
    set_box_color(bpl, '#D7191C')
    set_box_color(bpr, '#2C7BB6')

    plt.plot([], c='#D7191C', label=label1)
    plt.plot([], c='#2C7BB6', label=label2)
    plt.legend()

    plt.xticks(range(0, len(ticks) * 2, 2), ticks)
    plt.xlim(-2, len(ticks)*2)
    # plt.ylim(0, 8)
    plt.tight_layout()
    plt.savefig(outputFileName,format = 'pdf')
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()
    
def comparison_plot_box_n_superpossed(groups,ylabel,xlabel,xticksLabels,filename):
    
    
    data_groups  = []
    for group in groups:
        data = []
        for item in group:
            data.append(item.getData())
        data_groups.append(data)
    print(data_groups)
    colors = ['red','green','blue','purple']
    
    # we compare the performances of the 4 individuals within the same set of 3 settings 
    
    # --- Labels for your data:
    labels_list = [str(i) for i in range(100,1300,100)]
    width       = 1/len(labels_list)
    xlocations  = [ x*((1+ len(data_groups))*width) for x in range(len(data_groups[0]))]
    ymin        = min ( [ val  for dg in data_groups  for data in dg for val in data ] )
    ymax        = max ( [ val  for dg in data_groups  for data in dg for val in data ])

    ax = plt.gca()
    ax.set_ylim(0,ymax+ymin)

    ax.grid(True)
    ax.set_axisbelow(True)
    
    

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    for i in range(len(xticksLabels)):
        plt.plot([], c=colors[i], label=xticksLabels[i])
    plt.legend()
    space = len(data_groups)/2
    offset = len(data_groups)/2


    # --- Offset the positions per group:
    
    group_positions = []
    color_counter = 0
    for num, dg in enumerate(data_groups):    
        _off = (0 - space + (0.5+num))
        
        group_positions.append([x+_off*(width+0.01) for x in xlocations])
    first_pos = group_positions[0][0]
    last_post = group_positions[-1][-1]
    margin = 0.2
    plt.xlim(first_pos-margin, last_post+margin)
    
    for dg, pos, c in zip(data_groups, group_positions, colors):
        boxes = ax.boxplot(dg, 
                    sym='',
                    labels=['']*len(labels_list),
        #           labels=labels_list,
                    positions=pos, 
                    widths=width, 
                    # boxprops=dict(facecolor=c),
        #             capprops=dict(color=c),
        #            whiskerprops=dict(color=c),
        #            flierprops=dict(color=c, markeredgecolor=c),                       
                    # medianprops=dict(color='grey'),
        #           notch=False,  
        #           vert=True, 
        #           whis=1.5,
        #           bootstrap=None, 
        #           usermedians=None, 
        #           conf_intervals=None,
                    #patch_artist=True,
                    )
        if(color_counter>=len(colors)):
            print("Ran out of color!")
            
        set_box_color(boxes,colors[color_counter])
        color_counter+=1
    ax.set_xticks( xlocations )
    ax.set_xticklabels( labels_list, rotation=0 )


    plt.savefig(filename,format = 'pdf')
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()
    
    

def comparison_plot_bar_proxy():
    data = [800,1800,2400,5000,7000]
    labels = [100,300,500,700,1000]
    
    plt.ylabel("Throughput (Mbps)")
    plt.xlabel("UDP payload size (bytes)")
    plt.bar(labels,data,width=50)
    plt.grid(True)
    plt.savefig("../plots/dgSizeProxycmp.pdf",format = 'pdf')
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()
    
    

    
def throughput_comparison_plot_bar():
    
    item1 = ItemToPlot("nodpdk",take_average,("../data/output_nodpdk_tp_enc.txt",throughput_index))
    item2 = ItemToPlot("dpdk",take_average,("../data/output_dpdk_tp_enc.txt",throughput_index))
    comparison_plot_bar([item1,item2],"Throughput comparison","Throughput(Mbps)","../plots/Throughput_bar.png")
    
def throughput_comparison_plot_box():
    item1 = ItemToPlot("picoquic",get_full_data,("../data/throughputBBR_nodpdk.txt",throughput_index))
    item2 = ItemToPlot("picoquic-dpdk",get_full_data,("../data/throughputBBR_dpdk.txt",throughput_index))
    comparison_plot_box([item1,item2],"","Throughput(Mbps)","../plots/Throughput_box.pdf")
    
    
def throughput_comparison_interop_plot_box():
    item1 = ItemToPlot("picoquic client \n picoquic-dpdk server",get_full_data,("../data/cmp/clientNoDPDKInterop.txt",throughput_index,"Mbps"))
    item2 = ItemToPlot("picoquic-dpdk client \n picoquic server",get_full_data,("../data/cmp/clientDPDKInterop.txt",throughput_index,"Mbps"))
    comparison_plot_box([item1,item2],"","Throughput(Mbps)","../plots/Throughput_interop_box.pdf")
    
def throughput_comparison_plot_box_patched():
    item1 = ItemToPlot("picoquic",get_full_data,("../data/throughputBBR_nodpdk.txt",throughput_index))
    item2 = ItemToPlot("picoquic_patched",get_full_data,("../data/throughputBBRPatched_nodpdk.txt",throughput_index))
    comparison_plot_box([item1,item2],"","Throughput(Mbps)","../plots/Throughput_boxPatched.pdf")
    
    
def handshake_time_comparison_plot_box():
    def dataFunction(file,index):
        data = get_full_data(file,index)
        return [d*(10**6) for d in data]
    item1 = ItemToPlot("picoquic",dataFunction,("../data/handshakeBBRfixed_nodpdk.txt",time_index))
    item2 = ItemToPlot("picoquic-dpdk",dataFunction,("../data/handshakeBBRfixed_dpdk.txt",time_index))
    comparison_plot_box([item1,item2],"","Request time (us)","../plots/handshake_time_box.pdf")
    
# def handshake_time_comparison_plot_box_clean():
#     def dataFunction(file,index):
#         data = get_full_data(file,index)
#         return [d*(10**6) for d in data if d*(10**6) < 50000]
#     item1 = ItemToPlot("picoquic",dataFunction,("../data/handshakeBBR_nodpdk.txt",time_index))
#     item2 = ItemToPlot("picoquic-dpdk",dataFunction,("../data/handshakeBBR_dpdk.txt",time_index))
#     comparison_plot_box([item1,item2],"","Request time (us)","../plots/handshake_time_box_clean.pdf")
    
def handshake_comparison_plot():
    def dataFunction(file,index):
        data = get_full_data(file,index)
        return [d/20 for d in data]
    item1 = ItemToPlot("nodpdk",dataFunction,("../data/handshake_nodpdk.txt",request_index))
    item2 = ItemToPlot("dpdk",dataFunction,("../data/handshake_dpdk.txt",request_index))
    comparison_plot_box([item1,item2],"Handshake performance","Number of handshake completed (hz)","../plots/HandshakeComparison.pdf")
    
def request_comparison_plot():
    def dataFunction(file,index):
        data = get_full_data(file,index)
        return [d*(10**6) for d in data]
    item1 = ItemToPlot("picoquic",dataFunction,("../data/request_75_nodpdk.txt",time_index))
    item2 = ItemToPlot("picoquic-dpdk",dataFunction,("../data/request_75_dpdk.txt",time_index))
    comparison_plot_box([item1,item2],"","Request time (us)","../plots/request_time_box.pdf")
    
    
def server_scaling_plot():
    items = []
    for i in range(1,16):
        item = ItemToPlot(str(i),get_full_data,("../data/server_scaling_dpdk_{}.txt".format(str(i)),throughput_index))
        items.append(item)
    comparison_plot_box(items,"RSS analysis","individual throughput (Mbps)","../plots/server_scaling.png")
    
def proxy_pkt_size_Tp_plot():
    items = []
    for i in [100,500,1000,1200]:
        item = ItemToPlot("size : {}".format(str(i)),get_full_data,("../data/proxy_{}.txt".format(str(i)),goodput_index))
        items.append(item)
    comparison_plot_box(items, "Packet size impact","goodput(Mbpss)","../plots/proxy_pkt_size_goodput.png")
    
def noproxy_pkt_size_Tp_plot():
    items = []
    for i in [100,500,1000,1200]:
        item = ItemToPlot("size : {}".format(str(i)),get_full_data,("../data/noproxy_{}.txt".format(str(i)),goodput_index))
        items.append(item)
    comparison_plot_box(items, "Packet size impact without proxy","goodput(Mbps)","../plots/noproxy_pkt_size_goodput.png")
    
def proxy_pkt_size_NbPkt_plot():
    items = []
    for i in [100,500,1000,1200]:
        item = ItemToPlot("size : {}".format(str(i)),get_full_data,("../data/proxy_{}.txt".format(str(i)),nb_pkt_index ))
        items.append(item)
    comparison_plot_box(items, "Packet size impact","packets transmitted","../plots/proxy_pkt_size_nb_packet.png")
    
def proxy_TCP():
    items = []
    item = ItemToPlot("MSS : 1200",get_full_data_perf,("../data/proxy_tcp_1200.txt",perf_tp_index))
    items.append(item)
    comparison_plot_box(items, "TCP","goodput(Mbps)","../plots/tcpProxy.png")

def proxy_TCP_vs_UDP():
    item1 = ItemToPlot("TCP",get_full_data_perf,("../data/proxy_tcp_1200.txt",perf_tp_index))
    item2 = ItemToPlot("UDP",get_full_data,("../data/proxy_{}.txt".format("1200"),goodput_index))
    items = [item1, item2]
    comparison_plot_box(items, "Comparison","goodput(Mbps)","../plots/TCPvsUDPProxy.png")

def noproxy_pkt_size_plot():
    items = []
    for i in [10,100,1000]:
        item = ItemToPlot("payload_size : {}".format(str(i)),get_full_data,("../data/noproxy_{}.txt".format(str(i)),3))
        items.append(item)
    comparison_plot_box(items, "Packet size impact without proxy","time elpased (s)","../plots/noproxy_pkt_size.png")
    
###BATCHING###

def batchingTX_fixedRX64_plot():
    items = []
    for batching in [1,2,3,4,8,16,32,64]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_{}_fixed_20GB_RX64_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "","Throughput (Mbps)","../plots/batching_impact_FixedRX.pdf","tx_batching")
    
# def batching64_plot():
#     items = []
#     for batching in [1,2,3,4,8,16,32,64]:
#         item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_{}_fixed_20GB_RX64_dpdk.txt".format(str(batching)),throughput_index))
#         items.append(item)
#     comparison_plot_box(items, "","Throughput (Mbps)","../plots/batching_impact_FixedRX.pdf","tx_batching")

def batchingRX_fixedTX64_plot():
    items = []
    for batching in [4,8,16,32,64]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/batching/throughput_{}_fixed_20GB_TX64_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "","Throughput (Mbps)","../plots/batching_impact_FixedTX.pdf","rx_batching")
    
def batching_no_CC_plot():
    items = []
    for batching in [4,8,16,32,64,128]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_noCC_noPacing_{}_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "Batching size impact on throughput","Throughput (Mbps)","../plots/batching_impact_noCC.png")

def batching_plot_fixedTX64_plot():
    items = []
    for batching in [4,8,16,32,64]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_{}_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "Batching size impact on throughput","Throughput (Mbps)","../plots/batching_impact_withCC.png")
    
def batching_plot_CCalgo():
    items = []
    for CC in ["bbr","cubic","fast","reno"]:
        item = ItemToPlot("{}".format(str(CC)),get_full_data,("../data/CC_big_{}_dpdk.txt".format(str(CC)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "Batching size impact on throughput","Throughput (Mbps)","../plots/batching_impact_CCalgo.png")
    
def batching_plot_without_rereceive():
    items = []
    for batching in [4,8,16,32,64]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_{}_fixed_80GBfixed2_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "Batching size impact on throughput (80GB file without rereceive)","Throughput (Mbps)","../plots/batching_norereceive_80GB.png")
 
def batching_plot_with_rereceive():
    items = []
    items.append(ItemToPlot("(1,32)",get_full_data,("../data/throughput_1T32R_fixed_80GBwrereceive_dpdk.txt",throughput_index)))
    for batching in [4,8,16,32,64]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_{}_fixed_80GBwrereceive_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "Batching size impact on throughput (80GB)","Throughput (Mbps)","../plots/batching_rereceive_80GB.png")
    
    
def batching_plot_with_128RX():
    items = []
    for batching in [4,8,16,32,64]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_{}_fixed_10GB_RX128_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "Batching size impact on throughput (10GB) fixed 128RX","Throughput (Mbps)","../plots/batching_10GB_128RX.png")

    
###BATCHING###


##########$RSS#############

def RSS_plot15():
    items = []
    for core in range(1,16):
        item = ItemToPlot("{}".format(str(core)),get_full_data,("../data/TP_{}core_dpdk.txt".format(str(core)),throughput_index))
        items.append(item)
    comparison_plot_box(items, " " ,"Throughput (Mbps)","../plots/RSS.pdf","# of cores")

def RSS_plot8():
    items = []
    for core in range(1,9):
        item = ItemToPlot("{}".format(str(core)),get_full_data,("../data/TP_{}core_dpdk_8_client.txt".format(str(core)),throughput_index))
        items.append(item)
    comparison_plot_box(items, " " ,"Throughput (Mbps)","../plots/RSS8.pdf","# of cores")
    
def RSS_plot8X():
    items = []
    for core in range(1,9):
        item = ItemToPlot("{}".format(str(core)),get_full_data,("../data/TP_{}core_dpdk_8_client_X.txt".format(str(core)),throughput_index))
        items.append(item)
    comparison_plot_box(items, " " ,"Throughput (Mbps)","../plots/RSS8X.pdf","# of cores")
    
    
def RSS_PLOT_BAR():
    
    x = np.arange(8)
    y1_tmp = get_full_data("../data/RSS/balance_5core_dpdk_8_client.txt",
                       2,"queueid")
    y1 = np.zeros(8,dtype=int)
    for val in y1_tmp:
        y1[int(val)] += 1
    y2_tmp = get_full_data("../data/RSS/balance_7core_dpdk_8_client.txt",
                       2,"queueid")
    y2 = np.zeros(8,dtype=int)
    for val in y2_tmp:
        y2[int(val)] += 1
    y3_tmp = get_full_data("../data/RSS/balance_8core_dpdk_8_client.txt",
                       2,"queueid")
    y3 = np.zeros(8,dtype=int)
    for val in y3_tmp:
        y3[int(val)] += 1
    
    width = 0.2
    
    # plot data in grouped manner of bar type
    plt.ylim(0, 4)
    plt.bar(x-0.2, y1, width, color='cyan')
    plt.bar(x, y2, width, color='orange')
    plt.bar(x+0.2, y3, width, color='green')
    plt.xticks(x, [str(i) for i in range(8)])
    
    plt.xlabel("Core id")
    plt.ylabel("Number of clients")
    plt.legend(["Server with 5 cores", "Server with 7 cores", "Server with 8 cores"])
    plt.savefig("../plots/RSS_balance_noX.pdf",format = 'pdf')
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()
    
    
def RSS_PLOT_BAR_X():
    
    x = np.arange(8)
    y1_tmp = get_full_data("../data/RSS/balance_5core_dpdk_8_client_X.txt",
                       2,"queueid")
    y1 = np.zeros(8,dtype=int)
    for val in y1_tmp:
        y1[int(val)] += 1
    y2_tmp = get_full_data("../data/RSS/balance_7core_dpdk_8_client_X.txt",
                       2,"queueid")
    y2 = np.zeros(8,dtype=int)
    for val in y2_tmp:
        y2[int(val)] += 1
    y3_tmp = get_full_data("../data/RSS/balance_8core_dpdk_8_client_X.txt",
                       2,"queueid")
    y3 = np.zeros(8,dtype=int)
    for val in y3_tmp:
        y3[int(val)] += 1
    
    width = 0.2
    
    # plot data in grouped manner of bar type
    plt.ylim(0, 4)
    plt.bar(x-0.2, y1, width, color='cyan')
    plt.bar(x, y2, width, color='orange')
    plt.bar(x+0.2, y3, width, color='green')
    plt.xticks(x, [str(i) for i in range(8)])
    plt.xlabel("Core id")
    plt.ylabel("Number of clients")
    plt.legend(["Server with 5 cores", "Server with 7 cores", "Server with 8 cores"])
    plt.savefig("../plots/RSS_balance_X.pdf",format = 'pdf')
    plt.figure().clear()
    plt.close()
    plt.cla()
    plt.clf()

##########$RSS#############

##########$ENCRYPTION######
def encryption_plot():
    items = []
    
    items.append(ItemToPlot("{}".format("pquic-enc"),get_full_data,("../data/throughputBBR_nodpdk.txt",throughput_index)))
    items.append(ItemToPlot("{}".format("pquic-dpdk-enc"),get_full_data,("../data/throughputBBR_dpdk.txt",throughput_index)))
    items.append(ItemToPlot("{}".format("pquic-noenc"),get_full_data,("../data/throughputBBR_noEncryption_nodpdk.txt",throughput_index)))
    items.append(ItemToPlot("{}".format("pquic-dpdk-noenc"),get_full_data,("../data/throughputBBR_noEncryption_dpdk.txt",throughput_index)))
    comparison_plot_box(items, " " ,"Throughput (Mbps)","../plots/encryption.pdf")
    
    
def encryption_plot_DPDK():
    items = []
    items.append(ItemToPlot("{}".format("CHACHA"),get_full_data,("../data/throughputBBR20_dpdk.txt",throughput_index)))
    items.append(ItemToPlot("{}".format("AES128"),get_full_data,("../data/throughputBBR128_dpdk.txt",throughput_index)))
    items.append(ItemToPlot("{}".format("AES256"),get_full_data,("../data/throughputBBR256_dpdk.txt",throughput_index)))

    comparison_plot_box(items, " " ,"Throughput (Mbps)","../plots/encryptionDPDKcmp.pdf")
    
def encryption_plot_NODPDK():
    items = []
    items.append(ItemToPlot("{}".format("CHACHA"),get_full_data,("../data/throughputBBR20_nodpdk.txt",throughput_index)))
    items.append(ItemToPlot("{}".format("AES128"),get_full_data,("../data/throughputBBR128_nodpdk.txt",throughput_index)))
    items.append(ItemToPlot("{}".format("AES256"),get_full_data,("../data/throughputBBR256_nodpdk.txt",throughput_index)))

    comparison_plot_box(items, " " ,"Throughput (Mbps)","../plots/encryptionNODPDKcmp.pdf")
    
    
##########$ENCRYPTION######


#######PROXY######

def get_full_data_perf_nb_packets(file,index,size):
    res = get_full_data_perf(file,index)
    return [x*1000000/8/size for x in res]

def get_full_data_UDP_nb_packets(file,index,size):
    res = get_full_data_UDP(file,index)
    return [x*1000000/8/size for x in res]

def TCP_PROXY():
    items = []
    items.append(ItemToPlot("{}".format("picoquic-dpdk-proxy"),get_full_data_perf,("../data/proxy/proxyTCP1200.txt",perf_tp_index)))
    items.append(ItemToPlot("{}".format("l2-forwarder"),get_full_data_perf,("../data/proxy/noproxyTCP1200.txt",perf_tp_index)))
    comparison_plot_box(items, " " ,"Throughput (Mbps)","../plots/TCP1200cmp.pdf")
    
def TCP_proxy_var_sizes_proxy():
    items = []
    for size in range(100,1300,100):
        items.append(ItemToPlot(size,get_full_data_perf,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index)))
    comparison_plot_box(items, " ", "Throughput (Mbps)","../plots/TCP_pl_size_cmp_proxy.pdf","payload size",range(0,11000,1000))
    
def TCP_proxy_var_sizes_forwarder():
    items = []
    for size in range(100,1300,100):
        items.append(ItemToPlot(size,get_full_data_perf,("../data/proxy/noproxyTCP{}.txt".format(str(size)),perf_tp_index)))
    comparison_plot_box(items, " ", "Throughput (Mbps)","../plots/TCP_pl_size_cmp_forwarder.pdf","payload size")
    
    
def TCP_proxy_var_sizes_proxy_nb_packets():
    items = []
    for size in range(100,1300,100):
        items.append(ItemToPlot(size,get_full_data_perf_nb_packets,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index,size)))
    comparison_plot_box(items, " ", "Number of packets transmitted per second","../plots/TCP_pl_size_cmp_proxy_nb_packets.pdf","payload size")
    
def TCP_proxy_var_sizes_forwarder():
    items = []
    for size in range(100,1300,100):
        items.append(ItemToPlot(size,get_full_data_perf,("../data/proxy/noproxyTCP{}.txt".format(str(size)),perf_tp_index)))
    comparison_plot_box(items, " ", "Throughput (Mbps)","../plots/TCP_pl_size_cmp_forwarder.pdf","payload size")
        
        
def UDP_proxy_var_sizes_proxy():
    items = []
    for size in range(100,1300,100):
        items.append(ItemToPlot(size,get_full_data_UDP,("../data/proxy/proxyUDP{}.txt".format(str(size)),2)))
    comparison_plot_box(items, " ", "Throughput (Mbps)","../plots/UDP_pl_size_cmp_proxy.pdf","payload size",range(0,11000,1000))
    
def UDP_proxy_var_sizes_proxy_nb_packets():
    items = []
    for size in range(100,1300,100):
        items.append(ItemToPlot(size,get_full_data_UDP_nb_packets,("../data/proxy/proxyUDP{}.txt".format(str(size)),2,size)))
    comparison_plot_box(items, " ", "Number of packets transmitted per second","../plots/UDP_pl_size_cmp_proxy_nb_packets.pdf","payload size")
    
def UDP_proxy_var_sizes_forwarder():
    items = []
    for size in range(100,1300,100):
        items.append(ItemToPlot(size,get_full_data_UDP,("../data/proxy/noproxyUDP{}.txt".format(str(size)),2)))
    comparison_plot_box(items, " ", "Throughput (Mbps)","../plots/UDP_pl_size_cmp_forwarder.pdf","payload size")
    
    
# def TCP_proxy_cmp_wireguard_TP():
#     items1 = []
#     items2 = []
#     for size in range(100,1300,100):
#         items1.append(ItemToPlot("proxy",get_full_data_perf,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index)))
#         items2.append(ItemToPlot("wireguard",get_full_data_perf,("../data/proxy/wireguardTCP{}.txt".format(str(size)),perf_tp_index)))
        
#     comparison_plot_box_superpossed(items1,items2, "" ,"Throughput (Mbps)","../plots/wireguardVsProxyTP.pdf", 'proxy','wiregard', xLabel = "payload size", yTicks = None)
    
def prox_TCP_UDP_TP():
    items1 = []
    items2 = []
    for size in range(100,1300,100):
        
        items1.append(ItemToPlot("TCP",get_full_data_perf,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index)))
        items2.append(ItemToPlot("UDP",get_full_data,("../data/proxy/proxyUDP{}.txt".format(str(size)),3,"final")))
        
    comparison_plot_box_n_superpossed([items1,items2],'Goodput (Mbps)','payload size (bytes)',['TCP','UDP'],"../plots/TCPvsUDP_TP.pdf")


def prox_TCP_vs_forwarder_TP():
    items1 = []
    items2 = []
    for size in range(100,1300,100):
        
        items1.append(ItemToPlot("proxy",get_full_data_perf,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index)))
        items2.append(ItemToPlot("forwarder",get_full_data_perf,("../data/proxy/noproxyTCP{}.txt".format(str(size)),perf_tp_index)))
        
    comparison_plot_box_n_superpossed([items1,items2],'Goodput (Mbps)','payload size (bytes)',['relay','forwarder'],"../plots/proxy_vs_forwarder_TP.pdf")

def prox_TCP_UDP_PPS():
    items1 = []
    items2 = []
    for size in range(100,1300,100):
        
        def extractor(x,mysize=size):
            return float(x)*1000000/8/mysize
        
        items1.append(ItemToPlot("TCP",get_full_data_perf_nb_packets,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index,size)))
        items2.append(ItemToPlot("UDP",get_full_data,("../data/proxy/proxyUDP{}.txt".format(str(size)),3,"final",extractor)))
        
    comparison_plot_box_n_superpossed([items1,items2],'Packet per second','payload size (bytes)',['TCP','UDP'],"../plots/TCPvsUDP_PPS.pdf")
   
def TCP_proxy_cmp_wireguard_TP():
    items1 = []
    items2 = []
    items3 = []
    for size in range(100,1300,100):
        items1.append(ItemToPlot("picoquic",get_full_data_perf,("../data/proxy/proxyTCPNoDPDK{}.txt".format(str(size)),perf_tp_index)))
        items2.append(ItemToPlot("picoquic-dpdk",get_full_data_perf,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index)))
        items3.append(ItemToPlot("wireguard",get_full_data_perf,("../data/proxy/wireguardTCP{}.txt".format(str(size)),perf_tp_index)))
        
    comparison_plot_box_n_superpossed([items1,items2,items3],'Goodput (Mbps)','payload size (bytes)',['picoquic','picoquic-dpdk','wireguard'],"../plots/wireguardVsProxyTP.pdf")

def TCP_proxy_cmp_wireguard_PPS():
    items1 = []
    items2 = []
    items3 = []
    for size in range(100,1300,100):
        items1.append(ItemToPlot("picoquic",get_full_data_perf_nb_packets,("../data/proxy/proxyTCPNoDPDK{}.txt".format(str(size)),perf_tp_index,size)))
        items2.append(ItemToPlot("picoquic-dpdk",get_full_data_perf_nb_packets,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index,size)))
        items3.append(ItemToPlot("wireguard",get_full_data_perf_nb_packets,("../data/proxy/wireguardTCP{}.txt".format(str(size)),perf_tp_index,size)))
        
    comparison_plot_box_n_superpossed([items1,items2,items3],'Packet per second','payload size (bytes)',['picoquic','picoquic-dpdk','wireguard'],"../plots/wireguardVsProxyPPS.pdf")
    
#######PROXY######




######implem cmp##########


    
def implems_cmp():
    msquic_index = 4
    quiche_index = 2
    picotls_index = 6
    items = []
    items.append(ItemToPlot("picoquic",get_full_data,("../data/cmp/picoquicFair.txt",throughput_index, "Mbps")))
    items.append(ItemToPlot("picoquic-dpdk",get_full_data,("../data/throughputBBR_dpdk.txt",throughput_index)))
    
    items.append(ItemToPlot("msquic", get_full_data,("../data/cmp/msquicFair.txt",msquic_index,"kbps",lambda a : float(a)/1000)))
    items.append(ItemToPlot("quiche", get_full_data,("../data/cmp/quicheFair.txt",quiche_index,"Mbps")))
    
    f = lambda x : x[1:-8]
    items.append(ItemToPlot("picotls", get_full_data,("../data/cmp/picotlsFair.txt",picotls_index,"Mbps",f)))
    
    comparison_plot_box(items, " ", "Throughput (Mbps)","../plots/implem_cmp_fair.pdf")
    
    
    
    


######implem cmp##########

######################SELECT#########################


def selectBarPLot():
    
    implems = ['picoquic','picoquic_patched']
    cpu_utilisation = [70,100]
    plt.ylabel("CPU utilisation (%)")
    plt.bar(implems,cpu_utilisation)
    plt.grid(True)
    plt.ylim(bottom=0)
    
    plt.savefig("../plots/select_bar_cpu_utilisation.pdf")


#####################SELECT##########################


if __name__ == "__main__":
    #handshake_comparison_plot()
    #throughput_comparison_plot_box()
    #server_scaling_plot()
    #noproxy_pkt_size_plot()
    #batching_no_CC_plot()
    #batching_plot()
    #proxy_pkt_size_NbPkt_plot()
    #proxy_pkt_size_Tp_plot()
    #noproxy_pkt_size_Tp_plot()
    #proxy_TCP()
    #proxy_TCP_vs_UDP()
    #batching32_plot()
    #batching_plot_CCalgo()
    #batching_plot_without_rereceive()
    #batching_plot_with_128RX()
    #handshake_time_comparison_plot_box()
    #handshake_time_comparison_plot_box_clean()
    #RSS_plot()
    #RSS_plot8()
    #RSS_plot8X()
    #encryption_plot()
    
    #encryption_plot_DPDK()
    #encryption_plot_NODPDK()
    #TCP_PROXY()
    #comparison_plot_bar_proxy()
    #batching64_plot()
    # TCP_proxy_var_sizes_proxy()
    # TCP_proxy_var_sizes_forwarder()
    # UDP_proxy_var_sizes_proxy()
    # UDP_proxy_var_sizes_forwarder()
    
    # TCP_proxy_var_sizes_proxy_nb_packets()
    # UDP_proxy_var_sizes_proxy_nb_packets()
    
    #request_comparison_plot()
    #throughput_comparison_plot_box()
    #handshake_time_comparison_plot_box()
    #TCP_proxy_cmp_wireguard_PPS()
    #implems_cmp()
    
    #fast_test()
    #throughput_comparison_plot_box_patched()
    #implems_cmp()
    
    #TCP_proxy_cmp_wireguard_TP()
    #TCP_proxy_cmp_wireguard_PPS()
    #prox_TCP_UDP_TP()
    #prox_TCP_UDP_PPS()
    #prox_TCP_vs_forwarder_TP()
    #implems_cmp()
    # batchingRX_fixedRX32_plot()
    # batching32_plot()
    
    # batchingTX_fixedRX64_plot()
    # batchingRX_fixedTX64_plot()
    
    # RSS_PLOT_BAR()
    # RSS_PLOT_BAR_X()
    #selectBarPLot()
    
    throughput_comparison_interop_plot_box()