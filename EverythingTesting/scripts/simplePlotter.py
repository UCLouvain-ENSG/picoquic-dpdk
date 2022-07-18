import matplotlib.pyplot as plt

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

def get_full_data(file,index):
    file1 = open(file, 'r')
    data = []
    while True:
        line = file1.readline()
        if not line:
            break
        tab = line.split(" ")
        data.append(float(tab[index]))
    return data

def get_full_data_perf(file,index):
    file1 = open(file, 'r')
    data = []
    while True:
        line = file1.readline()
        if not line:
            break
        tab = line.split()
        data.append(float(tab[index])*1000.0)
    return data


def comparison_plot_bar(items,title,yLabel,outputFileName):
    data = [i.getData() for i in items]
    labels = [i.label for i in items]
    plt.title(title)
    plt.ylabel(yLabel)
    plt.bar(labels,data)
    plt.grid(True)
    plt.savefig(outputFileName)
    
def comparison_plot_box(items,title,yLabel,outputFileName, xLabel = None):
    print(xLabel)
    data = [i.getData() for i in items]
    labels = [i.label for i in items]
    fig, ax = plt.subplots()
    ax.boxplot(data,showfliers=False)
    ax.set_xticklabels(labels)
    ax.set_title(title)
    ax.set_ylabel(yLabel)
    if xLabel != None:
        ax.set_xlabel(xLabel)
    plt.grid(True)
    plt.savefig(outputFileName,format = 'pdf')
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
    comparison_plot_box([item1,item2],"","Throughput(Mbps)","../plots/Throughput_box.png")
    
    
def handshake_time_comparison_plot_box():
    def dataFunction(file,index):
        data = get_full_data(file,index)
        return [d*(10**6) for d in data]
    item1 = ItemToPlot("picoquic",dataFunction,("../data/handshakeBBRfixed_nodpdk.txt",time_index))
    item2 = ItemToPlot("picoquic-dpdk",dataFunction,("../data/handshakeBBRfixed_dpdk.txt",time_index))
    comparison_plot_box([item1,item2],"","Request time (us)","../plots/handshake_time_box.png")
    
def handshake_time_comparison_plot_box_clean():
    def dataFunction(file,index):
        data = get_full_data(file,index)
        return [d*(10**6) for d in data if d*(10**6) < 50000]
    item1 = ItemToPlot("picoquic",dataFunction,("../data/handshakeBBR_nodpdk.txt",time_index))
    item2 = ItemToPlot("picoquic-dpdk",dataFunction,("../data/handshakeBBR_dpdk.txt",time_index))
    comparison_plot_box([item1,item2],"","Request time (us)","../plots/handshake_time_box_clean.png")
    
def handshake_comparison_plot():
    def dataFunction(file,index):
        data = get_full_data(file,index)
        return [d/20 for d in data]
    item1 = ItemToPlot("nodpdk",dataFunction,("../data/handshake_nodpdk.txt",request_index))
    item2 = ItemToPlot("dpdk",dataFunction,("../data/handshake_dpdk.txt",request_index))
    comparison_plot_box([item1,item2],"Handshake performance","Number of handshake completed (hz)","../plots/HandshakeComparison.png")
    
    
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

def batching32_plot():
    items = []
    for batching in [1,2,3,4,8,16,32]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_{}_fixed_20GB_RX32_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "","Throughput (Mbps)","../plots/batching_impact_FixedRX.pdf","rx_batching")
    
def batching64_plot():
    items = []
    for batching in [1,2,3,4,8,16,32,64]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_{}_fixed_20GB_RX64_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "","Throughput (Mbps)","../plots/batching_impact_FixedRX.pdf","tx_batching")
    
def batching_no_CC_plot():
    items = []
    for batching in [4,8,16,32,64,128]:
        item = ItemToPlot("{}".format(str(batching)),get_full_data,("../data/throughput_noCC_noPacing_{}_dpdk.txt".format(str(batching)),throughput_index))
        items.append(item)
    comparison_plot_box(items, "Batching size impact on throughput","Throughput (Mbps)","../plots/batching_impact_noCC.png")

def batching_plot():
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

def TCP_PROXY():
    items = []
    items.append(ItemToPlot("{}".format("picoquic-dpdk-proxy"),get_full_data_perf,("../data/proxy/proxyTCP1200.txt",perf_tp_index)))
    items.append(ItemToPlot("{}".format("l2-forwarder"),get_full_data_perf,("../data/proxy/noproxyTCP1200.txt",perf_tp_index)))
    comparison_plot_box(items, " " ,"Throughput (Mbps)","../plots/TCP1200cmp.pdf")
    
def TCP_proxy_var_sizes_proxy():
    items = []
    for size in [100,300,500,700,1000,1200]:
        items.append(ItemToPlot(size,get_full_data_perf,("../data/proxy/proxyTCP{}.txt".format(str(size)),perf_tp_index)))
    comparison_plot_box(items, " ", "Throughput (Mbps)","../plots/TCP_pl_size_cmp_proxy.pdf","payload size")
    
def TCP_proxy_var_sizes_forwarder():
    items = []
    for size in [100,300,500,700,1000,1200]:
        items.append(ItemToPlot(size,get_full_data_perf,("../data/proxy/noproxyTCP{}.txt".format(str(size)),perf_tp_index)))
    comparison_plot_box(items, " ", "Throughput (Mbps)","../plots/TCP_pl_size_cmp_forwarder.pdf","payload size")
        
#######PROXY######



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
    TCP_proxy_var_sizes_proxy()
    TCP_proxy_var_sizes_forwarder()

