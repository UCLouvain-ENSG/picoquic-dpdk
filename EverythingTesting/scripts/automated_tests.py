#!/usr/bin/env python3

from subprocess import Popen, PIPE

import json
import shlex
import time

def retrieve_cards(number):
    cards = open('cards.txt', 'r')
    lines = cards.readlines()
    counter = 0
    nic_counter = 0
    ret = ''
    for line in lines:
        if(counter < 4):
            counter +=1
        else:
            line_as_array = line.split()
            card_id = line_as_array[0]
            ret += '-a 0000:{} '.format(card_id)
            nic_counter += 1
            if nic_counter == number:
                return ret
    return ret


#Global variables
nsc='sudo ip netns exec nsCLIENT'
nss='sudo ip netns exec nsSERVER'

serverName = 'server'
clientName = 'client1'
process_name = 'dpdk_picoquicdemo'
dpdk1Client = '--dpdk -l 0-1 -a 0000:18:00.1 -- -A 50:6b:4b:f3:7c:70'
dpdk15Client = '--dpdk -l 0-15 {} -- -A 50:6b:4b:f3:7c:71'.format(retrieve_cards(15))
dpdk8Client = '--dpdk -l 0-8 {} -- -A 50:6b:4b:f3:7c:71'.format(retrieve_cards(8))
dpdk1Server = '--dpdk -l 0-1 -a 0000:18:00.0 --'
dpdkVarServer = '--dpdk -l 0-{} -a 0000:51:00.1 --'
nodpdk = 'nodpdk'
working_directory = '/home/nikita/memoire/dpdk_picoquic'


def dic_to_json(dic):
    return shlex.quote(json.dumps(dic))
    

def get_pid_process(host,name):
    cmds = ['ssh',host,'nohup','pidof',name]
    p = Popen(cmds, stdout=PIPE)
    return p.communicate()[0]

def kill_process(host,pid):
    cmds = ['ssh',host,'nohup','sudo kill',str(pid)]
    return Popen(cmds, stdout=None, stderr=None, stdin=None)

def run_command(command,host,directory):
    cmds = ['ssh', host,'cd {}; {}'.format(directory,command)]
    print(cmds)
    return Popen(cmds, stdout=None, stderr=None, stdin=None)
    
def run_client(args):
    cmds = ['ssh', clientName,'python3','/home/nikita/memoire/dpdk_picoquic/EverythingTesting/scripts/client_for_tests.py',dic_to_json(args)]
    return Popen(cmds, stdout=None, stderr=None, stdin=None)

def run_server(args):
    cmds = ['ssh', serverName,'python3','/home/nikita/memoire/dpdk_picoquic/EverythingTesting/scripts/server_for_tests.py',dic_to_json(args)]
    return Popen(cmds, stdout=None, stderr=None, stdin=None)

def test_generic(argsClient,argsServer,isComparison):
    run_server(argsServer)
    time.sleep(5)
    client_process = run_client(argsClient)
    client_process.wait()
    pid = get_pid_process(serverName,process_name)
    intPid = int(pid)
    killing_process = kill_process(serverName,str(intPid))
    killing_process.wait()
    
    if isComparison:
        argsClientNoDpdk = argsClient.copy()
        argsClientNoDpdk["eal"] = nodpdk
        argsClientNoDpdk["output_file"] = argsClientNoDpdk["output_file"].replace("dpdk","nodpdk")
        
        argsServerNoDpdk = argsServer.copy()
        argsServerNoDpdk["eal"] = nodpdk
        
        run_server(argsServerNoDpdk)
        client_process = run_client(argsClientNoDpdk)
        client_process.wait()
        pid = get_pid_process(serverName,process_name)
        intPid = int(pid)
        killing_process = kill_process(serverName,str(intPid))
        killing_process.wait()
    print("FINISHED")
    
    
def test_generic_repeting_client(argsClient,argsServer,isComparison,repetition):
    run_server(argsServer)
    time.sleep(5)
    for it in range(repetition):
        client_process = run_client(argsClient)
        client_process.wait()
        time.sleep(5)
    
    pid = get_pid_process(serverName,process_name)
    intPid = int(pid)
    killing_process = kill_process(serverName,str(intPid))
    killing_process.wait()
    
    if isComparison:
        argsClientNoDpdk = argsClient.copy()
        argsClientNoDpdk["eal"] = nodpdk
        argsClientNoDpdk["output_file"] = argsClientNoDpdk["output_file"].replace("dpdk","nodpdk")
        
        argsServerNoDpdk = argsServer.copy()
        argsServerNoDpdk["eal"] = nodpdk
        
        run_server(argsServerNoDpdk)
        for it in range(repetition):
            client_process = run_client(argsClientNoDpdk)
            client_process.wait()
            time.sleep(5)
        pid = get_pid_process(serverName,process_name)
        intPid = int(pid)
        killing_process = kill_process(serverName,str(intPid))
        killing_process.wait()    
    print("FINISHED")
    
def test_server_scaling():
    
    clientArgs = {"eal" : dpdk15Client,
                  "args": "-D ",
                  "output_file":"server_scaling_dpdk.txt",
                  "ip_and_port" : "10.100.0.2 5600",
                  "request" : "/10000000000",
                  "keyword" : "Mbps"}   
    serverArgs = {"eal" : dpdk1Server,
                  "args" : "",
                  "port" : "-p 5600"}
    for i in range(3,16):
        serverArgs["eal"] = 'dpdk -l 0-{} -a 0000:51:00.1 --'.format(i)
        clientArgs["output_file"] = "server_scaling_dpdk_{}.txt".format(str(i))
        test_generic(clientArgs,serverArgs,False)
        time.sleep(10)
    
 
## TP TESTS ##   
def test_throughput():
    ##Throughput test
    for it in range(15):
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-D",
                    "output_file":"throughputBBR_dpdk.txt",
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic(clientArgsDpdk,serverArgsDpdk,True)
        time.sleep(5)
        
def test_throughput256():
    ##Throughput test
    
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"throughputBBR256_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/20000000000",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
    
def test_throughput128():
    ##Throughput test
    
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"throughputBBR128_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/20000000000",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
    
def test_throughput20():
    ##Throughput test
    
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"throughputBBR20_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/20000000000",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
    
## TP TESTS ##  
    
def test_throughput_without_encryption():
    ##Throughput test
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"throughputBBR_noEncryption_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/40000000000",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
        
        
    
def test_handshake_simple():
    ##Throughput test
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"handshakeBBRfixed_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "/8",
                "keyword" : "Mbps"}
    
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,50)
   
def test_RSS_15():
    for server_core in range(11,16): 
        clientArgsDpdk = {"eal" : dpdk15Client,
                    "args": "-D",
                    "output_file":"TP_{}core_dpdk.txt".format(str(server_core)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdkVarServer.format(str(server_core)),
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,8)
        time.sleep(10)
        
def test_RSS_8():
    for server_core in [8]: 
        clientArgsDpdk = {"eal" : dpdk8Client,
                    "args": "-D",
                    "output_file":"TP_{}core_dpdk_8_client.txt".format(str(server_core)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdkVarServer.format(str(server_core)),
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,8)
        time.sleep(10)
        
def test_RSS_8_X():
    for server_core in [8]: 
        clientArgsDpdk = {"eal" : dpdk8Client,
                    "args": "-D -X",
                    "output_file":"TP_{}core_dpdk_8_client_X.txt".format(str(server_core)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdkVarServer.format(str(server_core)),
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,8)
        time.sleep(10)
     
    
def test_handshake():
    #Testing handshake
    for it in range(10):
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-H -D",
                    "output_file":"handshake_new_dpdk.txt",
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/100",
                    "keyword" : "served"}   
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : "",
                    "port" : "-p 4443"}
        test_generic(clientArgsDpdk,serverArgsDpdk,True)
    
def test_request():
    #Testing requests
    
    clientArgsDpdk = {"eal" : dpdk1Client,
                "args": "-D",
                "output_file":"request_100_dpdk.txt",
                "ip_and_port" : "10.100.0.2 4443",
                "request" : "*100:/20000",
                "keyword" : "Mbps"}   
    serverArgsDpdk = {"eal" : dpdk1Server,
                "args" : "",
                "port" : "-p 4443"}
    test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,True,15)
  
    
def test_batching():
    for it in range(5):
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-D -* 1 -@ 32 -G cubic",
                    "output_file":"throughput_1,32_fixed_80GBwrereceive_dpdk.txt",
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/80000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : " -G cubic -* 1 -@ 32",
                    "port" : "-p 4443"}
        test_generic(clientArgsDpdk,serverArgsDpdk,False)
        time.sleep(5)
    time.sleep(10)
        
def test_batching_fixed_RX():
    for i in [4,8,16,32,64]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -* {} -@ 128 -G cubic".format(str(i)),
                        "output_file":"throughput_{}_fixed_10GB_RX128_dpdk.txt".format(str(i)),
                        "ip_and_port" : "10.100.0.2 4443",
                        "request" : "/20000000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : " -G cubic -* {} -@ 128".format(str(i)),
                        "port" : "-p 4443"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)
        
        
def test_batching_fixed_RX32():
    for i in [1,2,3,4,8,16,32]:
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-D -* {} -@ 32".format(str(i)),
                    "output_file":"throughput_{}_fixed_20GB_RX32_dpdk.txt".format(str(i)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : "-* {} -@ 32".format(str(i)),
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,15)
        
def test_batching_fixed_RX64():
    for i in [1,2,3,4,8,16,32,64]:
        clientArgsDpdk = {"eal" : dpdk1Client,
                    "args": "-D -* {} -@ 64".format(str(i)),
                    "output_file":"throughput_{}_fixed_20GB_RX64_dpdk.txt".format(str(i)),
                    "ip_and_port" : "10.100.0.2 4443",
                    "request" : "/20000000000",
                    "keyword" : "Mbps"}
        
        serverArgsDpdk = {"eal" : dpdk1Server,
                    "args" : "-* {} -@ 64".format(str(i)),
                    "port" : "-p 4443"}
        test_generic_repeting_client(clientArgsDpdk,serverArgsDpdk,False,15)
        
        
def test_batching2():
    for i in [1,2,4,8,16,32,64]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -* {}".format(str(i)),
                        "output_file":"throughput32_{}_dpdk.txt".format(str(i)),
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/80000000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : "-* {}".format(str(i)),
                        "port" : "-p 5600"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)

def test_congestion_dpdk():
    for CC in ["reno", "cubic", "bbr", "fast"]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -G {} -* 1".format(CC),
                        "output_file":"CC_{}_dpdk.txt".format(CC),
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/2000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : "-G {} -* 1".format(CC),
                        "port" : "-p 5600"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)
        
def test_congestion_big_dpdk():
    for CC in ["reno", "cubic", "bbr", "fast"]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -G {} -* 32".format(CC),
                        "output_file":"CC_big_{}_dpdk.txt".format(CC),
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/10000000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : "-G {} -* 32".format(CC),
                        "port" : "-p 5600"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)
        
def test_congestion_nodpdk():
    clientArgsDpdk = {"eal" : nodpdk,
                        "args": "-D",
                        "output_file":"CC_nodpdk.txt",
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/2000000",
                        "keyword" : "Mbps"}
            
    serverArgsDpdk = {"eal" : nodpdk,
                        "args" : " ",
                        "port" : "-p 5600"}
    test_generic(clientArgsDpdk,serverArgsDpdk,False)
    
def test_batching_noCC_noPacing():
    for i in [4,8,16,32,64,128]:
        for it in range(5):
            clientArgsDpdk = {"eal" : dpdk1Client,
                        "args": "-D -* {} -@ {}".format(str(i),str(i)),
                        "output_file":"throughput_noCC_noPacing_{}_dpdk.txt".format(str(i)),
                        "ip_and_port" : "10.100.0.2 5600",
                        "request" : "/20000000000",
                        "keyword" : "Mbps"}
            
            serverArgsDpdk = {"eal" : dpdk1Server,
                        "args" : "-* {} -@ {}".format(str(i),str(i)),
                        "port" : "-p 5600"}
            test_generic(clientArgsDpdk,serverArgsDpdk,False)
            time.sleep(5)
        time.sleep(10)


#############PROXY TESTING#####################

def clean_everything():
    p1 = run_command("sh killDpdkProcess.sh",clientName,working_directory)
    p2 = run_command("sh killForwarder.sh",clientName,working_directory)
    p3 = run_command("sh killiperf3.sh",serverName,working_directory)
    p4 = run_command("sh killUDP.sh",serverName,working_directory)
    for p in [p1,p2,p3,p4]:
        p.wait()
    
def proxy_TCP_testing():
    #dpdk proxy
    server = run_command("sh network_scripts/proxy_setup_server.sh",serverName,working_directory)
    server.wait()
    for i in range(5):
        for size in range(100,1300,100):
            
            clientP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",clientName,working_directory)
            time.sleep(3)
            clientP2 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,working_directory)
            time.sleep(3)
            serverP2 = run_command(nss + " taskset -c 2 iperf3 -s >> /dev/null",serverName,working_directory)
            time.sleep(3)
            serverP1 = run_command(nsc + " taskset -c 4 iperf3 -M {} -c 10.10.0.2 -t 30 >> EverythingTesting/data/proxy/proxyTCP{}.txt".format(str(size),str(size)),serverName,working_directory)
            serverP1.wait()
            clean_everything();
            time.sleep(3);
    #forwarder
    server = run_command("sudo ip -all netns delete  ",serverName,working_directory)  
    server.wait()        
    for i in range(1):
        for size in [1200]:        
            clientP1 = run_command("sh exec_scripts/dpdk_relay2.sh >> /dev/null",clientName,working_directory)
            time.sleep(3)
            clientP2 = run_command("sh exec_scripts/dpdk_relay1.sh >> /dev/null",clientName,working_directory)
            time.sleep(3)
            serverP2 = run_command(nss + " iperf3 -s >> /dev/null",serverName,working_directory)
            time.sleep(3)
            serverP1 = run_command(nsc + " iperf3 -M {} -c 10.10.0.2 -t 30 >> EverythingTesting/data/proxy/noproxyTCP{}.txt".format(str(size),str(size)),serverName,working_directory)
            serverP1.wait()
            clean_everything();
            time.sleep(3);
            
            
def proxy_UDP_testing():
    #dpdk proxy
    # server = run_command("sh network_scripts/proxy_setup_server.sh",serverName,working_directory)
    # server.wait()
    for i in range(5):
        for size in range(100,1300,100):        
            clientP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",clientName,working_directory)
            time.sleep(3)
            clientP2 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,working_directory)
            time.sleep(3)
            serverP2 = run_command("sh exec_scripts/proxy2.sh >> EverythingTesting/data/proxy/proxyUDP{}.txt".format(str(size)),serverName,working_directory)
            time.sleep(3)
            serverP1 = run_command("sh exec_scripts/proxy1.sh {} 1 >> /dev/null".format(str(size)),serverName,working_directory)
            serverP2.wait()
            clean_everything();
            time.sleep(3);
    #forwarder
    
    # server = run_command("sudo ip -all netns delete  ",serverName,working_directory)  
    # server.wait()   
    # for i in range(5):
    #     for size in range(100,1300,100):        
    #         clientP1 = run_command("sh exec_scripts/dpdk_relay2.sh >> /dev/null",clientName,working_directory)
    #         time.sleep(3)
    #         clientP2 = run_command("sh exec_scripts/dpdk_relay1.sh >> /dev/null",clientName,working_directory)
    #         time.sleep(3)
    #         serverP2 = run_command("sh exec_scripts/proxy2.sh >> EverythingTesting/data/proxy/noproxyUDP{}.txt".format(str(size)),serverName,working_directory)
    #         time.sleep(3)
    #         serverP1 = run_command("sh exec_scripts/proxy1.sh {} 10 >> /dev/null".format(str(size)),serverName,working_directory)
    #         serverP2.wait()
    #         clean_everything();
    #         time.sleep(3);
    #         print("Size {} finished",size)
            
            
            
    
    
    

#############PROXY TESTING#####################






if __name__ == "__main__":
    #test_handshake()
    #test_server_scaling()
    #test_batching2()
    #test_congestion_dpdk()
    #test_congestion_nodpdk()
    #test_batching_noCC_noPacing()
    #test_congestion_big_dpdk()
    #test_batching()
    #test_batching()
    #test_throughput()
    #test_handshake_simple()
    #test_handshake()
    #test_request()
    #test_RSS_15()
    #test_throughput_without_encryption()
    #test_RSS_8()
    #test_RSS_8_X()
    #test_throughput256()
    #test_throughput128()
    #test_throughput20()
    #test_batching_fixed_RX64()
    proxy_UDP_testing()
        
        
    

