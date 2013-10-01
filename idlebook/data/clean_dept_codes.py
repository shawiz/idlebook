def clean_code():
    old_file_name = "./name2dep_normalized.txt"
    new_file_name = "./dept_codes.txt"
    
    old_file = open(old_file_name, "r").readlines()
    codes = []
    
    for line in old_file:
        words = line.split(';')
        codes.append(words[1].strip())
    codes.sort()

    #write data
    new_file = open(new_file_name,'w')
    for code in codes:
        new_file.write(code + '\n')
    new_file.close()

if __name__ == "__main__":
#    clean_code()