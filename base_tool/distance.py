def minEditDist(sm, sn):
    # if sm[0] != sn [0] or sm[1] != sn[1] or sm[2] != sn[2] or sm[3] != sn[3]:
    #     return len(sm)
    m, n = len(sm) + 1, len(sn) + 1

    # create a matrix (m*n)

    matrix = [[0] * n for i in range(m)]

    matrix[0][0] = 0
    for i in range(1, m):
        matrix[i][0] = matrix[i - 1][0] + 1

    for j in range(1, n):
        matrix[0][j] = matrix[0][j - 1] + 1

    cost = 0

    for i in range(1, m):
        for j in range(1, n):
            if sm[i - 1] == sn[j - 1]:
                cost = 0
            else:
                cost = 1

            matrix[i][j] = min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + cost)

    return 1 - matrix[m - 1][n - 1]/len(sm)

str2 = "К-з Зарафшон к-к Анжирзор д.."
str1 = 'К-з Зарафшон к-к Боги баланд д.0'
mindist=minEditDist(str1,str2)

print(mindist)

print(len(str1))