import matplotlib.pyplot as plt
import numpy as np

def process():
    w = open("stats.txt", "r", encoding="utf-8")

    list = []

    for t in w.readlines():
        info = t.split(":")
        num_of_words = info[3]
        #num_of_concepts = len(info[4].split("|"))
        list.append((info[0], num_of_words, info[4].split("|")))

    return list

def gstats1():

    list_data = process()
    data = [round(int(s2), -3) for (s1, s2, s3) in list_data]

    len_q = [len(s3) for (s1, s2, s3) in list_data]

    plt.barh(data, len_q, align='center', height=500, alpha=0.5, orientation='horizontal')
    plt.yticks(np.arange(0, max(data) + 1, 2000))
    plt.xlabel('Broj koncepata')
    plt.ylabel('Broj reči unutar dokumenta (zaokruženo na najbližu hiljadu)')
    plt.show()


def gstats2():
    list_data = process()

    list_of_all_concepts = [s3 for (s1, s2, s3) in list_data]
    all_info = {}
    for list_of_concepts in list_of_all_concepts:
        for element in list_of_concepts:
            element = element.strip()
            if element in all_info:
                all_info[element] = all_info[element] + 1
            else:
                all_info[element] = 1
    top_10 = dict(sorted(all_info.items(), key=lambda x: x[1], reverse=True)[:10])
    top_10 = sorted(top_10.items(), key=lambda x: x[1])

    plt.barh([s1 for (s1, s2) in top_10], [s2 for (s1, s2) in top_10], align='center', height=0.5, alpha=0.5)

    plt.xlabel('Broj pojavljivanja koncepta na nivou svih dokumenata')
    #plt.ylabel('Koncept')
    plt.title("10 najčešćih koncepata")
    #plt.rcParams['font.size'] = 24
    plt.show()

def stats3():
    list_data = process()
    list_of_all_concepts = [s3 for (s1, s2, s3) in list_data]
    all_info = {}
    num = 0
    for list_of_concepts in list_of_all_concepts:
        if len(list_of_concepts) > 15:
           num = num + 1
    print(num)
if __name__ == "__main__":
    # gstats1()
    gstats2()
    # stats3()