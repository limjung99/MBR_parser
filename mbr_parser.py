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
        pivotAddress = startAddress
        offset = 0
        while True:
            nowAddress = pivotAddress+offset
            #EBR로 이동 및 Read 
            image_file.seek(nowAddress) # EBR 섹터 시작 주소 
            EBR = image_file.read(_SECTOR_SIZE) # 512 byte read 
            EBR = struct.unpack(_EBR_STRUCT,EBR)
            partition = EBR[1] 
            nextEBR = EBR[2]
            

            # 여기서부터는 상대 주소를 사용해서 file seek
            unpacked_partition = struct.unpack(_PTE_STRUCT,partition)
            isActive = unpacked_partition[0]
            CHS_Address = unpacked_partition[1]
            partionType = unpacked_partition[2]
            CHS_Address = unpacked_partition[3]
            LBA_Address = unpacked_partition[4]
            Num_of_Sector = unpacked_partition[5]
            startAddress = (nowAddress+LBA_Address)*_SECTOR_SIZE
            size = Num_of_Sector*_SECTOR_SIZE
            
            partitions.append([
                types[partionType],
                str(startAddress),
                str(size)
            ])

            if(int.from_bytes(nextEBR,byteorder='big')==0):
                break
            
            unpacked_nextEBR = struct.unpack(_PTE_STRUCT,nextEBR)
        
            isActive = unpacked_nextEBR[0]
            CHS_Address = unpacked_nextEBR[1]
            partionType = unpacked_nextEBR[2]
            CHS_Address = unpacked_nextEBR[3]
            start_Address = unpacked_nextEBR[4]
            Num_of_Sector = unpacked_nextEBR[5]

            offset = start_Address*_SECTOR_SIZE
            
            

    else:
        partitions.append([
            types[partionType],
            str(startAddress),
            str(size)
        ])



for i,partition in enumerate(partitions):

    print("index : "+str(i+1))
    print("     FileSystem : "+partition[0])
    print("     StartAddress : "+partition[1])
    print("     Size : "+partition[2])