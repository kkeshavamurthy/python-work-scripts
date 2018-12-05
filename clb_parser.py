from os import sys
import logging

'''
  Python script to parse the provided AP logs
  and print the number of times target-asserts,
  kernel panics & NSS Core dumps were seen.
  Takes 1 or more AP log files as input
  Usage: python clb_parser.py <path-to-logfile1> <path-to-logfile2>
'''

# Init logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_args():
    if len(sys.argv) < 2:
        print("Please provide atleast 1 argument")
        sys.exit()    

def parse_file(filename, num):

    # Init 3 dicts to store the error name & frequency
    ap_asserts = {}
    ap_panics = {}
    ap_nssdumps = {}

    # Pattern to look for each error. 
    patterns = ['PC is at',\
                'NSS core 0 signal COREDUMP COMPLETE',\
                'Fatal error received from wcss software']
    
    with open(filename, 'r') as fh:
        for line in fh:
            # Check for Kenel Panic Line
            if patterns[0] in line:
                logging.debug("Panic Line: {0}".format(line))
                
                panic_name = get_panic(line.strip())
                logging.debug("Panic Name: {0}".format(panic_name))

                add_panics(ap_panics, panic_name)
                logging.debug(ap_panics)
                
            # Check for NSS Dump Line
            elif patterns[1] in line:
                logging.debug("NSS Dump Line: {0}".format(line))
                
                nssdump_name = get_nssdump(line.strip())
                logging.debug("NSS Dump Name:{0}".format(nssdump_name))

                add_nssdumps(ap_nssdumps, nssdump_name)
                logging.debug(ap_nssdumps)

            # Check for Target Assert Line & parse the 4th line
            # as it has the assert name. 
            elif patterns[2] in line:
                fh.readline()
                fh.readline()
                fh.readline()
                line = fh.readline()
                logging.debug("Assert Line: {0}".format(line))

                assert_name = get_assert(line)
                logging.debug("Assert Name: {0}".format(assert_name))
                
                add_asserts(ap_asserts, assert_name)
                logging.debug(ap_asserts)

    # Print info 
    print_info(ap_asserts, ap_panics, ap_nssdumps, num)

def get_panic(line):
    return(line.split(']')[1].split(' ')[4])
    
def add_panics(ap_panics, panic_name):
    if panic_name in ap_panics:
        ap_panics[panic_name] += 1
    else:
        ap_panics[panic_name] = 1
    
def get_nssdump(line):
    return(line.split(']')[1])

def add_nssdumps(ap_nssdumps, nssdump_name):
    if nssdump_name in ap_nssdumps:
        ap_nssdumps[nssdump_name] += 1
    else:
        ap_nssdumps[nssdump_name] = 1

def get_assert(line):
    assert_name = line.split(']')[1].split(' ')[1]
    if assert_name == '\n' or assert_name == '':
        return("NoNameAssert")
    else:
        return(assert_name)

def add_asserts(ap_asserts, assert_name):
    if assert_name in ap_asserts:
        ap_asserts[assert_name] += 1
    else:
        ap_asserts[assert_name] = 1

def print_info(ap_asserts, ap_panics, ap_nssdumps, num):
    print("--------------------")
    print("AP-",(num)," Results")
    print("--------------------")
    print("Target Asserts:")
    for assert_name in ap_asserts:
        print('  ',assert_name,'-->',ap_asserts[assert_name],'times')

    print("Kernel Panics:")
    for panic_name in ap_panics:
        print('  ',panic_name,'-->',ap_panics[panic_name],'times')

    print("NSS Core Dumps:")
    for nssdump_name in ap_nssdumps:
        print('  ',nssdump_name,'-->',ap_nssdumps[nssdump_name],'times')

    print("--------------------")


if __name__ == "__main__":
    check_args()
    # Call the parse function for each log file. 
    for i in range(1,len(sys.argv)):
        parse_file(sys.argv[i],i)
    
