import re
import string


def find_longest_common_substring(text1: str, text2: str) -> str:
    """
    Find the longest common substring between two strings

    Parameters
    ----------
    text1: ``str``
        The first string
    text2: ``str``
        The second string

    Returns
    -------
    ``str``
        The longest common substring between the two strings
    """
    list1 = list(text1)
    list2 = list(text2)

    m = len(list1)
    n = len(list2)
    table = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if list1[i - 1] == list2[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])

    common_substring = []
    i = m
    j = n

    while i > 0 and j > 0:
        if list1[i - 1] == list2[j - 1]:
            common_substring.append(list1[i - 1])
            i -= 1
            j -= 1
        elif table[i - 1][j] > table[i][j - 1]:
            i -= 1
        else:
            j -= 1

    common_substring.reverse()
    final_string = ""
    common_substring = "".join(common_substring)
    all_words = set(text1.split() + text2.split())

    for word in common_substring.split():
        if word in all_words:
            final_string = final_string + " " + word

    return final_string.strip()


def calculate_similarity(text1: str, text2: str, common_substring: str) -> float:
    """
    Calculate the similarity between common substring and the average length of the two strings

    parameters:
    ----------
    text1: ``str``
        The first string
    text2: ``str``
        The second string
    common_substring: ``str``
        The longest common substring between the two strings

    Returns
    -------
    ``float``
        The similarity between the common substring and the average length of the two strings
    """
    total_len = (len(text1) + len(text2)) / 2
    sub_len = len(common_substring)
    
    return (sub_len / total_len) * 100


def clean_transcription(transcription: str) -> str:
    """
    Clean the transcription by removing all the punctuations and extra spaces

    Parameters
    ----------
    transcription: ``str``
        The transcription to be cleaned

    Returns
    -------
    ``str``
        The cleaned transcription
    """
    punctuations = string.punctuation + "।₹"
    transcription = transcription.translate(
        str.maketrans(punctuations, " " * len(punctuations))
    )
    transcription = re.sub(r"[\u200b\s]+", " ", transcription)

    return transcription.strip()
