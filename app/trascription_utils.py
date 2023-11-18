def common_ss(str1,str2):
    list1 = list(str1)
    list2 = list(str2)

    m = len(list1)
    n = len(list2)
    table = [[0 for j in range(n+1)] for i in range(m+1)]

    for i in range(1, m+1):
        for j in range(1, n+1):
            if list1[i-1] == list2[j-1]: 
                table[i][j] = table[i-1][j-1] + 1
            else:
                table[i][j] = max(table[i-1][j], table[i][j-1])

    
    common_string = []
    i = m
    j = n
    while i > 0 and j > 0:
        if list1[i-1] == list2[j-1]: 
            common_string.append(list1[i-1])
            i -= 1
            j -= 1
        elif table[i-1][j] > table[i][j-1]: 
            i -= 1
        else:
            j -= 1

    common_string.reverse()
    final_string=""
    common_string = "".join(common_string)
    all_words=set(str1.split()+str2.split())
    for word in common_string.split():
        if word in all_words:
            final_string=final_string+" "+word
    return final_string.strip()

def calculate_similarity(str1,str2,substr):
    total_len=(len(str1)+len(str2))/2
    sub_len=len(substr)
    return (sub_len/total_len)*100