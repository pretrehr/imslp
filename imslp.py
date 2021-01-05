import os
from subprocess import call



def download_pdf(file_link):
    for country_prefix in ["usimg", "euimg", "caimg"]:
        url_prefixes = ["imslp.simssa.ca", "ks4.imslp.net", "ks.imslp.net", "imslp.hk", "imslp.eu",
                        "petruccimusiclibrary.ca"]
        for prefix in url_prefixes:
            url = 'https://{}/files/imglnks/{}/{}'.format(prefix, country_prefix, file_link)
            target = url.split("/")[-1]
            if os.path.isfile(target):
                return
            wget = "curl --silent --url {} --output {}".format(url, target)
            call(wget)
            try:
                if os.path.getsize(target) > 1000:
                    return
            except FileNotFoundError:
                continue
            os.remove(target)
    print("******ERREUR*******", target)


def get_ids_piece(url):
    soup = BeautifulSoup(urllib.request.urlopen(url), features="lxml")
    for line in soup.find_all("a"):
        if "href" in line.attrs and "Special:ImagefromIndex" in line["href"]:
            id = line["href"].split("Special:ImagefromIndex/")[-1]
            for subline in line.findParent().findParent().findChildren("a", attrs={"class":"internal"}):
                if "pdf" in subline["href"]:
                    title = subline["href"].split("images/")[-1]
                    yield "/IMSLP{}-".format(id).join(title.rsplit("/", 1))


def download_pdfs_piece(url):
    for sheet_id in get_ids_piece(url):
        download_pdf(sheet_id)

def download_pdfs_composer(url):
    soup = BeautifulSoup(urllib.request.urlopen(url), features="lxml")
    composer_name = soup.find("h1").text.strip().split("Category:")[1]
    print(composer_name)
    if not os.path.isdir(composer_name):
        os.mkdir(composer_name)
    os.chdir(composer_name)
    dict_pieces = ast.literal_eval(str(soup).split("extend(catpagejs,{\"p1\":")[1].split("});")[0])
    for letter, pieces in dict_pieces.items():
        if not os.path.isdir(letter):
            os.mkdir(letter)
        os.chdir(letter)
        for piece in pieces:
            piece_name = piece
            if "|" in piece:
               piece_name = piece_name.split("|")[0]
               if not piece_name:
                   piece_name = piece.split("|")[1]
            url_piece = "https://imslp.org/wiki/"+urllib.parse.quote(piece_name).replace("%5C/", "%2F")
            for char in ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]:
                piece_name = piece_name.replace(char, " ")
            if not os.path.isdir(piece_name):
                os.mkdir(piece_name)
            elif "%2F" in url_piece:
                pass
            else:
                continue
            os.chdir(piece_name)
            print(piece_name)
            download_pdfs_piece(url_piece)
            os.chdir("..")
        os.chdir("..")
    os.chdir("..")