from funcs.comment_analysis import request
from colorama import init, Fore

init(convert=True, autoreset=True)

def main():
    while True:
        a = input(Fore.CYAN + "> " + Fore.LIGHTCYAN_EX)
        resp = request(a)
        b = []

        for k, v in resp.items():
            val = v["summaryScore"]["value"]
            if val > 0.8:
                vs = Fore.RED + str(val)
            elif val > 0.6:
                vs = Fore.LIGHTRED_EX + str(val)
            elif val > 0.4:
                vs = Fore.LIGHTYELLOW_EX + str(val)
            elif val > 0.2:
                vs = Fore.LIGHTGREEN_EX + str(val)
            else:
                vs = Fore.LIGHTCYAN_EX + str(val)
            
            b.append(((Fore.LIGHTCYAN_EX + k).replace("_", " "), vs))

        b.sort()

        for i in b:
            k, v = i
            print("{0:<30}{1:>15}".format(k.capitalize(), v))

main()
