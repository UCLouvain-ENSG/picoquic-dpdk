#!/usr/bin/env python3

from http import client
from subprocess import Popen, PIPE
import subprocess

import json
import shlex
import time

from toml import TomlDecodeError

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
dpdk_picoquic_directory = '/home/nikita/memoire/dpdk_picoquic'
wireguard_directory = '/home/nikita/memoire/wireguard'
picotls_directory = '/home/nikita/memoire/picotlsClean'
quiche_directory = '/home/nikita/memoire/quic-implems-dockers/quiche-cloudflare'
msquic_directory = '/home/nikita/memoire/msquic'


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
    
def run_command_read_STDOUT(command,host,directory):
    cmds = ['ssh', host,'cd {}; {}'.format(directory,command)]
    print(cmds)
    return Popen(cmds, stdout=subprocess.PIPE, stderr=None, stdin=None)

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
    p1 = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    p2 = run_command("sh killForwarder.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    p3 = run_command("sh killiperf3.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    p4 = run_command("sh killUDP.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    p5 = run_command("sudo kill $(pidof cli) >> /dev/null",clientName,dpdk_picoquic_directory)
    p6 = run_command("sudo kill $(pidof secnetperf) >> /dev/null",serverName,dpdk_picoquic_directory)
    p7 = run_command("sudo kill $(pidof generic-http3-server) >> /dev/null",serverName,dpdk_picoquic_directory)
    for p in [p1,p2,p3,p4,p5,p6,p7]:
        p.wait()
    
def proxy_TCP_testing():
    #dpdk proxy
    def mykiller():
        p1a = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        p1b = run_command("sh killDpdkProcess.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        p2a = run_command("sh killiperf3.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        p2b = run_command("sh killiperf3.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        p3a = run_command("sh killForwarder.sh >> /dev/null",clientName,dpdk_picoquic_directory)
        p3b = run_command("sh killForwarder.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        for p in [p1a,p1b,p2a,p2b,p3a,p3b]:
            p.wait()
        
    server = run_command("sh network_scripts/proxy_setup_server_Z.sh",serverName,dpdk_picoquic_directory)
    server.wait()
    client = run_command("sh network_scripts/proxy_setup_client_Z.sh",clientName,dpdk_picoquic_directory)
    client.wait()
    # for i in range(5):
    #     for size in range(100,1300,100):
    #         serverP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP1 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         serverP2 = run_command(nss + " iperf3 -s >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP2 = run_command(nsc + " iperf3 -M {} -c 3.0.0.1 -t 30 >> EverythingTesting/data/proxy/proxyTCP{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
    #         clientP2.wait()
    #         mykiller();
    #         time.sleep(3);
            
    # for i in range(5):
    #     for size in range(100,1300,100):
    #         serverP1 = run_command("sh exec_scripts/serverNoDPDKProxy.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP1 = run_command("sh exec_scripts/clientNoDPDKProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         serverP2 = run_command(nss + " iperf3 -s >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP2 = run_command(nsc + " iperf3 -M {} -c 3.0.0.1 -t 30 >> EverythingTesting/data/proxy/proxyTCPNoDPDK{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
    #         clientP2.wait()
    #         mykiller();
    #         time.sleep(3);
       
    for i in range(5):
        for size in range(100,1300,100):        
            serverP1 = run_command("sh exec_scripts/dpdk_relay2.sh >> /dev/null",serverName,dpdk_picoquic_directory)
            time.sleep(3)
            clientP1 = run_command("sh exec_scripts/dpdk_relay1.sh >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            serverP2 = run_command(nss + " iperf3 -s >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            clientP2 = run_command(nsc + " iperf3 -M {} -c 3.0.0.1 -t 30 >> EverythingTesting/data/proxy/noproxyTCP{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
            clientP2.wait()
            mykiller();
            time.sleep(3);
            
           
def proxy_TCP_noDPDK():
    server = run_command("sh network_scripts/proxy_setup_server.sh",serverName,dpdk_picoquic_directory)
    server.wait()
    for i in range(5):
        for size in range(100,1300,100):
            clientP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            clientP2 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(3)
            serverP2 = run_command(nss + " iperf3 -s >> /dev/null",serverName,dpdk_picoquic_directory)
            time.sleep(3)
            serverP1 = run_command(nsc + " iperf3 -M {} -c 10.10.0.2 -t 30 >> EverythingTesting/data/proxy/proxyTCP{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
            serverP1.wait()
            clean_everything();
            time.sleep(3);
     
def proxy_UDP_testing():
    #dpdk proxy
    # # server.wait()
    cmd1 = run_command("sudo ip -all netns delete  ",serverName,dpdk_picoquic_directory)
    cmd1.wait()

    cmd2 = run_command("sh network_scripts/proxy_setup_server.sh",serverName,dpdk_picoquic_directory)
    cmd2.wait()
    
   
    
    for i in range(5):
        killer = run_command("sh killiperf3.sh >> /dev/null",serverName,dpdk_picoquic_directory)
        killer.wait()
        cmd1 = nss + " iperf3 -s -p 5000 -f m >> /dev/null"
        cmd2 = nss + " iperf3 -s -p 5001 -f m >> /dev/null"
        cmd = "{} & {}".format(cmd1,cmd2)
        Server = run_command(cmd,serverName,dpdk_picoquic_directory)
        time.sleep(5)
        for size in range(100,1300,100):
            my_range = []
            if size == 100:
                my_range = range(int(10*size),size*20,int(size))
            elif size<700:
                my_range = range(int(3*size),size*15,int(size/2))
            else:
                my_range = range(int(2*size),size*7,int(size/2))
            for b in my_range:
                formater1 = run_command("echo -n {} Mbps iteration : {} >> EverythingTesting/data/proxy/proxyUDP_{}1.txt".format(b,size,i),clientName,dpdk_picoquic_directory)
                formater2 = run_command("echo -n {} Mbps >> EverythingTesting/data/proxy/proxyUDP_{}2.txt ".format(b,size),clientName,dpdk_picoquic_directory)
                formater1.wait()
                formater2.wait()
                clientP1 = run_command("sh exec_scripts/serverProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
                time.sleep(5)
                clientP2 = run_command("sh exec_scripts/clientProxy.sh >> /dev/null",clientName,dpdk_picoquic_directory)
                time.sleep(5)
                cmd1 = nsc + " iperf3 -c 10.10.0.2 --cport 5500 -p 5000 -l 1200 -u -b {}M -t 10 -f m | grep 'receiver' >> EverythingTesting/data/proxy/proxyUDP_{}1.txt".format(b,size)
                cmd2 = nsc + " iperf3 -c 10.10.0.2 --cport 5600 -p 5001 -l 1200 -u -b {}M -t 10 -f m | grep 'receiver' >> EverythingTesting/data/proxy/proxyUDP_{}2.txt".format(b,size)
                cmd = "{} & {}".format(cmd1,cmd2)
                Cli = run_command(cmd,serverName,dpdk_picoquic_directory)
                Cli.wait()
                time.sleep(2)
                killer1 = run_command("sh killDpdkProcess.sh >> /dev/null",clientName,dpdk_picoquic_directory)
                killer1.wait()
    killer2 = run_command("sh killiperf3.sh >> /dev/null",serverName,dpdk_picoquic_directory)
    killer2.wait()
    #forwarder    
    # for i in range(5):
    #     for size in range(100,1300,100):        
    #         clientP1 = run_command("sh exec_scripts/dpdk_relay2.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         clientP2 = run_command("sh exec_scripts/dpdk_relay1.sh >> /dev/null",clientName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         serverP2 = run_command("sh exec_scripts/proxy2.sh >> EverythingTesting/data/proxy/noproxyUDP{}.txt".format(str(size)),serverName,dpdk_picoquic_directory)
    #         time.sleep(3)
    #         serverP1 = run_command("sh exec_scripts/proxy1.sh {} 10 >> /dev/null".format(str(size)),serverName,dpdk_picoquic_directory)
    #         serverP2.wait()
    #         clean_everything();
    #         time.sleep(3);
    #         print("Size {} finished",size)
            
            
            
def wireguard_testing():
    cmd1 = run_command("sudo ip -all netns delete  ",serverName,dpdk_picoquic_directory)
    cmd1.wait()
    cmd2 = run_command("sh network_scripts/wireguard_server_setup.sh",serverName,dpdk_picoquic_directory)
    cmd2.wait()
    cmd3 = run_command("sh network_scripts/wireguard_client_setup.sh",clientName,dpdk_picoquic_directory)
    cmd3.wait()

    for i in range(5):
        for size in range(100,1300,100):
            server = run_command(nss + " iperf3 -s >> /dev/null",clientName,dpdk_picoquic_directory)
            time.sleep(5)
            client = run_command(nsc + " iperf3 -M {} -c 3.0.0.1 -t 30 >> EverythingTesting/data/proxy/wireguardTCP{}.txt".format(str(size),str(size)),serverName,dpdk_picoquic_directory)
            client.wait()
            clean_everything();
            time.sleep(3)
    

#############PROXY TESTING#####################



#############Big Comparison Tests#####################

def picotls_test():
    for i in range(5):
        server = run_command("sudo sh server.sh &>> {}/EverythingTesting/data/cmp/picotls.txt".format(dpdk_picoquic_directory),serverName,picotls_directory)
        time.sleep(3)
        client = run_command("sudo sh client.sh",clientName,picotls_directory)
        time.sleep(30)
        killer1 = run_command("sudo kill $(pidof cli)",clientName,dpdk_picoquic_directory)
        killer1.wait()
        killer2 = run_command("sudo kill $(pidof cli)",serverName,dpdk_picoquic_directory)
        killer2.wait()
        time.sleep(5)    
def quiche_test():
    for i in range(5):
        server = run_command("sh server.sh",serverName,quiche_directory)
        client = run_command("sh client.sh >> {}/EverythingTesting/data/cmp/quiche.txt".format(dpdk_picoquic_directory),clientName,quiche_directory)
        client.wait()
        clean_everything()
        time.sleep(3)
    
    
def msquic_test():
    for i in range(5):
        server = run_command("sh server.sh",serverName,msquic_directory)
        client = run_command("sh client.sh >> {}/EverythingTesting/data/cmp/msquic.txt".format(dpdk_picoquic_directory),clientName,msquic_directory)
        client.wait()
        clean_everything()
        time.sleep(3)
    

#############Big Comparison Tests#####################






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
    #proxy_UDP_testing()
    #proxy_UDP_testing()
        
        
    #picotls_test()
    #quiche_test()
    #msquic_test()
    
    #wireguard_testing()
    #proxy_UDP_testing()
    proxy_TCP_testing()
        
    

