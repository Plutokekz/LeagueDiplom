import os.path

from .LeagueApi import get_summoner_profile_dict


def generate_diploma(name: str, out_path: str = None):
    path = "\\".join(os.path.abspath(__file__).split("\\")[:-2])
    if out_path is None:
        out_path = os.path.join(path, "diploma")

    d = get_summoner_profile_dict(name)
    with open(os.path.join(path, "template", "Urkunde.tex"), "r", encoding="utf-8") as fp:
        text = fp.read()
        for key, value in d.items():
            text = text.replace(f"${key}$", str(value))

        with open(os.path.join(out_path, f"{d['name']}.tex"), "w", encoding="utf-8") as fpw:
            fpw.write(text)

    file_path = os.path.join(out_path, f'{d["name"]}.tex')
    os.system(
        f"pdflatex -output-directory={out_path} -shell-escape -synctex=1 -interaction=nonstopmode -jobname={d['name']} -output-format=pdf {file_path}")
    return path, d['name']


def delete_diploma(name: str):
    path = "\\".join(os.path.abspath(__file__).split("\\")[:-2])
    os.remove(f"{os.path.join(path, name)}.aux")
    os.remove(f"{os.path.join(path, name)}.log")
    os.remove(f"{os.path.join(path, name)}.synctex.gz")
    os.remove(f"{os.path.join(path, name)}.tex")
    os.remove(f"{os.path.join(path, name)}.pdf")
