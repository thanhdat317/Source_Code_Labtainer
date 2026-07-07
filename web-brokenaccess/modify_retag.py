f = '/home/student/labtainer/trunk/distrib/retag_all.py'
data = open(f).read()
data = data.replace("registry = 'mfthomps'", "registry = 'thanhdat317'")
data = data.replace("base_id = VersionInfo.getImageId(image_base)", "base_id = VersionInfo.getImageId(image_base, True)")
data = data.replace("image_base = VersionInfo.getFrom(dfile_path, registry)", "image_base = VersionInfo.getFrom(dfile_path, 'labtainers')")
open(f, 'w').write(data)
print("Updated retag_all.py successfully!")
