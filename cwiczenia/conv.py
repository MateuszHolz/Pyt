import re
with open("conv.txt", 'w') as f:
    for i in open("liczby.txt", 'r').readlines():
        for j in re.split('[a-zA-Z]', i):
            try:
                f.write("Liczba parsowana to {}. {}, {}, {} odpowiednio system 2, 8, 16\n".format(j.rstrip(), bin(int(j)), oct(int(j)), hex(int(j))))
            except ValueError:
                try:
                    f.write("Byl problem, liczba byla prawdopodobnie floatem. Liczba parsowana (odcinajac czesc floatowa) to {}. ### {}, {}, {} odpowiednio system 2, 8, 16\n".format(j.rstrip(), bin(int(float(j))), oct(int(float(j))), hex(int(float(j)))))
                except ValueError:
                    continue
