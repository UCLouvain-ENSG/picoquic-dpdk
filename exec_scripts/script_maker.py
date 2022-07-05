import os

default_string = "sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 0-{} {} -- -A 50:6b:4b:f3:7c:71 -D -* 32 -@ 32 10.100.0.2 4443 /10000000000"
    
def retrieve_cards():
    cards = open('exec_scripts/cards.txt', 'r')
    lines = cards.readlines()
    counter = 0
    trueCounter = 0
    ret = ''
    for line in lines:
        if(counter < 4):
            counter +=1
        else:
            trueCounter += 1
            line_as_array = line.split()
            card_id = line_as_array[0]
            ret += '-a 0000:{} '.format(card_id)
    return trueCounter,ret

def make_script():
    length,NICs = retrieve_cards()
    print(len(NICs))
    final_string = default_string.format(length,NICs)
    print(final_string)
    os.system(final_string)
   
   
make_script() 
    
    
