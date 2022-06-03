import datetime
from statistics import mean

if __name__ == '__main__':
    f = open('results.txt', 'r')
    times = []
    for line in f:
        if line[-1] == '\n':
            line = line[:-1]
        array = line.split(':')
        times.append(int(array[0])*3600 + int(array[1])*60 + float(array[2]))
    print(min(times))
    print(max(times))
    print(mean(times))