import sys
import os
import requests
import time


def download(elem):
    file_path = elem["path"]
    # проверяем существует ли уже файл
    if os.path.isfile(file_path):
        print("E{} already exists".format(elem["episode"]))
        return -1
    start_time = time.time()
    # эпизоды до 10-ого и после него имеют немного разные шаблоны адресов (из-за одного нуля перед номером эпизода)
    if elem["episode"] < 10:
        url = "https://galyonkin.com/wp-content/podcast/Galyonkin-S0{}E0{}.mp3".format(elem["season"], elem["episode"])
    else:
        url = "https://galyonkin.com/wp-content/podcast/Galyonkin-S0{}E{}.mp3".format(elem["season"], elem["episode"])
    req = requests.get(url)
    # открываем и записываем файл
    file = open(file_path, 'wb')
    for chunk in req.iter_content(chunk_size=1048576):
        file.write(chunk)
    file.close()
    print("E{} downloaded in {:.2f} seconds".format(elem["episode"], time.time()-start_time))
    return 1


def main():
    print("KDI Podcast Downloader ver. 0.3 Alpha")
    print("Обновляем базу подкастов...")
    # Начинаем с первого эпизода первого сезона
    # Инкрементируем эпизод до тех пор, пока не возникнет ошибка 404
    # Она означает, что текущий эпизод принадлежит к следующему сезону или является последним
    # Увеличиваем сезон на 1
    # Если ошибка 404 возникает снова, то эпизод точно последний
    # Записываем первый и последний эпизоды сезона
    first_episode_of_season = 1
    episode = 1
    season = 1
    seasons = []
    previous404 = False
    while True:
        if episode < 10:
            url = "http://galyonkin.com/wp-content/podcast/Galyonkin-S0{}E0{}.mp3".format(str(season), str(episode))
        else:
            url = "http://galyonkin.com/wp-content/podcast/Galyonkin-S0{}E{}.mp3".format(str(season), str(episode))
        r = requests.head(url)
        if r.status_code == 404:
            if previous404:
                seasons.append({"n": season - 1, "first": first_episode_of_season, "last": episode - 1})
                break
            else:
                previous404 = True
                season += 1
        else:
            if previous404:
                seasons.append({"n": season - 1, "first": first_episode_of_season, "last": episode - 1})
                first_episode_of_season = episode
            previous404 = False
            episode += 1
    print("\nДоступные сезоны и эпизоды:")
    for season in seasons:
        print("Сезон {}: {}-{} эпизоды".format(season["n"], season["first"], season["last"]))

    # определяем путь, куда будем сохранять файлы
    path_exists = False
    path = "default"
    while not path_exists:
        print("\nКорректно введите путь к папке, куда будут загружены подкасты")
        if sys.platform.startswith("win"):
            print(r"Вместо одного слэша '\' пишите два '\\'")
        print("Или напишите default, чтобы создать папку KDI в директории пользователя")
        path = input("Путь: ")
        if path == "default":
            path = os.path.expanduser("~/KDI")
            if not os.path.exists(path):
                os.mkdir(path)
        path_exists = os.path.exists(path)
    print("Папка загрузки: {}".format(path))

    episodes = []
    for season in seasons:
        for i in range(season["first"], season["last"] + 1):
            if sys.platform == "linux":
                file_path = path + "/S{}E{}.mp3".format(season["n"], i)
            elif sys.platform.startswith("win"):
                file_path = path + "\\S{}E{}.mp3".format(season["n"], i)
            else:
                file_path = path + "/S{}E{}.mp3".format(season["n"], i)
            episodes.append({"season": season["n"], "episode": i, "path": file_path})

    print("\nS1, или S2, или S3 и т.д. - скачать определенный сезон")
    print("E1, или E2, или E3 и т.д. - скачать определенный эпизод")
    print("all - скачать все выпуски")
    print("Загрузка большого числа эпизодов может занять достаточно большое время")
    print("Если в папке уже есть скачанные эпизоды, они не будут заново скачиваться")
    print("quit, q - команды выхода из загрузчика")
    command = "start"
    while command not in ["quit", "q"]:
        command = input("Напишите команду: ")
        try:
            episodes_to_download = []
            if command.startswith("S"):
                n_season = int(command[1:])
                for episode in episodes:
                    if episode["season"] == n_season:
                        episodes_to_download.append(episode)
            elif command.startswith("E"):
                n_episode = int(command[1:])
                episodes_to_download = []
                for episode in episodes:
                    if episode["episode"] == n_episode:
                        episodes_to_download.append(episode)
                        break
            elif command.startswith("all"):
                episodes_to_download = episodes
            for episode_to_download in episodes_to_download:
                download(episode_to_download)
        except:
            print("Возникла ошибка из-за неправильной команды или плохого соединения")


if __name__ == "__main__":
    main()
