from os import listdir


class AudioFiles:
    def __init__(self, dirpath):
        self.dirpath = dirpath
        self.files = listdir(dirpath)

    def exists_files(self, filename):
        return filename in self.files

    def get_filepath(self, filename):
        return f"{self.dirpath}/{filename}"

    def get_files(self):
        return self.files

    async def save_file(self, file, audio_name):
        await file.save(f"{self.dirpath}/{audio_name}")
        self.files.append(audio_name)
