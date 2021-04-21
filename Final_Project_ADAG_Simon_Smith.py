# Author: Simon Smith

"""
(for each text)
0. read text from PDF into text file
1. identify acronyms, gather surrounding text
2. guess acronym meanings
3. print pretty list of acronyms
"""
"""
Requires Xpdf reader and path to its executable
"""

import os
import subprocess
import chardet
import re
from nltk.corpus import stopwords as stopword_file

# set to true for debug info
Verbose = True

# initialize stopwords
stopwords = set(stopword_file.words('english'))


### ENTER PDF SOURCE FOLDER's PATH BELOW ###
source_path = r"C:\Users\simon\OneDrive\Desktop\360_final_files_test"
source_files = os.listdir(source_path)

if Verbose:
    print("Source files: ",source_files,'\n')


### function creates a text file of a PDF in the same folder (and with the same name) as the PDF. ###
### Requires Xpdf commandline tool, and an updated path to it, to use this function               ###

def pdf_to_text(pdf_path):
    pdftotextprogram_path = "C:\\Users\\simon\\Downloads\\xpdf-tools-win-4.03\\bin64\\pdftotext.exe"
    # make txt files for each pdf (pdfs are unchanged)
    subprocess.run((pdftotextprogram_path + ' ' + pdf_path),shell=True)

# make a txt copy of each pdf in source folder #
for filename in source_files:
    if filename.endswith('.pdf'):
        # set absolute path for pdf, and run pdf_to_text
        pdf_abs_path = source_path + '\\' + filename
        pdf_to_text(pdf_abs_path)

        if Verbose:
            print("Wrote .txt file for ",pdf_abs_path)

### read in text from a text file, return list of successful acronymic sequences
def find_acronyms(text_path):


    # open file as bytes, determine encoding, close byte reading
    with open(text_path,mode='rb') as encodedFile:
        file_bytes = encodedFile.read()
        file_encoding = chardet.detect(file_bytes)['encoding']

    # open file with correct encoding, identify acronymic sequences, print to screen
    with open(text_path,'r',encoding=file_encoding) as infile:
        if Verbose:
            print("(Reading ",text_path," with ",file_encoding," encoding.)\n")
        file_text = infile.read()
        acronym_and_phrase = []

        # add sequences of a string of 2 or more capital letters
        #capital_sequences = re.findall(r'[A-Z]{2,}',file_text)

        # add parenthetical acronyms (capitals, whtspace in parentheses with optional -s), stripped of parentheses
        # ex, {'LDV', 'ODEs', 'PAM', 'ICTV', 'DTP', 'SHFV', 'PRRSV', 'NTRs', 'EAV'}
        parenthetical_sequences = set([phrase.strip('()') for phrase in re.findall(r'\([-A-Zs\s]*\)',file_text)])
        parenthetical_sequences = [item for item in parenthetical_sequences if len(item) > 1]

        # for an acronym of N letters, find up to N+N-1 words before and after the acronym in the text
        for acronym in parenthetical_sequences:

            # depluralizes the acronym
            acronym = acronym.strip('s')

            # how many words to look behind the current word for acronomied phrase
            search_radius = 2*len(acronym)-1
            # below term is any word or words up to the search radius plus the acronym
            regex_search_term = search_radius * (r'(\b\w*\b[-\s])?') + '\(' + acronym
            # the result of the regex is a list, all toLower
            #print("Regex results: ",[item for item in re.findall( regex_search_term, file_text )])

            # regex results based on regex_search_term. May return more than one term: [(first)(second)]
            for phrase in re.findall( regex_search_term, file_text ):

                # clean blank entries and terminal '\n' from phrase
                phrase = [word.strip('\n-') for word in phrase if word]

                # if the capture cell isn't blank, grab the initial (made lowercase) of each word, join as a string
                initials = ''.join([initial[0].upper() for initial in list(phrase) if initial])

                print("Phrase: ",phrase," Initials: ",initials," Acronym:", acronym)
                print(' '.join(phrase))


                # find appropriate phrase that acronym represents and store it to return later#

                # if the initials are fewer than the acronym, no dice.
                #   Ex, Initials:  EV  Acronym: LDV
                if len(initials) < len(acronym):
                    continue

                # if the initials equal the acronym, or the acronym with a lowercase s, return the phrase buffer
                #   Ex, Initials:  EAV  Acronym: EAV -OR- Initials:  NTR  Acronym: NTRs
                elif (initials == acronym):
                    acronym_and_phrase.append([acronym, phrase])
                    #print([acronym, phrase])

                # if the phrase ends with the acronym, peel a word off the back for every acronym letter
                #   Ex, Initials:  WBHGT  Acronym: HGT
                elif initials.endswith(acronym):
                    # append to the acronym_and_phrase bank the acronym, and the last (length of acronym) words in phrase
                    acronym_and_phrase.append([acronym, phrase[-len(acronym):]])
                    #print([acronym, phrase[-len(acronym):]])

                # if the phrase has stopwords, try matching the acronym to the stopword-less phrase
                #   Ex, Initials:  ICOTTOV  Acronym: ICTV   Phrase:  ['International ', 'Committee ', 'on ', 'the', 'Taxonomy ', 'of ', 'Viruses ']
                else:
                    # try matching initials in order, with whatever crap comes between them
                    # go through the letters of the INITIALS one by one, asking if they're the next letter of ACRONYM

                    # for iterating through letters of the acronym
                    acronym_index = 0

                    # for iterating through initial letters of the phrase, to compare to acronym letters
                    for index in range(len(initials)):
                        if initials[index] == acronym[acronym_index]:
                            # see if the next acronym letter is in the target phrase
                            acronym_index += 1

                        # if the length of the index is the size of its length, it's all been found! Report it!
                        if acronym_index == len(acronym):
                            print("Final product for final ELSE test: ",[acronym, phrase[:index]])


            print() #formatting

    return acronym_and_phrase


for file in os.listdir(source_path):
    # only look at the generated (or original) .txt files, not the pdfs!
    if file.endswith('.txt'):
        txt_abs_path = source_path + '\\' + file
        if Verbose:
            print("\nFinding acronyms for ",txt_abs_path)
        print(find_acronyms(txt_abs_path))



"""
Notes on defining acronomy:
    The most common way to do acronyms is like so
    where '1' is what the acronym stands for, and
    '2' is the acronym itself
    
        1 (2) 
        
        1 can be...
        separated by hyphens:
            "definition-theorem-proof (DTP)"
        capitalized:
            "International Committee on the Taxonomy of Viruses (ICTV)"
        or space-separated:
            "equine arteritis virus (EAV)" 
        of mixed space and hyphen separated:
            "non-translated regions (NTRs)"
        or more words than the acronym, especially stopwords:
            "porcine reproductive and respiratory syndrome virus (PRRSV)"
            ('and' disappears)
            
        2 can have...
        a lowercase 's' on the end for plurality
            "non-translated regions (NTRs)"
        fewer letters than there are in the represented phrase, especially stopwords
            "porcine reproductive and respiratory syndrome virus (PRRSV)"
            ('and' disappears)
            
        
"""