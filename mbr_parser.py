import sys 
import struct 


_PTE_STRUCT = "<1s3s1s3sII"
_EBR_STRUCT = "<446s16s16s16s16s2s"
_PARTITION_START = 446
_SECTOR_SIZE = 512

def usage():
    print("Usage : python mbr_parser.py <image name> ")

types = {
    b'\x07' : "NTFS",
    b'\x05' : "Extend",
    b'\0B' : "FAT32(CHS)",
    b'\0C' : "FAT32(LBA)"
}


if len(sys.argv)!=2:
    usage()
    exit(-1)

image_name = sys.argv[1]

try:
    image_file = open("./"+image_name,'rb')
except:
    print("can not open file")
    exit(-1)

partionTableEntries = []

#Parse Table Entries
for i in range(4):
    image_file.seek(_PARTITION_START+ 16*i)
    TableEntry = image_file.read(16)
    partionTableEntries.append(TableEntry)

partitions = []

#MBR 엔트리 분석
for idx,entry in enumerate(partionTableEntries):
    partitionTableEntry = struct.unpack(_PTE_STRUCT,entry)
    isActive = partitionTableEntry[0]
    CHS_Address = partitionTableEntry[1]
    partionType = partitionTableEntry[2]
    CHS_Address = partitionTableEntry[3]
    LBA_Address = partitionTableEntry[4]
    Num_of_Sector = partitionTableEntry[5]
    startAddress = LBA_Address*_SECTOR_SIZE
    size = Num_of_Sector*_SECTOR_SIZE
    if types[partionType]=="Extend":
        #EBR로 이동 및 Read 
        image_file.seek(startAddress*512)
        EBR = image_file.read(_SECTOR_SIZE)
        EBR = struct.unpack(_EBR_STRUCT,EBR)
        while True:
            partition = EBR[1]
            partiton = struct.unpack(_PTE_STRUCT,partition)
            isActive = partiton[0]
            CHS_Address = partiton[1]
            partionType = partiton[2]
            CHS_Address = partition[3]
            LBA_Address = partition[4]
            Num_of_Sector = partition[5]
            startAddress = LBA_Address*_SECTOR_SIZE
            size = Num_of_Sector*_SECTOR_SIZE
            partitions.append({
                "index" : idx+1,
                "FilsSystem" : types[partionType],
                "StartAddress" : str(startAddress),
                "Size" : str(size)
            })

            nextEBR = EBR[2]
            if(int.from_bytes(nextEBR)==0):
                break

    else:
        partitions.append({
            "index" : idx+1,
            "FilsSystem" : types[partionType],
            "StartAddress" : str(startAddress),
            "Size" : str(size)
        })


for i in partitions:
    print("index : "+str(i))
    print("     FileSystem : ")
    print("     StartAddress : ")
    print("     Size : ")