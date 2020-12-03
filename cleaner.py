fname = "DataScrapper/tools/scrappedData.txt"
newname = "DataScrapper/tools/newData.txt"

def clean_sugar(fname):
    bad_words = ['sugar', 'vanilla', 'baking', 'powder']
    with open(fname) as oldfile, open(newname, 'w') as newfile:
        for line in oldfile:
            if not any(bad_word in line for bad_word in bad_words):
                newfile.write(line)

clean_sugar(fname)